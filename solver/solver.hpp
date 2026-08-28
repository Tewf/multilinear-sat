// The Las Vegas loop: iterate the batch, restart slots on the Luby schedule (and on
// stalls if asked), stop at the first rounded point that satisfies every clause, or
// at the time or iteration limit with the best point seen.
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
    int best_violated = -1;           // clauses the returned assignment violates (0 when Satisfiable)
    int64_t iterations = 0;           // batch iterations performed
    int64_t restarts = 0;             // slot restarts performed
    double elapsed_seconds = 0.0;
    std::string backend_name;
};

SolveResult solve(const Formula& formula, const SolverConfiguration& configuration);
SolveResult solve_with(const Formula& formula, const SolverConfiguration& configuration, Backend& backend);

}  // namespace multilinear_sat
