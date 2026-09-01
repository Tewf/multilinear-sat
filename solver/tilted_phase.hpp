// The seed of one run when it is the tilted loop: `steps` rounds of draw, anneal, update over
// the whole batch (groups of batch / tilted_groups slots sharing one theta), the certificate
// check on every annealed sample and on every solution a chain passed through; then a fresh
// draw from the final q_theta, left in the slots as the walk's start.
#pragma once
#include <chrono>

#include "run_state.hpp"
#include "tilted_state.hpp"

namespace multilinear_sat {

inline void record_annealed_samples(RunState& state, const TiltedState& tilted) {
    for (int slot = 0; slot < state.configuration.batch_size && !state.stop; ++slot) {
        if (tilted.found[slot]) state.record_best(0, state.backend.saved_assignment(slot));
    }
    if (state.stop) return;
    const int best = state.best_slot();
    if (state.violated[best] <= state.result.best_violated) state.record_best(state.violated[best], state.backend.walk_assignment(best));
}

inline void run_tilted_seed_phase(RunState& state, int64_t steps) {
    const SolverConfiguration& configuration = state.configuration;
    const TiltedParameters& parameters = configuration.tilted;
    const auto phase_start = std::chrono::steady_clock::now();
    const int slots_per_group = configuration.batch_size / parameters.tilted_groups;
    const int rungs = std::max(1, static_cast<int>(std::lround(parameters.tilted_rungs_per_variable * state.formula.variable_count)));
    TiltedState tilted(parameters.tilted_groups, slots_per_group, state.formula.variable_count);
    for (int group = 0; group < tilted.groups; ++group) tilted.initialise_group(group, parameters, configuration.seed, ++state.epoch);
    for (int64_t step = 0; step < steps && !state.stop; ++step) {
        const uint64_t epoch = ++state.epoch;
        state.backend.draw_tilted(tilted.theta, slots_per_group, epoch);
        state.backend.anneal(tilted.theta, tilted.beta, slots_per_group, rungs, parameters.tilted_skc_rungs,
                             configuration.walk.walk_noise, epoch, tilted.log_weights, state.violated, tilted.found);
        record_annealed_samples(state, tilted);
        state.check_limits();
        if (state.stop) break;
        state.backend.walk_assignments(tilted.assignments);
        for (int group = 0; group < tilted.groups; ++group) tilted.update_group(group, parameters);
        tilted.advance(parameters, configuration.seed, ++state.epoch);
    }
    state.result.restarts += tilted.restarts;
    if (!state.stop) state.backend.draw_tilted(tilted.theta, slots_per_group, ++state.epoch);
    state.result.seed_seconds += std::chrono::duration<double>(std::chrono::steady_clock::now() - phase_start).count();
}

}  // namespace multilinear_sat
