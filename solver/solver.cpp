#include "solver.hpp"

#include <cstdio>
#include <stdexcept>

#include "luby.hpp"
#include "polish_phase.hpp"
#include "posterior.hpp"
#include "seed_phase.hpp"
#include "tilted_phase.hpp"

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
    const bool seed_runs = (c.seed_kind == SeedKind::Ascent || c.seed_kind == SeedKind::Tilted) && c.seed_steps > 0;
    if (!seed_runs && c.polish_flips == 0) throw std::invalid_argument("a run needs seed steps (ascent or tilted) or walk flips");
    if (c.seed_kind == SeedKind::Tilted) {
        const TiltedParameters& t = c.tilted;
        if (t.tilted_groups <= 0 || c.batch_size % t.tilted_groups != 0) throw std::invalid_argument("batch_size must be a positive multiple of tilted_groups");
        if (t.tilted_rungs_per_variable < 0.0f || t.tilted_learning_rate <= 0.0f || t.tilted_learning_rate_half_life <= 0.0f || t.tilted_init_scale < 0.0f)
            throw std::invalid_argument("tilted_rungs_per_variable and tilted_init_scale must not be negative, the learning rate and its half life must be positive");
        if (t.beta_initial < 0.0f || t.beta_growth_factor < 1.0f || t.beta_max < t.beta_initial || t.ess_floor_fraction < 0.0f || t.tilted_luby_unit_steps <= 0)
            throw std::invalid_argument("the beta schedule needs 0 <= beta_initial <= beta_max, beta_growth_factor >= 1, ess_floor_fraction >= 0 and positive tilted_luby_unit_steps");
    }
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

// Cumulative counts after each run, so a reader can difference consecutive lines into per-run outcomes.
static void print_run(const RunState& state, int64_t run, int64_t scale) {
    const SolveResult& r = state.result;
    std::fprintf(stderr, "c run %lld elapsed %.3f best %d restarts %lld heuristic_failures %lld rigorous_failures %lld posterior_beta %.6f posterior_rigorous %.6f"
                         " scale %lld polish_successes %lld flips %lld seed_seconds %.4f polish_seconds %.4f\n",
                 static_cast<long long>(run), state.elapsed(), r.best_violated, static_cast<long long>(r.restarts),
                 static_cast<long long>(r.heuristic_failures), static_cast<long long>(r.rigorous_failures), r.posterior_beta, r.posterior_rigorous,
                 static_cast<long long>(scale), static_cast<long long>(r.polish_successes), static_cast<long long>(r.flips), r.seed_seconds, r.polish_seconds);
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
        const int64_t scale = configuration.restart_schedule == RestartSchedule::Luby ? luby(run) : 1;
        if (configuration.seed_kind == SeedKind::Tilted) run_tilted_seed_phase(state, configuration.seed_steps * scale);
        else run_seed_phase(state, configuration.seed_steps * scale);
        run_polish_phase(state, configuration.polish_flips * scale);
        if (state.stop) break;
        ++state.result.runs;
        update_posteriors(state);
        if (configuration.verbose) print_run(state, run, scale);
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
