#include <cmath>

#include "doctest.h"
#include "luby.hpp"
#include "random_hash.hpp"

using namespace multilinear_sat;

TEST_CASE("the Luby sequence starts 1 1 2 1 1 2 4 1 1 2 1 1 2 4 8") {
    const int64_t expected[15] = {1, 1, 2, 1, 1, 2, 4, 1, 1, 2, 1, 1, 2, 4, 8};
    for (int i = 0; i < 15; ++i) CHECK(luby(i + 1) == expected[i]);
    CHECK(luby(31) == 16);
    CHECK(luby(32) == 1);
}

TEST_CASE("hash randomness is deterministic, uniform and Gaussian") {
    CHECK(uniform_random(1, 2, 3, 4) == uniform_random(1, 2, 3, 4));
    CHECK(uniform_random(1, 2, 3, 4) != uniform_random(1, 2, 3, 5));
    double sum = 0.0, sum_squares = 0.0, gaussian_sum = 0.0, gaussian_squares = 0.0;
    const int samples = 200000;
    for (int i = 0; i < samples; ++i) {
        const float u = uniform_random(7, 0, 0, i);
        CHECK(u >= 0.0f);
        CHECK(u < 1.0f);
        sum += u; sum_squares += u * u;
        const float g = gaussian_random(7, 1, 0, i);
        gaussian_sum += g; gaussian_squares += g * g;
    }
    CHECK(sum / samples == doctest::Approx(0.5).epsilon(0.01));
    CHECK(sum_squares / samples == doctest::Approx(1.0 / 3.0).epsilon(0.01));
    CHECK(gaussian_sum / samples == doctest::Approx(0.0).scale(1.0).epsilon(0.01));
    CHECK(gaussian_squares / samples == doctest::Approx(1.0).epsilon(0.02));
}
