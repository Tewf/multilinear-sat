// The Las Vegas loop: runs of the whole batch, each a seed (gradient iterations, a uniform
// draw or all false) then a polish (the walk), on the Luby schedule; stop at the first
// rounded point or walk state that satisfies every row, or at the time, iteration or run
// limit with the best point seen and the two UNSAT posteriors of the failed polishes.
#pragma once
#include <cstdint>
#include <string>
#include <vector>

#include "backend.hpp"
#include "configuration.hpp"
#include "formula.hpp"

namespace multilinear_sat {

enum class Status { Satisfiable, Unknown };

struct SolveResult {
    Status status = Status::Unknown;
    std::vector<int8_t> assignment;   // a satisfying assignment, or the best rounded point seen
    int best_violated = -1;           // rows the returned assignment violates (0 when Satisfiable)
    int64_t iterations = 0;           // gradient iterations of the batch
    int64_t restarts = 0;             // slot restarts performed
    int64_t runs = 0;                 // completed seed-and-polish runs of the batch
    int64_t flips = 0;                // walk steps over all slots
    int64_t polish_successes = 0;     // heuristic slots whose polish ended satisfied, over all completed runs
    int64_t heuristic_failures = 0;   // heuristic slots whose polish ended violated
    int64_t rigorous_failures = 0;    // Schoening slots whose 3n flips ended violated
    double seed_seconds = 0.0, polish_seconds = 0.0, elapsed_seconds = 0.0;
    double posterior_rigorous = 0.0;  // P(UNSAT | rigorous failures), posterior.hpp; never a verdict
    double posterior_beta = 0.0;      // P(UNSAT | heuristic failures) under the Beta-mixture model
    std::string backend_name;
};

SolveResult solve(const Formula& formula, const SolverConfiguration& configuration);
SolveResult solve_with(const Formula& formula, const SolverConfiguration& configuration, Backend& backend);

}  // namespace multilinear_sat
