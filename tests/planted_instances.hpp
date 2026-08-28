// Test instances with a known satisfying assignment: every clause is drawn at random
// and kept only if the planted assignment satisfies it, so the instance is satisfiable
// by construction. Deterministic from the seed.
#pragma once
#include <cstdint>
#include <vector>

#include "formula.hpp"

namespace multilinear_sat::testing {

struct Planted {
    Formula formula;
    std::vector<int8_t> assignment;
};

inline uint64_t next_random(uint64_t& state) {
    state = state * 6364136223846793005ull + 1442695040888963407ull;
    return state >> 33;
}

inline Planted planted_3sat(int variable_count, double ratio, uint64_t seed) {
    uint64_t state = seed * 7919 + 17;
    std::vector<int8_t> assignment(variable_count);
    for (int v = 0; v < variable_count; ++v) assignment[v] = (next_random(state) & 1) ? 1 : -1;
    const int clause_count = static_cast<int>(ratio * variable_count + 0.5);
    std::vector<std::vector<int32_t>> clauses;
    while (static_cast<int>(clauses.size()) < clause_count) {
        std::vector<int32_t> clause;
        while (clause.size() < 3) {
            const int v = static_cast<int>(next_random(state) % variable_count);
            bool fresh = true;
            for (int32_t l : clause) fresh &= (l != v + 1 && l != -(v + 1));
            if (fresh) clause.push_back((next_random(state) & 1) ? v + 1 : -(v + 1));
        }
        bool satisfied = false;
        for (int32_t l : clause) satisfied |= (l > 0) ? (assignment[l - 1] > 0) : (assignment[-l - 1] < 0);
        if (satisfied) clauses.push_back(clause);
    }
    return {make_formula(variable_count, clauses), assignment};
}

}  // namespace multilinear_sat::testing
