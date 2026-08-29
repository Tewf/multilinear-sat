// CUDA backend, the gradient half: one thread per (slot, row) to mark violated rows and
// count them, one thread per (slot, variable) to take the step. Same inline functions as
// the CPU backend, so a run is reproducible across backends from its seed.
#include "cuda_backend.hpp"

#include "batch_kernels.hpp"
#include "cuda_helpers.cuh"

namespace multilinear_sat {

constexpr int cuda_block_size = 256;

__global__ void clause_kernel(DeviceFormula formula, const float* points, uint8_t* flags, int* counts,
                              int variable_count, int clause_count, int batch_size) {
    const long long index = blockIdx.x * (long long)blockDim.x + threadIdx.x;
    if (index >= (long long)batch_size * clause_count) return;
    const int slot = static_cast<int>(index / clause_count), clause = static_cast<int>(index % clause_count);
    const uint8_t violated = mark_clause_violated(formula.literals, formula.clause_offsets, formula.clause_is_parity, clause, points + (size_t)slot * variable_count);
    flags[index] = violated;
    if (violated) atomicAdd(&counts[slot], 1);
}

__global__ void variable_kernel(DeviceFormula formula, const uint8_t* flags, const float* points, float* next, float* velocity,
                                int variable_count, int clause_count, int batch_size, StepParameters step, float sigma,
                                uint64_t seed, uint64_t epoch) {
    const long long index = blockIdx.x * (long long)blockDim.x + threadIdx.x;
    if (index >= (long long)batch_size * variable_count) return;
    const int slot = static_cast<int>(index / variable_count), variable = static_cast<int>(index % variable_count);
    const size_t base = (size_t)slot * variable_count;
    update_variable(formula.literals, formula.clause_offsets, formula.clause_is_parity, formula.occurrence_offsets, formula.occurrence_clauses,
                    formula.occurrence_positions, flags + (size_t)slot * clause_count, points + base, next + base,
                    velocity + base, variable, step, sigma, seed, epoch, slot);
}

__global__ void restart_kernel(const int* slots, int slot_count, float* points, float* velocity, int variable_count,
                               uint64_t seed, uint64_t epoch) {
    const long long index = blockIdx.x * (long long)blockDim.x + threadIdx.x;
    if (index >= (long long)slot_count * variable_count) return;
    const int slot = slots[index / variable_count], variable = static_cast<int>(index % variable_count);
    points[(size_t)slot * variable_count + variable] = 2.0f * uniform_random(seed, epoch, slot, variable) - 1.0f;
    velocity[(size_t)slot * variable_count + variable] = 0.0f;
}

CudaBackend::~CudaBackend() { release(); }

void CudaBackend::initialise(const Formula& formula, int batch_size, uint64_t seed) {
    release();
    try {
        formula_ = &formula;
        batch_size_ = batch_size; variable_count_ = formula.variable_count; clause_count_ = formula.clause_count(); seed_ = seed;
        device_ = {upload(formula.literals, "upload literals"), upload(formula.clause_offsets, "upload clause offsets"),
                   upload(formula.occurrence_offsets, "upload occurrence offsets"),
                   upload(formula.occurrence_clauses, "upload occurrence clauses"),
                   upload(formula.occurrence_positions, "upload occurrence positions"),
                   upload(formula.occurrence_literals, "upload occurrence literals"),
                   upload(formula.clause_is_parity, "upload parity flags")};
        const size_t floats = (size_t)batch_size_ * variable_count_ * sizeof(float);
        points_ = static_cast<float*>(allocate(floats, "allocate points"));
        next_ = static_cast<float*>(allocate(floats, "allocate next points"));
        velocity_ = static_cast<float*>(allocate(floats, "allocate velocity"));
        flags_ = static_cast<uint8_t*>(allocate((size_t)batch_size_ * clause_count_, "allocate clause flags"));
        counts_ = static_cast<int*>(allocate(batch_size_ * sizeof(int), "allocate counts"));
        slots_ = static_cast<int*>(allocate(batch_size_ * sizeof(int), "allocate slots"));
        allocate_walk();
    } catch (...) {
        release();
        throw;
    }
    restart_slots(every_slot(batch_size_), 0);
}

void CudaBackend::restart_slots(const std::vector<int>& slots, uint64_t epoch) {
    const long long work = (long long)slots.size() * variable_count_;
    if (work == 0) return;
    upload_into(slots_, slots, "copy slots");
    restart_kernel<<<blocks_for(work, cuda_block_size), cuda_block_size>>>(slots_, (int)slots.size(), points_, velocity_, variable_count_, seed_, epoch);
    check(cudaGetLastError(), "restart_kernel launch");
}

void CudaBackend::iterate(const StepParameters& step, int64_t iteration, std::vector<int>& violated) {
    check(cudaMemsetAsync(counts_, 0, batch_size_ * sizeof(int)), "memset counts");
    const long long clause_work = (long long)batch_size_ * clause_count_;
    if (clause_work > 0) {
        clause_kernel<<<blocks_for(clause_work, cuda_block_size), cuda_block_size>>>(device_, points_, flags_, counts_, variable_count_, clause_count_, batch_size_);
        check(cudaGetLastError(), "clause_kernel launch");
    }
    const long long variable_work = (long long)batch_size_ * variable_count_;
    if (variable_work > 0) {
        variable_kernel<<<blocks_for(variable_work, cuda_block_size), cuda_block_size>>>(device_, flags_, points_, next_, velocity_, variable_count_,
                                                                                        clause_count_, batch_size_, step, kick_sigma_at(step, iteration),
                                                                                        seed_, (uint64_t)iteration + 1);
        check(cudaGetLastError(), "variable_kernel launch");
    }
    download_into(violated, counts_, batch_size_, "copy counts (or an earlier kernel failed)");
    std::swap(points_, next_);
}

std::vector<float> CudaBackend::point(int slot) const { return download(points_, slot); }

std::vector<int8_t> CudaBackend::rounded_assignment(int slot) const {
    // After iterate() swapped the buffers, next_ holds the point the counts were taken on.
    const std::vector<float> host = download(next_, slot);
    std::vector<int8_t> assignment(variable_count_);
    for (int variable = 0; variable < variable_count_; ++variable) assignment[variable] = rounds_true(host[variable]) ? 1 : -1;
    return assignment;
}

std::vector<float> CudaBackend::download(const float* buffer, int slot) const {
    std::vector<float> host;
    download_into(host, buffer + (size_t)slot * variable_count_, variable_count_, "copy point");
    return host;
}

void CudaBackend::release() {
    for (const void* p : {(const void*)device_.literals, (const void*)device_.clause_offsets, (const void*)device_.occurrence_offsets,
                          (const void*)device_.occurrence_clauses, (const void*)device_.occurrence_positions,
                          (const void*)device_.occurrence_literals, (const void*)device_.clause_is_parity}) cudaFree((void*)p);
    for (void* p : {(void*)points_, (void*)next_, (void*)velocity_, (void*)flags_, (void*)counts_, (void*)slots_,
                    (void*)assignment_, (void*)true_count_, (void*)violated_list_, (void*)violated_position_, (void*)violated_count_,
                    (void*)flips_done_, (void*)plan_, (void*)probsat_weight_, (void*)metropolis_threshold_,
                    (void*)theta_, (void*)beta_, (void*)log_weights_, (void*)found_, (void*)saved_}) cudaFree(p);
    device_ = {}; points_ = next_ = velocity_ = nullptr; flags_ = nullptr; counts_ = slots_ = nullptr;
    assignment_ = true_count_ = nullptr; violated_list_ = violated_position_ = violated_count_ = flips_done_ = nullptr;
    plan_ = nullptr; probsat_weight_ = metropolis_threshold_ = nullptr;
    theta_ = beta_ = log_weights_ = nullptr; found_ = saved_ = nullptr; theta_capacity_ = beta_capacity_ = 0;
}

bool cuda_available() {
    int count = 0;
    return cudaGetDeviceCount(&count) == cudaSuccess && count > 0;
}

std::unique_ptr<Backend> make_cuda_backend() {
    if (!cuda_available()) throw std::runtime_error("no CUDA device available");
    return std::make_unique<CudaBackend>();
}

}  // namespace multilinear_sat
