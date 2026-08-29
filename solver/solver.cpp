#include "solver.hpp"

#include <cstdio>
#include <stdexcept>

#include "luby.hpp"
#include "polish_phase.hpp"
#include "posterior.hpp"
#include "seed_phase.hpp"

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

static void validate(const SolverConfiguration& c, const Formula& formula) {
    if (c.batch_size <= 0) throw std::invalid_argument("batch_size must be positive");
    if (c.seed_steps < 0 || c.polish_flips < 0 || c.run_limit < 0) throw std::invalid_argument("seed_steps, polish_flips and run_limit must not be negative");
    if ((c.seed_kind != SeedKind::Ascent || c.seed_steps == 0) && c.polish_flips == 0) throw std::invalid_argument("a run needs gradient steps or walk flips: set seed_steps with the ascent, or polish_flips");
    if (c.stall_patience < 0) throw std::invalid_argument("stall_patience must not be negative");
    if (c.step.step_size <= 0.0f) throw std::invalid_argument("step_size must be positive");
    if (c.step.kick_sigma < 0.0f || c.step.kick_decay <= 0.0f) throw std::invalid_argument("kick_sigma must not be negative and kick_decay must be positive");
    if (c.walk.walk_flips_per_launch <= 0) throw std::invalid_argument("walk_flips_per_launch must be positive");
    if (c.walk.walk_noise < 0.0f || c.walk.walk_noise > 1.0f) throw std::invalid_argument("walk_noise must lie in [0, 1]");
    if (c.walk.probsat_eps <= 0.0f || c.walk.metropolis_beta < 0.0f) throw std::invalid_argument("probsat_eps must be positive and metropolis_beta not negative");
    if (c.rigorous_fraction < 0.0f || c.rigorous_fraction > 1.0f) throw std::invalid_argument("rigorous_fraction must lie in [0, 1]");
    if (c.rigorous_fraction > 0.0f && (formula.parity_count() > 0 || formula.max_clause_length() > 3)) throw std::invalid_argument("Schoening's bound, hence rigorous_fraction, needs a 3-CNF");
    if (c.prior_satisfiable <= 0.0 || c.prior_satisfiable >= 1.0 || c.beta_prior_a <= 0.0 || c.beta_prior_b <= 0.0) throw std::invalid_argument("prior_satisfiable must lie in (0, 1) and the Beta prior parameters must be positive");
    if (formula.max_clause_length() > 255) throw std::invalid_argument("the walk counts true literals in a byte: no row may exceed 255 literals");
}

static void print_run(const RunState& state, int64_t run) {
    const SolveResult& r = state.result;
    std::fprintf(stderr, "c run %lld elapsed %.3f best %d restarts %lld heuristic_failures %lld rigorous_failures %lld posterior_beta %.6f posterior_rigorous %.6f\n",
                 static_cast<long long>(run), state.elapsed(), r.best_violated, static_cast<long long>(r.restarts),
                 static_cast<long long>(r.heuristic_failures), static_cast<long long>(r.rigorous_failures), r.posterior_beta, r.posterior_rigorous);
}

static void update_posteriors(RunState& state) {
    const SolverConfiguration& c = state.configuration;
    state.result.posterior_rigorous = rigorous_posterior(state.formula.variable_count, state.result.rigorous_failures, c.prior_satisfiable);
    state.result.posterior_beta = beta_mixture_posterior(state.result.heuristic_failures, c.beta_prior_a, c.beta_prior_b, c.prior_satisfiable);
}

SolveResult solve_with(const Formula& formula, const SolverConfiguration& configuration, Backend& backend) {
    validate(configuration, formula);
    RunState state(formula, configuration, backend);
    backend.initialise(formula, configuration.batch_size, configuration.seed);
    update_posteriors(state);
    for (int64_t run = 1; !state.stop; ++run) {
        const int64_t scale = luby(run);
        run_seed_phase(state, configuration.seed_steps * scale);
        run_polish_phase(state, configuration.polish_flips * scale);
        if (state.stop) break;
        ++state.result.runs;
        update_posteriors(state);
        if (configuration.verbose) print_run(state, run);
        if (configuration.run_limit > 0 && run >= configuration.run_limit) break;
        backend.restart_slots(every_slot(configuration.batch_size), ++state.epoch);
        state.result.restarts += configuration.batch_size;
        state.reset_slot_records();
    }
    state.result.elapsed_seconds = state.elapsed();
    if (state.result.status == Status::Satisfiable && !satisfies(formula, state.result.assignment)) {
        throw std::logic_error("the certificate no longer satisfies the formula");
    }
    return state.result;
}

}  // namespace multilinear_sat
