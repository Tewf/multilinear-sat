// The two per-element operations of one gradient iteration, shared by the CPU loops and
// the CUDA kernels: mark a row as violated by the rounded point, and update one
// variable of one slot (gradient over its occurrences, focused kick, momentum, clip).
#pragma once
#include <cmath>
#include <cstdint>

#include "configuration.hpp"
#include "energy_math.hpp"
#include "random_hash.hpp"

namespace multilinear_sat {

// The kick's standard deviation at a given iteration (decay applied per iteration).
inline float kick_sigma_at(const StepParameters& step, int64_t iteration) {
    return step.kick_sigma * powf(step.kick_decay, static_cast<float>(iteration));
}

MULTILINEAR_SAT_INLINE uint8_t mark_clause_violated(const int32_t* literals, const int32_t* clause_offsets,
                                                    const uint8_t* clause_is_parity, int clause, const float* point) {
    const int begin = clause_offsets[clause];
    return row_violated_by_rounding(clause_is_parity[clause] != 0, literals + begin, clause_offsets[clause + 1] - begin, point) ? 1 : 0;
}

MULTILINEAR_SAT_INLINE void update_variable(const int32_t* literals, const int32_t* clause_offsets, const uint8_t* clause_is_parity,
                                            const int32_t* occurrence_offsets, const int32_t* occurrence_clauses,
                                            const int32_t* occurrence_positions, const uint8_t* clause_violated,
                                            const float* point, float* next_point, float* velocity, int variable,
                                            const StepParameters& step, float sigma, uint64_t seed, uint64_t epoch,
                                            int slot) {
    float gradient = 0.0f;
    bool in_violated_clause = false;
    for (int o = occurrence_offsets[variable]; o < occurrence_offsets[variable + 1]; ++o) {
        const int clause = occurrence_clauses[o];
        const int begin = clause_offsets[clause];
        gradient += row_gradient_at(clause_is_parity[clause] != 0, literals + begin, clause_offsets[clause + 1] - begin, point, occurrence_positions[o]);
        in_violated_clause |= (clause_violated[clause] != 0);
    }
    float kick = 0.0f;
    if (sigma > 0.0f && (!step.focused_kick || in_violated_clause)) {
        kick = sigma * gaussian_random(seed, epoch, static_cast<uint64_t>(slot), static_cast<uint64_t>(variable));
    }
    const float new_velocity = step.momentum * velocity[variable] - step.step_size * gradient;
    float value = point[variable] + new_velocity + kick;
    value = value > 1.0f ? 1.0f : (value < -1.0f ? -1.0f : value);
    velocity[variable] = new_velocity;
    next_point[variable] = value;
}

}  // namespace multilinear_sat
