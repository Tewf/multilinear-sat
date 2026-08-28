#include <cmath>
#include <vector>

#include "doctest.h"
#include "energy_math.hpp"
#include "planted_instances.hpp"

using namespace multilinear_sat;

static double total_energy(const Formula& f, const std::vector<float>& point) {
    double total = 0.0;
    for (int c = 0; c < f.clause_count(); ++c)
        total += clause_energy(f.literals.data() + f.clause_offsets[c], f.clause_length(c), point.data());
    return total;
}

TEST_CASE("clause energy is -1 on satisfying vertices and +1 on falsifying ones") {
    const int32_t clause[3] = {1, -2, 3};
    const float satisfied_point[3] = {1.0f, 1.0f, -1.0f};    // x1 true satisfies literal 1
    const float falsified_point[3] = {-1.0f, 1.0f, -1.0f};   // every literal false
    CHECK(clause_energy(clause, 3, satisfied_point) == doctest::Approx(-1.0f));
    CHECK(clause_energy(clause, 3, falsified_point) == doctest::Approx(1.0f));
    CHECK(clause_violated_by_rounding(clause, 3, falsified_point));
    CHECK_FALSE(clause_violated_by_rounding(clause, 3, satisfied_point));
}

TEST_CASE("the energy at the centre is the expected value under uniform rounding") {
    const int32_t clause[3] = {1, 2, 3};
    const float centre[3] = {0.0f, 0.0f, 0.0f};
    // P(falsified) = 1/8, so E = (1/8)(+1) + (7/8)(-1) = -3/4
    CHECK(clause_energy(clause, 3, centre) == doctest::Approx(-0.75f));
}

TEST_CASE("the analytic gradient matches central finite differences") {
    auto planted = testing::planted_3sat(40, 4.2, 3);
    const Formula& f = planted.formula;
    std::vector<float> point(f.variable_count);
    uint64_t state = 11;
    for (float& x : point) x = 1.6f * (static_cast<float>(testing::next_random(state) % 10000) / 10000.0f) - 0.8f;
    for (int v = 0; v < f.variable_count; v += 7) {
        float analytic = 0.0f;
        for (int o = f.occurrence_offsets[v]; o < f.occurrence_offsets[v + 1]; ++o) {
            const int c = f.occurrence_clauses[o];
            analytic += clause_gradient_at(f.literals.data() + f.clause_offsets[c], f.clause_length(c), point.data(),
                                           f.occurrence_positions[o]);
        }
        // The energy is affine in each single variable, so the central difference is exact
        // for any h; a large h keeps float round-off negligible.
        const float h = 0.25f;
        std::vector<float> plus = point, minus = point;
        plus[v] += h; minus[v] -= h;
        const double numeric = (total_energy(f, plus) - total_energy(f, minus)) / (2.0 * h);
        CHECK(analytic == doctest::Approx(numeric).epsilon(1e-4).scale(1.0));
    }
}
