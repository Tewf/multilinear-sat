// The multilinear (Fourier) clause energy and its gradient, as inline functions
// compiled for both the CPU backend and the CUDA kernels.
//
// A point x lives in [-1, 1]^n with +1 meaning true. The literal value of a signed
// literal l is sign(l) * x_{|l|}. A clause of length k has energy
//     E_c(x) = -1 + 2^{1-k} * prod_{i in c} (1 - l_i),
// which is +1 at a vertex that falsifies the clause, -1 at a vertex that satisfies it,
// and in between equals the expectation under independent rounding. The gradient with
// respect to x_v, for the occurrence of v at position i, is
//     dE_c/dx_v = -sign(l_i) * 2^{1-k} * prod_{j != i} (1 - l_j).
#pragma once
#include <cstdint>

#ifdef __CUDACC__
#define MULTILINEAR_SAT_INLINE __host__ __device__ inline
#else
#define MULTILINEAR_SAT_INLINE inline
#endif

namespace multilinear_sat {

MULTILINEAR_SAT_INLINE int variable_of(int32_t literal) { return (literal > 0 ? literal : -literal) - 1; }
MULTILINEAR_SAT_INLINE float sign_of(int32_t literal) { return literal > 0 ? 1.0f : -1.0f; }

MULTILINEAR_SAT_INLINE float literal_value(int32_t literal, const float* point) {
    return sign_of(literal) * point[variable_of(literal)];
}

// 2^{1-k} without a pow call; clause lengths are small integers.
MULTILINEAR_SAT_INLINE float length_prefactor(int length) {
    float factor = 1.0f;
    for (int i = 1; i < length; ++i) factor *= 0.5f;
    return factor;
}

// prod_{j != skip} (1 - l_j) over the clause's literals; skip = -1 skips nothing.
MULTILINEAR_SAT_INLINE float clause_product(const int32_t* literals, int length, const float* point, int skip) {
    float product = 1.0f;
    for (int j = 0; j < length; ++j) {
        if (j != skip) product *= (1.0f - literal_value(literals[j], point));
    }
    return product;
}

MULTILINEAR_SAT_INLINE float clause_energy(const int32_t* literals, int length, const float* point) {
    return -1.0f + length_prefactor(length) * clause_product(literals, length, point, -1);
}

// Whether the vertex nearest to the point (sign rounding, ties to true) falsifies the clause.
MULTILINEAR_SAT_INLINE bool clause_violated_by_rounding(const int32_t* literals, int length, const float* point) {
    for (int j = 0; j < length; ++j) {
        const float value = point[variable_of(literals[j])];
        const bool variable_true = value >= 0.0f;
        const bool literal_true = (literals[j] > 0) ? variable_true : !variable_true;
        if (literal_true) return false;
    }
    return true;
}

MULTILINEAR_SAT_INLINE float clause_gradient_at(const int32_t* literals, int length, const float* point, int position) {
    return -sign_of(literals[position]) * length_prefactor(length) * clause_product(literals, length, point, position);
}

}  // namespace multilinear_sat
