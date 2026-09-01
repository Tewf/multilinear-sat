// The integer tables behind the walk's two real-valued rules, built once on the host and
// handed to either backend, so a CPU slot and a CUDA slot with the same hash flip the same
// variable. Both are indexed up to the largest occurrence count, which bounds every break
// count and every loss.
#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <vector>

#include "configuration.hpp"

namespace multilinear_sat {

// probsat's weight of a break count b, (eps + b)^-cb, scaled to 2^24 and at least 1 so no
// candidate is impossible.
inline std::vector<uint32_t> probsat_weight_table(int length, const WalkParameters& walk) {
    std::vector<uint32_t> table(length);
    for (int b = 0; b < length; ++b) {
        const double weight = std::pow(static_cast<double>(walk.probsat_eps) + b, -static_cast<double>(walk.probsat_cb)) * 16777216.0;
        table[b] = static_cast<uint32_t>(std::max(1.0, std::min(weight, 4294967295.0)));
    }
    return table;
}

// xnf's weight of one kind's break count b, xnf_cb^-(row_weight * b), scaled to 2^16 and at
// least 1: the product over the three row kinds is xnf_cb^-wb, the exponential score of the
// weighted break, exactly and in integers.
inline std::vector<uint32_t> xnf_weight_table(int length, float cb, float row_weight) {
    std::vector<uint32_t> table(length);
    for (int b = 0; b < length; ++b) {
        const double weight = std::pow(static_cast<double>(cb), -static_cast<double>(row_weight) * b) * 65536.0;
        table[b] = static_cast<uint32_t>(std::max(1.0, std::min(weight, 4294967295.0)));
    }
    return table;
}

// Metropolis's acceptance of a loss d, exp(-beta d), as the threshold a 32-bit uniform
// must fall under.
inline std::vector<uint32_t> metropolis_threshold_table(int length, const WalkParameters& walk) {
    std::vector<uint32_t> table(length);
    for (int d = 0; d < length; ++d) {
        const double threshold = std::floor(4294967296.0 * std::exp(-static_cast<double>(walk.metropolis_beta) * d));
        table[d] = static_cast<uint32_t>(std::min(threshold, 4294967295.0));
    }
    return table;
}

}  // namespace multilinear_sat
