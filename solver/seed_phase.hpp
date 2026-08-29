// The seed of one run when it is the ascent: gradient iterations of the whole batch, each
// with the certificate check on the best rounded point and the stall resampling.
#pragma once
#include <chrono>

#include "run_state.hpp"

namespace multilinear_sat {

inline void resample_stalled_slots(RunState& state) {
    const int patience = state.configuration.stall_patience;
    if (patience <= 0) return;
    std::vector<int> stalled;
    for (int slot = 0; slot < state.configuration.batch_size; ++slot) {
        if (state.since_improvement[slot] >= patience) {
            stalled.push_back(slot);
            state.since_improvement[slot] = 0;
            state.slot_best[slot] = state.formula.clause_count() + 1;
        }
    }
    if (stalled.empty()) return;
    state.backend.restart_slots(stalled, ++state.epoch);
    state.result.restarts += static_cast<int64_t>(stalled.size());
}

inline void run_seed_phase(RunState& state, int64_t steps) {
    if (state.configuration.seed_kind != SeedKind::Ascent) return;
    const auto phase_start = std::chrono::steady_clock::now();
    for (int64_t step = 0; step < steps && !state.stop; ++step) {
        state.backend.iterate(state.configuration.step, state.iteration, state.violated);
        state.result.iterations = ++state.iteration;
        for (int slot = 0; slot < state.configuration.batch_size; ++slot) {
            if (state.violated[slot] < state.slot_best[slot]) {
                state.slot_best[slot] = state.violated[slot];
                state.since_improvement[slot] = 0;
            } else {
                ++state.since_improvement[slot];
            }
        }
        const int best = state.best_slot();
        if (state.violated[best] <= state.result.best_violated) state.record_best(state.violated[best], state.backend.rounded_assignment(best));
        state.check_limits();
        if (!state.stop) resample_stalled_slots(state);
    }
    state.result.seed_seconds += std::chrono::duration<double>(std::chrono::steady_clock::now() - phase_start).count();
}

}  // namespace multilinear_sat
