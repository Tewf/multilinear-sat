// The error check, allocation and grid-size helpers the two CUDA source files share.
#pragma once
#include <cuda_runtime.h>

#include <stdexcept>
#include <string>
#include <vector>

namespace multilinear_sat {

inline void check(cudaError_t error, const char* what) {
    if (error != cudaSuccess) throw std::runtime_error(std::string(what) + ": " + cudaGetErrorString(error));
}

inline void* allocate(size_t bytes, const char* what) {
    void* device = nullptr;
    check(cudaMalloc(&device, bytes == 0 ? 1 : bytes), what);   // a zero-byte buffer is legal here, not in cudaMalloc
    return device;
}

template <typename T>
T* upload(const std::vector<T>& host, const char* what) {
    T* device = static_cast<T*>(allocate(host.size() * sizeof(T), what));
    check(cudaMemcpy(device, host.data(), host.size() * sizeof(T), cudaMemcpyHostToDevice), what);
    return device;
}

template <typename T>
void upload_into(T* device, const std::vector<T>& host, const char* what) {
    check(cudaMemcpy(device, host.data(), host.size() * sizeof(T), cudaMemcpyHostToDevice), what);
}

template <typename T>
void download_into(std::vector<T>& host, const T* device, size_t count, const char* what) {
    host.resize(count);
    if (count > 0) check(cudaMemcpy(host.data(), device, count * sizeof(T), cudaMemcpyDeviceToHost), what);
}

inline unsigned blocks_for(long long work, int block_size) { return static_cast<unsigned>((work + block_size - 1) / block_size); }

}  // namespace multilinear_sat
