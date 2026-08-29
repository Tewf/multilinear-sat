// What the run loop carries between its phases: the batch's per-slot bookkeeping, the
// clock, the split between heuristic and rigorous slots, and the result being built.
#pragma once
#include <chrono>
#include <cmath>
#include <stdexcept>
#include <utility>
#include <vector>

#include "backend.hpp"
#include "solver.hpp"

namespace multilinear_sat {

struct RunState {
    const Formula& formula;
    const SolverConfiguration& configuration;
    Backend& backend;
    std::chrono::steady_clock::time_point start = std::chrono::steady_clock::now();
    SolveResult result;
    std::vector<int> violated, since_improvement, slot_best;
    std::vector<int32_t> flips_done;
    int64_t iteration = 0;
    uint64_t epoch = 0;
    int rigorous_slots = 0;   // the last rigorous_slots slots of the batch walk Schoening's rule
    bool stop = false;        // a limit was reached, or a certificate was found in solver mode

    RunState(const Formula& formula_, const SolverConfiguration& configuration_, Backend& backend_)
        : formula(formula_), configuration(configuration_), backend(backend_) {
        const int batch = configuration.batch_size;
        result.backend_name = backend.name();
        result.best_violated = formula.clause_count() + 1;
        violated.assign(batch, 0);
        flips_done.assign(batch, 0);
        rigorous_slots = static_cast<int>(std::lround(static_cast<double>(configuration.rigorous_fraction) * batch));
        reset_slot_records();
    }

    double elapsed() const { return std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count(); }
    bool heuristic(int slot) const { return slot < configuration.batch_size - rigorous_slots; }
    int best_slot() const {
        int best = 0;
        for (int slot = 1; slot < configuration.batch_size; ++slot) if (violated[slot] < violated[best]) best = slot;
        return best;
    }

    void reset_slot_records() {
        since_improvement.assign(configuration.batch_size, 0);
        slot_best.assign(configuration.batch_size, formula.clause_count() + 1);
    }

    // A zero count is a certificate only once the checker agrees; a backend that lies is a
    // bug, not an UNKNOWN. In solver mode the first certificate ends the search; with a run
    // limit the batch completes its runs so that every polish outcome is counted.
    void record_certificate(std::vector<int8_t> assignment) {
        if (!satisfies(formula, assignment)) throw std::logic_error("backend reported a satisfying point that the checker rejects");
        if (result.status != Status::Satisfiable) {
            result.status = Status::Satisfiable;
            result.best_violated = 0;
            result.assignment = std::move(assignment);
        }
        if (configuration.run_limit == 0) stop = true;
    }

    void record_best(int count, std::vector<int8_t> assignment) {
        if (count == 0) record_certificate(std::move(assignment));
        else if (count < result.best_violated) {
            result.best_violated = count;
            result.assignment = std::move(assignment);
        }
    }

    void check_limits() {
        if (elapsed() >= configuration.time_limit_seconds) stop = true;
        if (configuration.iteration_limit > 0 && iteration >= configuration.iteration_limit) stop = true;
    }
};

}  // namespace multilinear_sat
