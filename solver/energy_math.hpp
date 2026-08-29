// The multilinear (Fourier) energies and their gradients, as inline functions compiled
// for both the CPU backend and the CUDA kernels.
//
// A point x lives in [-1, 1]^n with +1 meaning true. The literal value of a signed
// literal l is sign(l) * x_{|l|}. A clause of length k has energy
//     E_c(x) = -1 + 2^{1-k} * prod_{i in c} (1 - l_i),
// which is +1 at a vertex that falsifies the clause, -1 at a vertex that satisfies it,
// and in between equals the expectation under independent rounding. The gradient with
// respect to x_v, for the occurrence of v at position i, is
//     dE_c/dx_v = -sign(l_i) * 2^{1-k} * prod_{j != i} (1 - l_j).
// An odd parity over k literals is one Walsh monomial,
//     E_x(x) = (-1)^k * prod_{i in x} l_i,
// again +1 where it is falsified (an even number of true literals), -1 where satisfied,
// and the expectation in between; its gradient is the product without one factor
// (FastFourierSAT, Cen, Zhang, Fong, AAAI 2025, Corollary 2: O(k), no transform).
#pragma once
#include <cstdint>

#include "device_inline.hpp"

namespace multilinear_sat {

MULTILINEAR_SAT_INLINE int variable_of(int32_t literal) { return (literal > 0 ? literal : -literal) - 1; }
MULTILINEAR_SAT_INLINE float sign_of(int32_t literal) { return literal > 0 ? 1.0f : -1.0f; }

// The one rounding rule: a coordinate rounds to true iff it is non-negative. Counting
// violated rows and building the certificate must use the same rule.
MULTILINEAR_SAT_INLINE bool rounds_true(float coordinate) { return coordinate >= 0.0f; }

MULTILINEAR_SAT_INLINE float literal_value(int32_t literal, const float* point) {
    return sign_of(literal) * point[variable_of(literal)];
}

MULTILINEAR_SAT_INLINE bool literal_true_by_rounding(int32_t literal, const float* point) {
    const bool variable_true = rounds_true(point[variable_of(literal)]);
    return (literal > 0) ? variable_true : !variable_true;
}

// 2^{1-k} without a pow call; clause lengths are small integers.
MULTILINEAR_SAT_INLINE float length_prefactor(int length) {
    float factor = 1.0f;
    for (int i = 1; i < length; ++i) factor *= 0.5f;
    return factor;
}

// prod_{j != skip} (1 - l_j) over the row's literals; skip = -1 skips nothing.
MULTILINEAR_SAT_INLINE float clause_product(const int32_t* literals, int length, const float* point, int skip) {
    float product = 1.0f;
    for (int j = 0; j < length; ++j) {
        if (j != skip) product *= (1.0f - literal_value(literals[j], point));
    }
    return product;
}

// prod_{j != skip} l_j, the parity's monomial without one factor.
MULTILINEAR_SAT_INLINE float literal_product(const int32_t* literals, int length, const float* point, int skip) {
    float product = 1.0f;
    for (int j = 0; j < length; ++j) {
        if (j != skip) product *= literal_value(literals[j], point);
    }
    return product;
}

MULTILINEAR_SAT_INLINE float parity_sign(int length) { return (length & 1) ? -1.0f : 1.0f; }

MULTILINEAR_SAT_INLINE float clause_energy(const int32_t* literals, int length, const float* point) {
    return -1.0f + length_prefactor(length) * clause_product(literals, length, point, -1);
}

MULTILINEAR_SAT_INLINE float parity_energy(const int32_t* literals, int length, const float* point) {
    return parity_sign(length) * literal_product(literals, length, point, -1);
}

// Whether the vertex nearest to the point (sign rounding, ties to true) falsifies the row.
MULTILINEAR_SAT_INLINE bool clause_violated_by_rounding(const int32_t* literals, int length, const float* point) {
    for (int j = 0; j < length; ++j) {
        if (literal_true_by_rounding(literals[j], point)) return false;
    }
    return true;
}

MULTILINEAR_SAT_INLINE bool parity_violated_by_rounding(const int32_t* literals, int length, const float* point) {
    int true_literals = 0;
    for (int j = 0; j < length; ++j) true_literals += literal_true_by_rounding(literals[j], point);
    return (true_literals & 1) == 0;
}

MULTILINEAR_SAT_INLINE float clause_gradient_at(const int32_t* literals, int length, const float* point, int position) {
    return -sign_of(literals[position]) * length_prefactor(length) * clause_product(literals, length, point, position);
}

MULTILINEAR_SAT_INLINE float parity_gradient_at(const int32_t* literals, int length, const float* point, int position) {
    return parity_sign(length) * sign_of(literals[position]) * literal_product(literals, length, point, position);
}

// The three operations of a row of either kind.
MULTILINEAR_SAT_INLINE float row_energy(bool is_parity, const int32_t* literals, int length, const float* point) {
    return is_parity ? parity_energy(literals, length, point) : clause_energy(literals, length, point);
}

MULTILINEAR_SAT_INLINE bool row_violated_by_rounding(bool is_parity, const int32_t* literals, int length, const float* point) {
    return is_parity ? parity_violated_by_rounding(literals, length, point) : clause_violated_by_rounding(literals, length, point);
}

MULTILINEAR_SAT_INLINE float row_gradient_at(bool is_parity, const int32_t* literals, int length, const float* point, int position) {
    return is_parity ? parity_gradient_at(literals, length, point, position) : clause_gradient_at(literals, length, point, position);
}

}  // namespace multilinear_sat
