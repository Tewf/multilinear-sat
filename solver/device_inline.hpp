// The one macro that lets a function compile for the CPU backend and the CUDA kernels.
#pragma once
#ifdef __CUDACC__
#define MULTILINEAR_SAT_INLINE __host__ __device__ inline
#else
#define MULTILINEAR_SAT_INLINE inline
#endif
