// The polish of one run: every heuristic slot walks from its seed for the run's flip
// budget, every rigorous slot from a uniform start with Schoening's rule for 3n flips, in
// launches of walk_flips_per_launch with the certificate check between them; a completed
// polish then counts its outcomes for the per-restart measurement and the posteriors.
#pragma once
#include <algorithm>
#include <chrono>

#include "run_state.hpp"

namespace multilinear_sat {

constexpr int schoening_flips_per_variable = 3;   // the walk length of Schoening's algorithm, part of its bound

inline std::vector<WalkSlotPlan> walk_plan(const RunState& state, int64_t polish_flips) {
    const SolverConfiguration& configuration = state.configuration;
    const int32_t heuristic_budget = static_cast<int32_t>(std::min<int64_t>(polish_flips, INT32_MAX));
    const int32_t rigorous_budget = schoening_flips_per_variable * state.formula.variable_count;
    std::vector<WalkSlotPlan> plan(configuration.batch_size);
    for (int slot = 0; slot < configuration.batch_size; ++slot) {
        if (state.heuristic(slot)) {
            plan[slot] = {static_cast<uint8_t>(configuration.seed_kind), static_cast<uint8_t>(configuration.walk.walk_rule), heuristic_budget};
        } else {
            plan[slot] = {static_cast<uint8_t>(SeedKind::Uniform), static_cast<uint8_t>(WalkRule::Schoening), rigorous_budget};
        }
    }
    return plan;
}

inline void count_polish_outcomes(RunState& state, int64_t polish_flips) {
    for (int slot = 0; slot < state.configuration.batch_size; ++slot) {
        const bool failed = state.violated[slot] > 0;
        if (!state.heuristic(slot)) state.result.rigorous_failures += failed;
        else if (polish_flips > 0) {
            state.result.heuristic_failures += failed;
            state.result.polish_successes += !failed;
        }
    }
}

inline void run_polish_phase(RunState& state, int64_t polish_flips) {
    if (state.stop || (polish_flips <= 0 && state.rigorous_slots == 0)) return;
    const auto phase_start = std::chrono::steady_clock::now();
    const std::vector<WalkSlotPlan> plan = walk_plan(state, polish_flips);
    const WalkParameters& walk = state.configuration.walk;
    state.backend.begin_walk(plan, walk, state.epoch);
    int32_t longest = 0;
    for (const WalkSlotPlan& slot : plan) longest = std::max(longest, slot.budget);
    const int64_t launches = (longest + walk.walk_flips_per_launch - 1) / walk.walk_flips_per_launch;
    bool completed = true;
    for (int64_t launch = 0; launch < launches; ++launch) {
        state.backend.walk(walk, state.violated);
        const int best = state.best_slot();
        if (state.violated[best] <= state.result.best_violated) state.record_best(state.violated[best], state.backend.walk_assignment(best));
        state.check_limits();
        if (state.stop) { completed = launch + 1 == launches; break; }
    }
    state.backend.walk_flips_done(state.flips_done);
    for (int32_t flips : state.flips_done) state.result.flips += flips;
    if (completed) count_polish_outcomes(state, polish_flips);
    state.result.polish_seconds += std::chrono::duration<double>(std::chrono::steady_clock::now() - phase_start).count();
}

}  // namespace multilinear_sat
