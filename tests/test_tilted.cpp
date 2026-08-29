// The tilted seed: the self-normalised annealed samples estimate E_tilted[x] (checked by
// enumeration on a small formula, the Python record's Table 1), the theta step moves toward
// the solutions, and the seed followed by the polish solves a planted instance with a
// certificate.
#include <cmath>

#include "backend.hpp"
#include "doctest.h"
#include "planted_instances.hpp"
#include "solver.hpp"
#include "tilted_state.hpp"

using namespace multilinear_sat;

namespace {
// E_tilted[x] under q_theta(x) exp(beta S(x)) / Z by enumeration, and E_theta[x] = tanh theta.
std::vector<double> tilted_mean_by_enumeration(const Formula& f, const std::vector<float>& theta, double beta) {
    const int n = f.variable_count;
    std::vector<double> mean(n, 0.0);
    double partition = 0.0;
    for (int bits = 0; bits < (1 << n); ++bits) {
        std::vector<int8_t> assignment(n);
        double log_q = 0.0;
        for (int v = 0; v < n; ++v) {
            assignment[v] = (bits >> v) & 1 ? 1 : -1;
            log_q += std::log(0.5 * (1.0 + assignment[v] * std::tanh(theta[v])));
        }
        const double weight = std::exp(log_q + beta * (f.clause_count() - count_violated(f, assignment)));
        partition += weight;
        for (int v = 0; v < n; ++v) mean[v] += weight * assignment[v];
    }
    for (double& value : mean) value /= partition;
    return mean;
}
}  // namespace

TEST_CASE("the weighted mean of the annealed samples is a consistent estimate of the tilted mean") {
    auto planted = testing::planted_3sat(10, 3.5, 21);
    const Formula& f = planted.formula;
    std::vector<float> theta(f.variable_count);
    uint64_t state = 5;
    for (float& value : theta) value = 0.8f * (static_cast<float>(testing::next_random(state) % 1000) / 500.0f - 1.0f);
    for (float beta : {0.5f, 2.0f}) {
        const std::vector<double> exact = tilted_mean_by_enumeration(f, theta, beta);
        double previous_error = 1e9;
        for (int slots : {256, 4096}) {
            auto backend = make_cpu_backend();
            backend->initialise(f, slots, 3);
            TiltedState tilted(1, slots, f.variable_count);
            tilted.theta = theta;
            tilted.beta[0] = beta;
            std::vector<int> violated;
            backend->draw_tilted(tilted.theta, slots, 11);
            backend->anneal(tilted.theta, tilted.beta, slots, 16 * f.variable_count, 11, tilted.log_weights, violated, tilted.found);
            backend->walk_assignments(tilted.assignments);
            tilted.normalise_weights(0);
            double squared_error = 0.0;
            for (int v = 0; v < f.variable_count; ++v) {
                double estimate = 0.0;
                for (int s = 0; s < slots; ++s) estimate += tilted.weights[s] * (tilted.assignments[static_cast<size_t>(s) * f.variable_count + v] ? 1.0 : -1.0);
                squared_error += (estimate - exact[v]) * (estimate - exact[v]);
            }
            const double root_mean_square = std::sqrt(squared_error / f.variable_count);
            CHECK(root_mean_square < (slots == 256 ? 0.15 : 0.05));
            CHECK(root_mean_square < previous_error);
            previous_error = root_mean_square;
        }
    }
}

TEST_CASE("the theta step raises the mean satisfied count of the draws") {
    auto planted = testing::planted_3sat(30, 4.0, 22);
    const Formula& f = planted.formula;
    SolverConfiguration configuration;
    configuration.tilted.tilted_groups = 1;
    auto backend = make_cpu_backend();
    backend->initialise(f, 512, 4);
    TiltedState tilted(1, 512, f.variable_count);
    tilted.initialise_group(0, configuration.tilted, 4, 1);
    tilted.beta[0] = 1.0f;
    std::vector<int> violated;
    auto mean_violated = [&](uint64_t epoch) {
        backend->draw_tilted(tilted.theta, 512, epoch);
        std::vector<uint8_t> found;
        backend->anneal(tilted.theta, tilted.beta, 512, 0, epoch, tilted.log_weights, violated, found);   // zero rungs: the raw draws
        double total = 0.0;
        for (int count : violated) total += count;
        return total / 512.0;
    };
    const double before = mean_violated(100);
    for (int step = 0; step < 40; ++step) {
        const uint64_t epoch = 200 + step;
        backend->draw_tilted(tilted.theta, 512, epoch);
        backend->anneal(tilted.theta, tilted.beta, 512, 2 * f.variable_count, epoch, tilted.log_weights, violated, tilted.found);
        backend->walk_assignments(tilted.assignments);
        tilted.update_group(0, configuration.tilted);
    }
    CHECK(mean_violated(300) < 0.7 * before);
}

TEST_CASE("the tilted seed followed by the polish solves a planted instance with a certificate") {
    auto planted = testing::planted_3sat(60, 4.1, 23);
    SolverConfiguration configuration;
    configuration.backend = BackendKind::Cpu;
    configuration.batch_size = 64;
    configuration.seed = 6;
    configuration.seed_kind = SeedKind::Tilted;
    configuration.seed_steps = 5;
    configuration.polish_flips = 600;
    configuration.tilted.tilted_groups = 2;
    const SolveResult result = solve(planted.formula, configuration);
    REQUIRE(result.status == Status::Satisfiable);
    CHECK(satisfies(planted.formula, result.assignment));
    CHECK(result.seed_seconds > 0.0);
    configuration.tilted.tilted_groups = 3;   // 64 slots do not split into 3 groups
    CHECK_THROWS(solve(planted.formula, configuration));
}
