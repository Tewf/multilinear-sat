// The host side of the tilted seed: one natural parameter vector theta and one inverse
// temperature per group of slots, the group's Luby budget in steps, and the update of a
// group from its annealed samples: self-normalised weights, their effective sample size, the
// gradient E_tilted[x] - p estimated as the weighted mean of the samples minus p, a plain
// step theta += eta_t g with eta_t = eta_0 / (1 + t / half_life) (the cross-entropy iteration
// collapses under a constant step: Costa, Jones, Kroese 2007), then beta raised by its factor
// while the effective sample size stays above the floor. No control variate: the Python
// record measured it adding noise at every beta.
#pragma once
#include <cmath>
#include <vector>

#include "configuration.hpp"
#include "luby.hpp"
#include "random_hash.hpp"

namespace multilinear_sat {

constexpr uint64_t tilted_epoch_mark = 0x54494c54ull;   // "TILT": the restart-stream epoch of a group's theta

struct TiltedState {
    int groups = 0, slots_per_group = 0, variable_count = 0;
    std::vector<float> theta;          // groups x variables
    std::vector<float> beta;           // groups
    std::vector<int64_t> steps_in_restart, sequence_index;   // Luby per group, groups staggered by one position
    std::vector<float> log_weights;    // slots
    std::vector<uint8_t> assignments;  // slots x variables, the annealed samples
    std::vector<uint8_t> found;        // slots
    std::vector<float> weights;        // scratch: one group's normalised weights
    int64_t restarts = 0;

    TiltedState(int groups_, int slots_per_group_, int variable_count_)
        : groups(groups_), slots_per_group(slots_per_group_), variable_count(variable_count_),
          theta(static_cast<size_t>(groups) * variable_count, 0.0f), beta(groups, 0.0f), steps_in_restart(groups, 0),
          sequence_index(groups, 0), log_weights(static_cast<size_t>(groups) * slots_per_group, 0.0f),
          assignments(static_cast<size_t>(groups) * slots_per_group * variable_count, 0), found(static_cast<size_t>(groups) * slots_per_group, 0),
          weights(slots_per_group, 0.0f) {}

    float* group_theta(int group) { return theta.data() + static_cast<size_t>(group) * variable_count; }

    void initialise_group(int group, const TiltedParameters& tilted, uint64_t seed, uint64_t epoch) {
        float* group_parameters = group_theta(group);
        for (int v = 0; v < variable_count; ++v) {
            group_parameters[v] = (2.0f * uniform_random(seed, epoch ^ tilted_epoch_mark, static_cast<uint64_t>(group), static_cast<uint64_t>(v)) - 1.0f) * tilted.tilted_init_scale;
        }
        beta[group] = tilted.beta_initial;
        steps_in_restart[group] = 0;
        sequence_index[group] = 1 + group;
    }

    // (weights normalised in place, the effective sample size) of one group's log weights.
    float normalise_weights(int group) {
        const float* logs = log_weights.data() + static_cast<size_t>(group) * slots_per_group;
        float largest = logs[0];
        for (int s = 1; s < slots_per_group; ++s) largest = std::max(largest, logs[s]);
        double total = 0.0, squares = 0.0;
        for (int s = 0; s < slots_per_group; ++s) { weights[s] = std::exp(logs[s] - largest); total += weights[s]; }
        for (int s = 0; s < slots_per_group; ++s) { weights[s] = static_cast<float>(weights[s] / total); squares += static_cast<double>(weights[s]) * weights[s]; }
        return static_cast<float>(1.0 / squares);
    }

    // The step on theta from the annealed samples, then the beta schedule; returns the ESS.
    float update_group(int group, const TiltedParameters& tilted) {
        const float effective_sample_size = normalise_weights(group);
        const float rate = tilted.tilted_learning_rate / (1.0f + static_cast<float>(steps_in_restart[group]) / tilted.tilted_learning_rate_half_life);
        float* group_parameters = group_theta(group);
        for (int v = 0; v < variable_count; ++v) {
            float weighted_mean = 0.0f;
            for (int s = 0; s < slots_per_group; ++s) {
                const size_t slot = static_cast<size_t>(group) * slots_per_group + s;
                weighted_mean += weights[s] * (assignments[slot * variable_count + v] ? 1.0f : -1.0f);
            }
            group_parameters[v] += rate * (weighted_mean - std::tanh(group_parameters[v]));
        }
        if (effective_sample_size >= tilted.ess_floor_fraction * static_cast<float>(slots_per_group)) {
            beta[group] = std::min(beta[group] * tilted.beta_growth_factor, tilted.beta_max);
        }
        return effective_sample_size;
    }

    // One step counted for every group; groups whose Luby budget is spent are reinitialised.
    void advance(const TiltedParameters& tilted, uint64_t seed, uint64_t epoch) {
        for (int group = 0; group < groups; ++group) {
            if (++steps_in_restart[group] >= luby(sequence_index[group]) * tilted.tilted_luby_unit_steps) {
                const int64_t next = sequence_index[group] + 1;
                initialise_group(group, tilted, seed, epoch);
                sequence_index[group] = next;
                ++restarts;
            }
        }
    }
};

}  // namespace multilinear_sat
