// Test instances with a known satisfying assignment: every row is drawn at random and
// kept only if the planted assignment satisfies it, so the instance is satisfiable by
// construction. Deterministic from the seed. planted_3sat draws clauses; planted_xnf adds
// odd parities of a given length, each with the sign of one literal flipped when the
// planted assignment would falsify it.
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

inline std::vector<int32_t> random_row(uint64_t& state, int variable_count, int length) {
    std::vector<int32_t> row;
    while (static_cast<int>(row.size()) < length) {
        const int v = static_cast<int>(next_random(state) % variable_count);
        bool fresh = true;
        for (int32_t l : row) fresh &= (l != v + 1 && l != -(v + 1));
        if (fresh) row.push_back((next_random(state) & 1) ? v + 1 : -(v + 1));
    }
    return row;
}

inline bool literal_holds(int32_t literal, const std::vector<int8_t>& assignment) {
    return (literal > 0) ? (assignment[literal - 1] > 0) : (assignment[-literal - 1] < 0);
}

inline std::vector<int8_t> random_assignment(uint64_t& state, int variable_count) {
    std::vector<int8_t> assignment(variable_count);
    for (int v = 0; v < variable_count; ++v) assignment[v] = (next_random(state) & 1) ? 1 : -1;
    return assignment;
}

inline std::vector<std::vector<int32_t>> planted_clauses(uint64_t& state, const std::vector<int8_t>& assignment, int clause_count) {
    std::vector<std::vector<int32_t>> clauses;
    while (static_cast<int>(clauses.size()) < clause_count) {
        std::vector<int32_t> clause = random_row(state, static_cast<int>(assignment.size()), 3);
        bool satisfied = false;
        for (int32_t l : clause) satisfied |= literal_holds(l, assignment);
        if (satisfied) clauses.push_back(clause);
    }
    return clauses;
}

inline Planted planted_3sat(int variable_count, double ratio, uint64_t seed) {
    uint64_t state = seed * 7919 + 17;
    std::vector<int8_t> assignment = random_assignment(state, variable_count);
    const int clause_count = static_cast<int>(ratio * variable_count + 0.5);
    return {make_formula(variable_count, planted_clauses(state, assignment, clause_count)), assignment};
}

inline Planted planted_xnf(int variable_count, double clause_ratio, int parity_count, int parity_length, uint64_t seed) {
    uint64_t state = seed * 104729 + 31;
    std::vector<int8_t> assignment = random_assignment(state, variable_count);
    const int clause_count = static_cast<int>(clause_ratio * variable_count + 0.5);
    std::vector<std::vector<int32_t>> clauses = planted_clauses(state, assignment, clause_count), parities;
    while (static_cast<int>(parities.size()) < parity_count) {
        std::vector<int32_t> parity = random_row(state, variable_count, parity_length);
        int true_literals = 0;
        for (int32_t l : parity) true_literals += literal_holds(l, assignment);
        if (true_literals % 2 == 0) parity[0] = -parity[0];
        parities.push_back(parity);
    }
    return {make_formula(variable_count, clauses, parities), assignment};
}

}  // namespace multilinear_sat::testing
