// The four variable-choice rules of the walk and one step of it on one slot, shared by
// the CPU loops and the CUDA kernels. Every rule but Metropolis first draws a violated
// row uniformly, then a variable of it:
//   skc         WalkSAT/SKC (Selman, Kautz, Cohen 1994): a zero-break variable if any, else
//               with probability walk_noise a uniform one, else the first minimum break;
//   probsat     Balint and Schoning (SAT 2012): a variable with probability proportional to
//               (eps + break)^-cb, the polynomial break distribution, no make counts;
//   schoening   Schoning (FOCS 1999): a uniform variable of the row;
//   metropolis  a uniform variable of the whole formula, accepted with probability
//               min(1, exp(beta (make - break))): a symmetric proposal, so the chain has
//               exp(beta S) as its stationary law, which is what the annealed weights need;
//   xnf         xnfSAT (Nawrocki, Liu, Frohlich, Heule, Biere, SAT 2021): a variable with
//               score cb^-wb, wb the break count weighted per row kind (binary clause,
//               longer clause, parity), as the product of three integer tables.
// The real-valued weights and acceptance probabilities are integer tables built on the
// host (walk_tables.hpp), so the two backends draw the same variable from the same hash.
#pragma once
#include <cstdint>

#include "configuration.hpp"
#include "walk_bookkeeping.hpp"

namespace multilinear_sat {

struct WalkTables {
    const uint32_t* probsat_weight;           // indexed by break count
    const uint32_t* metropolis_threshold;     // indexed by the loss break - make, when positive
    const uint32_t* xnf_binary_clause_weight; // indexed by the kind's break count; the product
    const uint32_t* xnf_clause_weight;        // of the three entries is xnf's score
    const uint32_t* xnf_parity_weight;
};

MULTILINEAR_SAT_INLINE int choose_skc(const WalkFormula& formula, const WalkSlot& slot, const int32_t* row_literals, int length,
                                      float noise, uint64_t hash_noise, uint64_t hash_index) {
    int best = 0, best_break = 1 << 30;
    for (int i = 0; i < length; ++i) {
        const int breaks = break_count(formula, slot, variable_of(row_literals[i]));
        if (breaks < best_break) { best_break = breaks; best = i; }
    }
    if (best_break > 0 && uniform_from_hash(hash_noise) < noise) return static_cast<int>(hash_index % static_cast<uint64_t>(length));
    return best;
}

MULTILINEAR_SAT_INLINE int choose_probsat(const WalkFormula& formula, const WalkSlot& slot, const int32_t* row_literals, int length,
                                          const uint32_t* weight, uint64_t hash) {
    uint64_t total = 0;
    for (int i = 0; i < length; ++i) total += weight[break_count(formula, slot, variable_of(row_literals[i]))];
    uint64_t remaining = hash % total;
    for (int i = 0; i < length; ++i) {
        const uint64_t w = weight[break_count(formula, slot, variable_of(row_literals[i]))];
        if (remaining < w) return i;
        remaining -= w;
    }
    return length - 1;
}

MULTILINEAR_SAT_INLINE uint64_t xnf_weight_of(const WalkFormula& formula, const WalkSlot& slot, const WalkTables& tables, int variable) {
    int binary_clauses, longer_clauses, parities;
    split_break_count(formula, slot, variable, binary_clauses, longer_clauses, parities);
    return static_cast<uint64_t>(tables.xnf_binary_clause_weight[binary_clauses]) *
           tables.xnf_clause_weight[longer_clauses] * tables.xnf_parity_weight[parities];
}

MULTILINEAR_SAT_INLINE int choose_xnf(const WalkFormula& formula, const WalkSlot& slot, const int32_t* row_literals, int length,
                                      const WalkTables& tables, uint64_t hash) {
    uint64_t total = 0;
    for (int i = 0; i < length; ++i) total += xnf_weight_of(formula, slot, tables, variable_of(row_literals[i]));
    uint64_t remaining = hash % total;
    for (int i = 0; i < length; ++i) {
        const uint64_t w = xnf_weight_of(formula, slot, tables, variable_of(row_literals[i]));
        if (remaining < w) return i;
        remaining -= w;
    }
    return length - 1;
}

// The proposed variable, or -1 when the proposal is rejected.
MULTILINEAR_SAT_INLINE int propose_metropolis(const WalkFormula& formula, const WalkSlot& slot, const uint32_t* threshold,
                                              uint64_t hash_variable, uint64_t hash_accept) {
    const int variable = static_cast<int>(hash_variable % static_cast<uint64_t>(formula.variable_count));
    int make = 0, breaks = 0;
    flip_effect(formula, slot, variable, make, breaks);
    const int loss = breaks - make;
    if (loss <= 0 || static_cast<uint32_t>(hash_accept >> 32) < threshold[loss]) return variable;
    return -1;
}

// One step: returns whether a variable was flipped (a rejected Metropolis proposal is a
// step that flips nothing).
MULTILINEAR_SAT_INLINE bool walk_one_step(const WalkFormula& formula, WalkSlot& slot, const WalkTables& tables, WalkRule rule,
                                          float noise, uint64_t seed, uint64_t epoch, int slot_index, int64_t step) {
    const uint64_t hash_0 = walk_hash(seed, epoch, static_cast<uint64_t>(slot_index), step, 0);
    const uint64_t hash_1 = walk_hash(seed, epoch, static_cast<uint64_t>(slot_index), step, 1);
    int variable;
    if (rule == WalkRule::Metropolis) {
        variable = propose_metropolis(formula, slot, tables.metropolis_threshold, hash_0, hash_1);
        if (variable < 0) return false;
    } else {
        const int row = slot.violated_list[hash_0 % static_cast<uint64_t>(*slot.violated_count)];
        const int32_t* row_literals = formula.literals + formula.clause_offsets[row];
        const int length = formula.clause_offsets[row + 1] - formula.clause_offsets[row];
        int index;
        if (rule == WalkRule::Schoening) index = static_cast<int>(hash_1 % static_cast<uint64_t>(length));
        else if (rule == WalkRule::ProbSat) index = choose_probsat(formula, slot, row_literals, length, tables.probsat_weight, hash_1);
        else if (rule == WalkRule::Xnf) index = choose_xnf(formula, slot, row_literals, length, tables, hash_1);
        else index = choose_skc(formula, slot, row_literals, length, noise, hash_1, walk_hash(seed, epoch, static_cast<uint64_t>(slot_index), step, 2));
        variable = variable_of(row_literals[index]);
    }
    flip_variable(formula, slot, variable);
    return true;
}

// A launch's worth of steps on one slot: up to flips_per_launch, stopping at the slot's
// budget or as soon as no row is violated.
MULTILINEAR_SAT_INLINE void walk_slot(const WalkFormula& formula, WalkSlot slot, const WalkTables& tables, const WalkSlotPlan& plan,
                                      float noise, int flips_per_launch, uint64_t seed, uint64_t epoch, int slot_index, int32_t& flips_done) {
    int32_t done = flips_done;
    for (int i = 0; i < flips_per_launch && done < plan.budget && *slot.violated_count > 0; ++i, ++done) {
        walk_one_step(formula, slot, tables, static_cast<WalkRule>(plan.rule), noise, seed, epoch, slot_index, done);
    }
    flips_done = done;
}

}  // namespace multilinear_sat
