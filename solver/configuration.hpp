// Every tunable of the solver in one place. Defaults are the values the benchmark
// in benchmark/results.md was run with; the command line overrides any of them.
#pragma once
#include <cstdint>

namespace multilinear_sat {

enum class BackendKind { Cpu, Cuda, Auto };
enum class SeedKind { Uniform, AllFalse, Ascent, Tilted };    // where each run's walk starts
enum class WalkRule { Skc, ProbSat, Schoening, Metropolis };  // how the walk picks a variable
enum class RestartSchedule { Luby, Fixed };                   // run k's budget: times luby(k), or the same every run

struct StepParameters {
    float step_size = 0.1f;      // gradient step on the cube
    float momentum = 0.9f;       // heavy-ball momentum
    float kick_sigma = 0.3f;     // standard deviation of the Gaussian kick; 0 disables it
    bool focused_kick = true;    // kick only variables of clauses the rounded point violates
    float kick_decay = 1.0f;     // multiplies kick_sigma every iteration (1 = constant)
};

struct WalkParameters {
    WalkRule walk_rule = WalkRule::Skc;
    float walk_noise = 0.5f;          // skc: probability of a random variable when every candidate breaks something
    float probsat_cb = 2.06f;         // probsat: a variable with break b has weight (probsat_eps + b)^-probsat_cb
    float probsat_eps = 0.9f;         //          (Balint and Schoning 2012, their 3-SAT values)
    float metropolis_beta = 1.0f;     // metropolis: accept a flip losing d satisfied rows with probability exp(-beta d)
    int walk_flips_per_launch = 32;   // flips per slot between two certificate checks (one CUDA launch)
};

// The tilted seed (seed_kind tilted): groups of slots share a natural parameter vector theta,
// each step draws the group's slots from q_theta, anneals them toward q_theta exp(beta S) and
// steps theta by the weighted sample mean minus tanh theta. Set once from the Python
// record's calibration, never tuned: PROVISIONAL.
struct TiltedParameters {
    int tilted_groups = 16;                          // the batch splits evenly into this many groups
    float tilted_rungs_per_variable = 2.0f;          // rungs of the annealing ladder per step, times n
    float tilted_learning_rate = 0.1f;               // eta_0 of the step on theta
    float tilted_learning_rate_half_life = 100.0f;   // eta_t = eta_0 / (1 + t / this), t steps since the group's restart
    float tilted_init_scale = 1.0f;                  // theta ~ Uniform(-scale, scale) at a group's start
    float beta_initial = 0.05f;
    float beta_growth_factor = 1.05f;                // applied while the group's effective sample size stays above the floor
    float beta_max = 5.0f;
    float ess_floor_fraction = 0.25f;                // raise beta while ESS >= this * slots per group, else hold
    int tilted_luby_unit_steps = 50;                 // a group's restart budget = luby(i) * this, in steps
};

struct SolverConfiguration {
    BackendKind backend = BackendKind::Auto;
    int batch_size = 1024;            // parallel starts; the unit of work on the GPU
    uint64_t seed = 1;
    double time_limit_seconds = 60.0;
    int64_t iteration_limit = 0;      // 0 = unlimited (gradient iterations)
    int64_t run_limit = 0;            // 0 = stop at the first certificate; N = complete N runs of the whole batch
                                      // and report every polish outcome (the per-restart measurement)
    SeedKind seed_kind = SeedKind::Ascent;
    int seed_steps = 200;             // gradient iterations of a run's seed, times luby(run); 0 = a uniform start
    int64_t polish_flips = 0;         // walk flips per slot of a run's polish, times luby(run); 0 = no walk
    RestartSchedule restart_schedule = RestartSchedule::Luby;   // fixed = every run at the unit budget (a fixed cutoff)
    int stall_patience = 0;           // resample a slot after this many non-improving iterations; 0 = off
    float rigorous_fraction = 0.0f;   // share of the batch walking Schoening's rule from uniform starts for 3n flips
    double prior_satisfiable = 0.5;   // pi, the prior P(SAT) of the instance's family
    double beta_prior_a = 0.4698;     // Beta(a, b) prior of a satisfiable instance's per-restart success (posterior.hpp),
    double beta_prior_b = 5.0207;     // fitted by moments on uf250-1065, uniform starts, 10n SKC flips at 4096 slots
                                      // (benchmark/seed_comparison.jsonl, 2026-08-29): PROVISIONAL, refit on your family
    StepParameters step;
    WalkParameters walk;
    TiltedParameters tilted;
    bool verbose = false;
};

}  // namespace multilinear_sat
