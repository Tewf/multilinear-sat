// CUDA backend: one thread per (slot, clause) to mark violated clauses and count
// them, one thread per (slot, variable) to take the step. Same inline functions as
// the CPU backend, so a run is reproducible across backends from its seed.
#include <cuda_runtime.h>

#include <stdexcept>
#include <string>

#include "backend.hpp"
#include "batch_kernels.hpp"

namespace multilinear_sat {

constexpr int cuda_block_size = 256;

static void check(cudaError_t error, const char* what) {
    if (error != cudaSuccess) throw std::runtime_error(std::string(what) + ": " + cudaGetErrorString(error));
}

static void* allocate(size_t bytes, const char* what) {
    void* device = nullptr;
    check(cudaMalloc(&device, bytes == 0 ? 1 : bytes), what);   // a zero-byte buffer is legal here, not in cudaMalloc
    return device;
}

template <typename T>
static T* upload(const std::vector<T>& host, const char* what) {
    T* device = static_cast<T*>(allocate(host.size() * sizeof(T), what));
    check(cudaMemcpy(device, host.data(), host.size() * sizeof(T), cudaMemcpyHostToDevice), what);
    return device;
}

static unsigned blocks_for(long long work) { return static_cast<unsigned>((work + cuda_block_size - 1) / cuda_block_size); }

struct DeviceFormula {
    const int32_t *literals, *clause_offsets, *occurrence_offsets, *occurrence_clauses, *occurrence_positions;
};

__global__ void clause_kernel(DeviceFormula formula, const float* points, uint8_t* flags, int* counts,
                              int variable_count, int clause_count, int batch_size) {
    const long long index = blockIdx.x * (long long)blockDim.x + threadIdx.x;
    if (index >= (long long)batch_size * clause_count) return;
    const int slot = static_cast<int>(index / clause_count), clause = static_cast<int>(index % clause_count);
    const uint8_t violated = mark_clause_violated(formula.literals, formula.clause_offsets, clause, points + (size_t)slot * variable_count);
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
    update_variable(formula.literals, formula.clause_offsets, formula.occurrence_offsets, formula.occurrence_clauses,
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

class CudaBackend final : public Backend {
public:
    ~CudaBackend() override { release(); }
    const char* name() const override { return "cuda"; }

    void initialise(const Formula& formula, int batch_size, uint64_t seed) override {
        release();
        try {
            batch_size_ = batch_size; variable_count_ = formula.variable_count; clause_count_ = formula.clause_count(); seed_ = seed;
            device_ = {upload(formula.literals, "upload literals"), upload(formula.clause_offsets, "upload clause offsets"),
                       upload(formula.occurrence_offsets, "upload occurrence offsets"),
                       upload(formula.occurrence_clauses, "upload occurrence clauses"),
                       upload(formula.occurrence_positions, "upload occurrence positions")};
            const size_t floats = (size_t)batch_size_ * variable_count_ * sizeof(float);
            points_ = static_cast<float*>(allocate(floats, "allocate points"));
            next_ = static_cast<float*>(allocate(floats, "allocate next points"));
            velocity_ = static_cast<float*>(allocate(floats, "allocate velocity"));
            flags_ = static_cast<uint8_t*>(allocate((size_t)batch_size_ * clause_count_, "allocate clause flags"));
            counts_ = static_cast<int*>(allocate(batch_size_ * sizeof(int), "allocate counts"));
            slots_ = static_cast<int*>(allocate(batch_size_ * sizeof(int), "allocate slots"));
        } catch (...) {
            release();
            throw;
        }
        restart_slots(every_slot(batch_size_), 0);
    }

    void restart_slots(const std::vector<int>& slots, uint64_t epoch) override {
        const long long work = (long long)slots.size() * variable_count_;
        if (work == 0) return;
        check(cudaMemcpy(slots_, slots.data(), slots.size() * sizeof(int), cudaMemcpyHostToDevice), "copy slots");
        restart_kernel<<<blocks_for(work), cuda_block_size>>>(slots_, (int)slots.size(), points_, velocity_, variable_count_, seed_, epoch);
        check(cudaGetLastError(), "restart_kernel launch");
#ifndef NDEBUG
        check(cudaDeviceSynchronize(), "restart_kernel");
#endif
    }

    void iterate(const StepParameters& step, int64_t iteration, std::vector<int>& violated) override {
        check(cudaMemsetAsync(counts_, 0, batch_size_ * sizeof(int)), "memset counts");
        const long long clause_work = (long long)batch_size_ * clause_count_;
        if (clause_work > 0) {
            clause_kernel<<<blocks_for(clause_work), cuda_block_size>>>(device_, points_, flags_, counts_, variable_count_, clause_count_, batch_size_);
            check(cudaGetLastError(), "clause_kernel launch");
        }
        const long long variable_work = (long long)batch_size_ * variable_count_;
        if (variable_work > 0) {
            variable_kernel<<<blocks_for(variable_work), cuda_block_size>>>(device_, flags_, points_, next_, velocity_, variable_count_,
                                                                          clause_count_, batch_size_, step, kick_sigma_at(step, iteration),
                                                                          seed_, (uint64_t)iteration + 1);
            check(cudaGetLastError(), "variable_kernel launch");
        }
        violated.resize(batch_size_);
        check(cudaMemcpy(violated.data(), counts_, batch_size_ * sizeof(int), cudaMemcpyDeviceToHost), "copy counts (or an earlier kernel failed)");
        std::swap(points_, next_);
    }

    std::vector<float> point(int slot) const override { return download(points_, slot); }

    std::vector<int8_t> rounded_assignment(int slot) const override {
        // After iterate() swapped the buffers, next_ holds the point the counts were taken on.
        const std::vector<float> host = download(next_, slot);
        std::vector<int8_t> assignment(variable_count_);
        for (int variable = 0; variable < variable_count_; ++variable) assignment[variable] = rounds_true(host[variable]) ? 1 : -1;
        return assignment;
    }

private:
    std::vector<float> download(const float* buffer, int slot) const {
        std::vector<float> host(variable_count_);
        if (variable_count_ > 0) {
            check(cudaMemcpy(host.data(), buffer + (size_t)slot * variable_count_, variable_count_ * sizeof(float), cudaMemcpyDeviceToHost), "copy point");
        }
        return host;
    }

    void release() {
        for (const int32_t* p : {device_.literals, device_.clause_offsets, device_.occurrence_offsets,
                                 device_.occurrence_clauses, device_.occurrence_positions}) cudaFree((void*)p);
        for (void* p : {(void*)points_, (void*)next_, (void*)velocity_, (void*)flags_, (void*)counts_, (void*)slots_}) cudaFree(p);
        device_ = {}; points_ = next_ = velocity_ = nullptr; flags_ = nullptr; counts_ = slots_ = nullptr;
    }

    DeviceFormula device_{};
    float *points_ = nullptr, *next_ = nullptr, *velocity_ = nullptr;
    uint8_t* flags_ = nullptr;
    int *counts_ = nullptr, *slots_ = nullptr;
    int batch_size_ = 0, variable_count_ = 0, clause_count_ = 0;
    uint64_t seed_ = 0;
};

bool cuda_available() {
    int count = 0;
    return cudaGetDeviceCount(&count) == cudaSuccess && count > 0;
}

std::unique_ptr<Backend> make_cuda_backend() {
    if (!cuda_available()) throw std::runtime_error("no CUDA device available");
    return std::make_unique<CudaBackend>();
}

}  // namespace multilinear_sat
