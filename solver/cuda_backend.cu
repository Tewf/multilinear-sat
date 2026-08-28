// CUDA backend: one thread per (slot, clause) to mark violated clauses and count
// them, one thread per (slot, variable) to take the step. Same inline functions as
// the CPU backend, so a run is reproducible across backends from its seed.
#include <cuda_runtime.h>

#include <stdexcept>
#include <string>

#include "backend.hpp"
#include "batch_kernels.hpp"

namespace multilinear_sat {

static void check(cudaError_t error, const char* what) {
    if (error != cudaSuccess) throw std::runtime_error(std::string(what) + ": " + cudaGetErrorString(error));
}

template <typename T>
static T* upload(const std::vector<T>& host) {
    T* device = nullptr;
    check(cudaMalloc(&device, host.size() * sizeof(T) + 1), "cudaMalloc");
    check(cudaMemcpy(device, host.data(), host.size() * sizeof(T), cudaMemcpyHostToDevice), "cudaMemcpy");
    return device;
}

struct DeviceFormula {
    const int32_t *literals, *clause_offsets, *occurrence_offsets, *occurrence_clauses, *occurrence_positions;
};

__global__ void clause_kernel(DeviceFormula f, const float* points, uint8_t* flags, int* counts, int n, int m, int batch) {
    const long long index = blockIdx.x * (long long)blockDim.x + threadIdx.x;
    if (index >= (long long)batch * m) return;
    const int slot = static_cast<int>(index / m), clause = static_cast<int>(index % m);
    const uint8_t violated = mark_clause_violated(f.literals, f.clause_offsets, clause, points + (size_t)slot * n);
    flags[index] = violated;
    if (violated) atomicAdd(&counts[slot], 1);
}

__global__ void variable_kernel(DeviceFormula f, const uint8_t* flags, const float* points, float* next, float* velocity,
                                int n, int m, int batch, StepParameters step, float sigma, uint64_t seed, uint64_t epoch) {
    const long long index = blockIdx.x * (long long)blockDim.x + threadIdx.x;
    if (index >= (long long)batch * n) return;
    const int slot = static_cast<int>(index / n), variable = static_cast<int>(index % n);
    const size_t base = (size_t)slot * n;
    update_variable(f.literals, f.clause_offsets, f.occurrence_offsets, f.occurrence_clauses, f.occurrence_positions,
                    flags + (size_t)slot * m, points + base, next + base, velocity + base, variable, step, sigma, seed,
                    epoch, slot);
}

__global__ void restart_kernel(const int* slots, int count, float* points, float* velocity, int n, uint64_t seed, uint64_t epoch) {
    const long long index = blockIdx.x * (long long)blockDim.x + threadIdx.x;
    if (index >= (long long)count * n) return;
    const int slot = slots[index / n], variable = static_cast<int>(index % n);
    points[(size_t)slot * n + variable] = 2.0f * uniform_random(seed, epoch, slot, variable) - 1.0f;
    velocity[(size_t)slot * n + variable] = 0.0f;
}

static unsigned blocks_for(long long work) { return static_cast<unsigned>((work + 255) / 256); }

class CudaBackend final : public Backend {
public:
    ~CudaBackend() override { release(); }
    const char* name() const override { return "cuda"; }

    void initialise(const Formula& formula, int batch_size, uint64_t seed) override {
        release();
        batch_ = batch_size; n_ = formula.variable_count; m_ = formula.clause_count(); seed_ = seed;
        device_ = {upload(formula.literals), upload(formula.clause_offsets), upload(formula.occurrence_offsets),
                   upload(formula.occurrence_clauses), upload(formula.occurrence_positions)};
        const size_t floats = (size_t)batch_ * n_;
        check(cudaMalloc(&points_, floats * sizeof(float)), "cudaMalloc points");
        check(cudaMalloc(&next_, floats * sizeof(float)), "cudaMalloc next");
        check(cudaMalloc(&velocity_, floats * sizeof(float)), "cudaMalloc velocity");
        check(cudaMalloc(&flags_, (size_t)batch_ * m_), "cudaMalloc flags");
        check(cudaMalloc(&counts_, batch_ * sizeof(int)), "cudaMalloc counts");
        check(cudaMalloc(&slots_, batch_ * sizeof(int)), "cudaMalloc slots");
        std::vector<int> all(batch_);
        for (int b = 0; b < batch_; ++b) all[b] = b;
        restart_slots(all, 0);
    }

    void restart_slots(const std::vector<int>& slots, uint64_t epoch) override {
        if (slots.empty()) return;
        check(cudaMemcpy(slots_, slots.data(), slots.size() * sizeof(int), cudaMemcpyHostToDevice), "copy slots");
        restart_kernel<<<blocks_for((long long)slots.size() * n_), 256>>>(slots_, (int)slots.size(), points_, velocity_, n_, seed_, epoch);
        check(cudaGetLastError(), "restart_kernel");
    }

    void iterate(const StepParameters& step, int64_t iteration, std::vector<int>& violated) override {
        check(cudaMemsetAsync(counts_, 0, batch_ * sizeof(int)), "memset counts");
        clause_kernel<<<blocks_for((long long)batch_ * m_), 256>>>(device_, points_, flags_, counts_, n_, m_, batch_);
        check(cudaGetLastError(), "clause_kernel");
        const float sigma = step.kick_sigma * powf(step.kick_decay, static_cast<float>(iteration));
        variable_kernel<<<blocks_for((long long)batch_ * n_), 256>>>(device_, flags_, points_, next_, velocity_, n_, m_, batch_,
                                                                      step, sigma, seed_, (uint64_t)iteration + 1);
        check(cudaGetLastError(), "variable_kernel");
        violated.resize(batch_);
        check(cudaMemcpy(violated.data(), counts_, batch_ * sizeof(int), cudaMemcpyDeviceToHost), "copy counts");
        std::swap(points_, next_);
    }

    std::vector<float> download(const float* buffer, int slot) const {
        std::vector<float> host(n_);
        check(cudaMemcpy(host.data(), buffer + (size_t)slot * n_, n_ * sizeof(float), cudaMemcpyDeviceToHost), "copy point");
        return host;
    }

    std::vector<float> point(int slot) const override { return download(points_, slot); }

    std::vector<int8_t> rounded_assignment(int slot) const override {
        // After iterate() swapped the buffers, next_ holds the point the counts were taken on.
        const std::vector<float> host = download(next_, slot);
        std::vector<int8_t> assignment(n_);
        for (int v = 0; v < n_; ++v) assignment[v] = host[v] >= 0.0f ? 1 : -1;
        return assignment;
    }

private:
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
    int batch_ = 0, n_ = 0, m_ = 0;
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
