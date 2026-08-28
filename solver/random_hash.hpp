// Counter-based random numbers: a value is a pure function of (seed, epoch, slot,
// coordinate), so a run is reproducible from its seed on any backend and no random
// state has to live on the device. splitmix64 finaliser, then Box-Muller.
#pragma once
#include <cstdint>
#include <cmath>

#include "energy_math.hpp"

namespace multilinear_sat {

MULTILINEAR_SAT_INLINE uint64_t hash_mix(uint64_t z) {
    z += 0x9e3779b97f4a7c15ull;
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ull;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebull;
    return z ^ (z >> 31);
}

MULTILINEAR_SAT_INLINE uint64_t hash_combine(uint64_t seed, uint64_t epoch, uint64_t slot, uint64_t coordinate) {
    return hash_mix(hash_mix(hash_mix(seed ^ epoch) ^ slot) ^ coordinate);
}

// Uniform in [0, 1) from the top 24 bits, exact in float.
MULTILINEAR_SAT_INLINE float uniform_from_hash(uint64_t hash) {
    return static_cast<float>(hash >> 40) * (1.0f / 16777216.0f);
}

MULTILINEAR_SAT_INLINE float uniform_random(uint64_t seed, uint64_t epoch, uint64_t slot, uint64_t coordinate) {
    return uniform_from_hash(hash_combine(seed, epoch, slot, coordinate));
}

// Standard normal from two independent uniforms (Box-Muller, one output kept).
MULTILINEAR_SAT_INLINE float gaussian_random(uint64_t seed, uint64_t epoch, uint64_t slot, uint64_t coordinate) {
    const uint64_t first = hash_combine(seed, epoch, slot, coordinate);
    const float u1 = uniform_from_hash(first) + 1e-7f;
    const float u2 = uniform_from_hash(hash_mix(first));
    return sqrtf(-2.0f * logf(u1)) * cosf(6.2831853f * u2);
}

}  // namespace multilinear_sat
