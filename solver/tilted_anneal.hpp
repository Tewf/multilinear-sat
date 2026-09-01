// The tilted seed's two per-slot operations, shared by the CPU loops and the CUDA kernels
// (method/sampling-gradient-loop.md): a draw of q_theta, the
// product measure with P(x_i = true) = (1 + tanh theta_i) / 2, and the annealed-importance-
// sampling ladder (Neal 2001) toward q_theta(x) exp(beta S(x)), S the satisfied-row count.
// From the draw (exact at beta_0 = 0), rung k proposes a uniform variable of the formula
// and accepts with min(1, exp(beta k / K dS - 2 theta_i x_i)), a symmetric proposal that
// leaves q_theta exp(beta_k S) invariant; the log weight is sum_k (beta_k - beta_{k-1})
// S(x_{k-1}), so the self-normalised weighted mean of the annealed samples is a consistent
// estimate of E_tilted[x] (the Python record's Table 1). A chain that passes through a
// satisfying assignment keeps moving, since freezing it there biased the mean by 0.4 RMS;
// the assignment is saved aside so the run can end on it. The acceptance uses logf, so the
// two backends agree to float tolerance here, as they do for the gradient.
#pragma once
#include <cmath>
#include <cstdint>

#include "walk_bookkeeping.hpp"
#include "walk_rules.hpp"

namespace multilinear_sat {

MULTILINEAR_SAT_INLINE void draw_tilted_slot(const WalkFormula& formula, WalkSlot& slot, const float* theta, uint64_t seed, uint64_t epoch,
                                             int slot_index) {
    for (int v = 0; v < formula.variable_count; ++v) {
        const float probability_true = 0.5f * (1.0f + tanhf(theta[v]));
        slot.assignment[v] = uniform_random(seed, epoch, static_cast<uint64_t>(slot_index), static_cast<uint64_t>(v)) < probability_true ? 1 : 0;
    }
    recount_slot(formula, slot);
}

MULTILINEAR_SAT_INLINE float anneal_slot(const WalkFormula& formula, WalkSlot& slot, const float* theta, float beta, int rungs,
                                         bool skc_rungs, float noise,
                                         uint64_t seed, uint64_t epoch, int slot_index, uint8_t* found, uint8_t* saved) {
    float log_weight = 0.0f;
    for (int rung = 1; rung <= rungs; ++rung) {
        if (*slot.violated_count == 0 && !*found) {
            *found = 1;
            for (int v = 0; v < formula.variable_count; ++v) saved[v] = slot.assignment[v];
        }
        log_weight += beta / static_cast<float>(rungs) * static_cast<float>(formula.clause_count - *slot.violated_count);
        const uint64_t hash_variable = walk_hash(seed, epoch, static_cast<uint64_t>(slot_index), rung, 0);
        const uint64_t hash_accept = walk_hash(seed, epoch, static_cast<uint64_t>(slot_index), rung, 1);
        if (skc_rungs) {
            // The Python record's walk mode: the rung is one WalkSAT/SKC step on a violated
            // row, so the ladder generates elites while the same weights are accumulated.
            // The record measured those weights as biased, so this mode is an elite
            // generator, not an estimator. A satisfied slot stays put; `found` above has
            // already saved it.
            if (*slot.violated_count > 0) {
                const int row = slot.violated_list[hash_variable % static_cast<uint64_t>(*slot.violated_count)];
                const int32_t* row_literals = formula.literals + formula.clause_offsets[row];
                const int length = formula.clause_offsets[row + 1] - formula.clause_offsets[row];
                const int index = choose_skc(formula, slot, row_literals, length, noise, hash_accept,
                                             walk_hash(seed, epoch, static_cast<uint64_t>(slot_index), rung, 2));
                flip_variable(formula, slot, variable_of(row_literals[index]));
            }
            continue;
        }
        const int variable = static_cast<int>(hash_variable % static_cast<uint64_t>(formula.variable_count));
        int make = 0, breaks = 0;
        flip_effect(formula, slot, variable, make, breaks);
        const float x = slot.assignment[variable] ? 1.0f : -1.0f;
        const float log_acceptance = beta * static_cast<float>(rung) / static_cast<float>(rungs) * static_cast<float>(make - breaks)
                                     - 2.0f * theta[variable] * x;
        if (logf(uniform_from_hash(hash_accept) + 1e-7f) < log_acceptance) flip_variable(formula, slot, variable);
    }
    return log_weight;
}

}  // namespace multilinear_sat
