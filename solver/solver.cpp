#include "solver.hpp"

#include <chrono>
#include <cstdio>
#include <stdexcept>

#include "luby.hpp"

namespace multilinear_sat {

static std::unique_ptr<Backend> choose_backend(BackendKind kind) {
    if (kind == BackendKind::Cpu) return make_cpu_backend();
    if (kind == BackendKind::Cuda) return make_cuda_backend();
    return cuda_available() ? make_cuda_backend() : make_cpu_backend();
}

SolveResult solve(const Formula& formula, const SolverConfiguration& configuration) {
    auto backend = choose_backend(configuration.backend);
    return solve_with(formula, configuration, *backend);
}

SolveResult solve_with(const Formula& formula, const SolverConfiguration& configuration, Backend& backend) {
    using clock = std::chrono::steady_clock;
    const auto start = clock::now();
    const int batch = configuration.batch_size;
    if (batch <= 0) throw std::invalid_argument("batch_size must be positive");
    if (configuration.luby_unit <= 0) throw std::invalid_argument("luby_unit must be positive");
    if (configuration.stall_patience < 0) throw std::invalid_argument("stall_patience must not be negative");
    if (configuration.step.step_size <= 0.0f) throw std::invalid_argument("step_size must be positive");
    if (configuration.step.kick_sigma < 0.0f || configuration.step.kick_decay <= 0.0f) throw std::invalid_argument("kick_sigma must not be negative and kick_decay must be positive");
    backend.initialise(formula, batch, configuration.seed);

    SolveResult result;
    result.backend_name = backend.name();
    result.best_violated = formula.clause_count() + 1;
    std::vector<int> violated(batch), slot_restarts(batch, 0), since_restart(batch, 0), since_improvement(batch, 0);
    std::vector<int> slot_best(batch, formula.clause_count() + 1), to_restart;
    uint64_t epoch = 0;

    for (int64_t iteration = 0;; ++iteration) {
        backend.iterate(configuration.step, iteration, violated);
        result.iterations = iteration + 1;
        for (int b = 0; b < batch; ++b) {
            if (violated[b] < result.best_violated) {
                result.best_violated = violated[b];
                result.assignment = backend.rounded_assignment(b);
            }
            if (violated[b] < slot_best[b]) { slot_best[b] = violated[b]; since_improvement[b] = 0; }
            else ++since_improvement[b];
            ++since_restart[b];
        }
        if (result.best_violated == 0) {
            result.status = Status::Satisfiable;
            break;
        }
        const double elapsed = std::chrono::duration<double>(clock::now() - start).count();
        if (elapsed >= configuration.time_limit_seconds) break;
        if (configuration.iteration_limit > 0 && result.iterations >= configuration.iteration_limit) break;

        to_restart.clear();
        for (int b = 0; b < batch; ++b) {
            const int64_t cutoff = configuration.luby_unit * luby(slot_restarts[b] + 1);
            const bool stalled = configuration.stall_patience > 0 && since_improvement[b] >= configuration.stall_patience;
            if (since_restart[b] >= cutoff || stalled) {
                to_restart.push_back(b);
                ++slot_restarts[b];
                since_restart[b] = 0;
                since_improvement[b] = 0;
                slot_best[b] = formula.clause_count() + 1;
            }
        }
        if (!to_restart.empty()) {
            backend.restart_slots(to_restart, ++epoch);
            result.restarts += static_cast<int64_t>(to_restart.size());
        }
        if (configuration.verbose && iteration % 100 == 0) {
            std::fprintf(stderr, "c iteration %lld best violated %d restarts %lld %.1fs\n",
                         static_cast<long long>(iteration), result.best_violated,
                         static_cast<long long>(result.restarts), elapsed);
        }
    }
    result.elapsed_seconds = std::chrono::duration<double>(clock::now() - start).count();
    if (result.status == Status::Satisfiable && !satisfies(formula, result.assignment)) {
        throw std::logic_error("backend reported a satisfying point that the checker rejects");
    }
    return result;
}

}  // namespace multilinear_sat
