// Counter-based random numbers: a value is a pure function of (seed, stream, epoch,
// slot, coordinate), so a run is reproducible from its seed on any backend and no random
// state lives on the device. Restarts, kicks and walk steps draw from three separate
// streams, so a restart position can never repeat a kick or a flip, and the seed is
// mixed before the epoch so that (seed, epoch) pairs with the same XOR do not share a
// stream. splitmix64 finaliser, then Box-Muller for the Gaussian.
#pragma once
#include <cmath>
#include <cstdint>

#include "device_inline.hpp"

namespace multilinear_sat {

MULTILINEAR_SAT_INLINE uint64_t hash_mix(uint64_t z) {
    z += 0x9e3779b97f4a7c15ull;
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ull;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebull;
    return z ^ (z >> 31);
}

constexpr uint64_t restart_stream = 0x52455354ull;   // "REST"
constexpr uint64_t kick_stream = 0x4b49434bull;      // "KICK"
constexpr uint64_t walk_stream = 0x57414c4bull;      // "WALK"

MULTILINEAR_SAT_INLINE uint64_t hash_combine(uint64_t seed, uint64_t stream, uint64_t epoch, uint64_t slot, uint64_t coordinate) {
    return hash_mix(hash_mix(hash_mix(hash_mix(hash_mix(seed) ^ stream) ^ epoch) ^ slot) ^ coordinate);
}

// Uniform in [0, 1) from the top 24 bits, exact in float.
MULTILINEAR_SAT_INLINE float uniform_from_hash(uint64_t hash) {
    return static_cast<float>(hash >> 40) * (1.0f / 16777216.0f);
}

// The restart stream: a fresh coordinate for (epoch, slot, coordinate).
MULTILINEAR_SAT_INLINE float uniform_random(uint64_t seed, uint64_t epoch, uint64_t slot, uint64_t coordinate) {
    return uniform_from_hash(hash_combine(seed, restart_stream, epoch, slot, coordinate));
}

// The first uniform behind a kick (exposed so tests can check the streams never meet).
MULTILINEAR_SAT_INLINE float kick_uniform(uint64_t seed, uint64_t epoch, uint64_t slot, uint64_t coordinate) {
    return uniform_from_hash(hash_combine(seed, kick_stream, epoch, slot, coordinate));
}

// Standard normal for the kick stream (Box-Muller, one output kept).
MULTILINEAR_SAT_INLINE float gaussian_random(uint64_t seed, uint64_t epoch, uint64_t slot, uint64_t coordinate) {
    const uint64_t first = hash_combine(seed, kick_stream, epoch, slot, coordinate);
    const float u1 = uniform_from_hash(first) + 1e-7f;
    const float u2 = uniform_from_hash(hash_mix(first));
    return sqrtf(-2.0f * logf(u1)) * cosf(6.2831853f * u2);
}

// The walk stream: the draw-th 64-bit hash of the flip-th step of a slot. A step uses at
// most four draws, so the coordinate is flip * 4 + draw.
MULTILINEAR_SAT_INLINE uint64_t walk_hash(uint64_t seed, uint64_t epoch, uint64_t slot, int64_t flip, int draw) {
    return hash_combine(seed, walk_stream, epoch, slot, static_cast<uint64_t>(flip) * 4 + static_cast<uint64_t>(draw));
}

}  // namespace multilinear_sat
