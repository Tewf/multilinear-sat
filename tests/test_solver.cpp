#include "doctest.h"
#include "planted_instances.hpp"
#include "solver.hpp"

using namespace multilinear_sat;

static SolverConfiguration cpu_configuration() {
    SolverConfiguration configuration;
    configuration.backend = BackendKind::Cpu;
    configuration.batch_size = 64;
    configuration.time_limit_seconds = 60.0;
    configuration.seed = 5;
    return configuration;
}

static Formula contradiction() {
    return make_formula(2, {{1, 2}, {-1, 2}, {1, -2}, {-1, -2}});   // unsatisfiable: never improves past 1
}

TEST_CASE("a planted satisfiable instance is solved and the model is certified") {
    auto planted = testing::planted_3sat(80, 4.0, 1);
    SolveResult result = solve(planted.formula, cpu_configuration());
    REQUIRE(result.status == Status::Satisfiable);
    CHECK(result.best_violated == 0);
    CHECK(satisfies(planted.formula, result.assignment));
    CHECK(result.backend_name == std::string("cpu"));
    CHECK(result.iterations > 0);
    CHECK(result.flips == 0);
}

TEST_CASE("an unsatisfiable formula ends Unknown with the best point reported") {
    SolverConfiguration configuration = cpu_configuration();
    configuration.iteration_limit = 200;
    SolveResult result = solve(contradiction(), configuration);
    CHECK(result.status == Status::Unknown);
    CHECK(result.best_violated == 1);
    CHECK(result.iterations == 200);
    CHECK(count_violated(contradiction(), result.assignment) == 1);
}

TEST_CASE("runs are reproducible from the seed") {
    auto planted = testing::planted_3sat(60, 4.1, 2);
    SolverConfiguration configuration = cpu_configuration();
    SolveResult first = solve(planted.formula, configuration);
    SolveResult second = solve(planted.formula, configuration);
    CHECK(first.iterations == second.iterations);
    CHECK(first.assignment == second.assignment);
}

TEST_CASE("a stalled slot is resampled before its run ends, and bad configurations are refused") {
    SolverConfiguration configuration = cpu_configuration();
    configuration.batch_size = 1;
    configuration.seed_steps = 1000;
    configuration.stall_patience = 5;
    configuration.iteration_limit = 30;
    configuration.step.focused_kick = false;
    configuration.step.kick_decay = 0.5f;
    CHECK(solve(contradiction(), configuration).restarts >= 4);
    configuration.seed_steps = 0;
    CHECK_THROWS(solve(contradiction(), configuration));          // nothing to run per run
    configuration.seed_steps = 10;
    configuration.step.kick_sigma = -1.0f;
    CHECK_THROWS(solve(contradiction(), configuration));
    configuration.step.kick_sigma = 0.3f;
    configuration.rigorous_fraction = 0.5f;
    CHECK_THROWS(solve(make_formula(4, {{1, 2, 3, 4}}), configuration));   // Schoening's bound needs a 3-CNF
}

TEST_CASE("runs follow the Luby schedule") {
    SolverConfiguration configuration = cpu_configuration();
    configuration.batch_size = 1;
    configuration.seed_steps = 10;
    configuration.iteration_limit = 10 * (1 + 1 + 2 + 1) + 5;   // through four runs, inside the fifth
    SolveResult result = solve(contradiction(), configuration);
    CHECK(result.restarts == 4);
    CHECK(result.runs == 4);
}

TEST_CASE("the walk alone, from uniform or all-false starts, and the ascent with a polish all solve and certify") {
    auto planted = testing::planted_3sat(100, 4.2, 3);
    SolverConfiguration configuration = cpu_configuration();
    SUBCASE("uniform starts") { configuration.seed_kind = SeedKind::Uniform; configuration.polish_flips = 1000; }
    SUBCASE("all false") { configuration.seed_kind = SeedKind::AllFalse; configuration.polish_flips = 1000; }
    SUBCASE("ascent then probsat") { configuration.seed_steps = 20; configuration.polish_flips = 1000; configuration.walk.walk_rule = WalkRule::ProbSat; }
    SUBCASE("ascent then metropolis") { configuration.seed_steps = 20; configuration.polish_flips = 3000; configuration.walk.walk_rule = WalkRule::Metropolis; configuration.walk.metropolis_beta = 2.0f; }
    SolveResult result = solve(planted.formula, configuration);
    REQUIRE(result.status == Status::Satisfiable);
    CHECK(satisfies(planted.formula, result.assignment));
    CHECK(result.flips > 0);
    CHECK(result.polish_seconds > 0.0);
}

TEST_CASE("with a run limit the batch completes its runs and reports every polish outcome and the posteriors") {
    auto planted = testing::planted_3sat(50, 4.2, 4);
    SolverConfiguration configuration = cpu_configuration();
    configuration.batch_size = 32;
    configuration.seed_kind = SeedKind::Uniform;
    configuration.polish_flips = 300;
    configuration.run_limit = 2;
    configuration.rigorous_fraction = 0.25f;
    SolveResult result = solve(planted.formula, configuration);
    CHECK(result.runs == 2);
    CHECK(result.restarts == 32);
    CHECK(result.polish_successes + result.heuristic_failures == 2 * 24);
    CHECK(result.polish_successes > 0);
    CHECK(result.status == Status::Satisfiable);
    CHECK(satisfies(planted.formula, result.assignment));
    CHECK(result.rigorous_failures <= 2 * 8);
    CHECK(result.posterior_beta >= 0.5);
    CHECK(result.posterior_beta < 1.0);
    CHECK(result.posterior_rigorous >= 0.5);
    const int64_t walked = result.flips;
    CHECK(walked <= 2 * (24 * 300 + 8 * 150));
}
