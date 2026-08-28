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

TEST_CASE("a planted satisfiable instance is solved and the model is certified") {
    auto planted = testing::planted_3sat(80, 4.0, 1);
    SolveResult result = solve(planted.formula, cpu_configuration());
    REQUIRE(result.status == Status::Satisfiable);
    CHECK(result.best_violated == 0);
    CHECK(satisfies(planted.formula, result.assignment));
    CHECK(result.backend_name == std::string("cpu"));
    CHECK(result.iterations > 0);
}

TEST_CASE("an unsatisfiable formula ends Unknown with the best point reported") {
    Formula f = make_formula(2, {{1, 2}, {-1, 2}, {1, -2}, {-1, -2}});
    SolverConfiguration configuration = cpu_configuration();
    configuration.iteration_limit = 200;
    SolveResult result = solve(f, configuration);
    CHECK(result.status == Status::Unknown);
    CHECK(result.best_violated == 1);
    CHECK(result.iterations == 200);
    CHECK(count_violated(f, result.assignment) == 1);
}

TEST_CASE("runs are reproducible from the seed") {
    auto planted = testing::planted_3sat(60, 4.1, 2);
    SolverConfiguration configuration = cpu_configuration();
    SolveResult first = solve(planted.formula, configuration);
    SolveResult second = solve(planted.formula, configuration);
    CHECK(first.iterations == second.iterations);
    CHECK(first.assignment == second.assignment);
}

TEST_CASE("a stalled slot restarts before its Luby cutoff, and bad configurations are refused") {
    Formula f = make_formula(2, {{1, 2}, {-1, 2}, {1, -2}, {-1, -2}});   // unsatisfiable, never improves past 1
    SolverConfiguration configuration = cpu_configuration();
    configuration.batch_size = 1;
    configuration.luby_unit = 1000;
    configuration.stall_patience = 5;
    configuration.iteration_limit = 30;
    configuration.step.focused_kick = false;
    configuration.step.kick_decay = 0.5f;
    CHECK(solve(f, configuration).restarts >= 4);
    configuration.luby_unit = 0;
    CHECK_THROWS(solve(f, configuration));
    configuration.luby_unit = 10;
    configuration.step.kick_sigma = -1.0f;
    CHECK_THROWS(solve(f, configuration));
}

TEST_CASE("restarts follow the Luby schedule") {
    Formula f = make_formula(2, {{1, 2}, {-1, 2}, {1, -2}, {-1, -2}});   // unsatisfiable: never stops early
    SolverConfiguration configuration = cpu_configuration();
    configuration.batch_size = 1;
    configuration.luby_unit = 10;
    configuration.iteration_limit = 10 * (1 + 1 + 2 + 1) + 5;   // through four cutoffs, inside the fifth
    SolveResult result = solve(f, configuration);
    CHECK(result.restarts == 4);
}
