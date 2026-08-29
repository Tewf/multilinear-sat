// Every tunable of the solver in one place. Defaults are the values the benchmark
// in benchmark/results.md was run with; the command line overrides any of them.
#pragma once
#include <cstdint>

namespace multilinear_sat {

enum class BackendKind { Cpu, Cuda, Auto };
enum class SeedKind { Uniform, AllFalse, Ascent };            // where each run's walk starts
enum class WalkRule { Skc, ProbSat, Schoening, Metropolis };  // how the walk picks a variable

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
    int stall_patience = 0;           // resample a slot after this many non-improving iterations; 0 = off
    float rigorous_fraction = 0.0f;   // share of the batch walking Schoening's rule from uniform starts for 3n flips
    double prior_satisfiable = 0.5;   // pi, the prior P(SAT) of the instance's family
    double beta_prior_a = 1.0;        // Beta(a, b) prior of a satisfiable instance's per-restart success; (1, 1)
    double beta_prior_b = 1.0;        // until fitted on the family (posterior.hpp)
    StepParameters step;
    WalkParameters walk;
    bool verbose = false;
};

}  // namespace multilinear_sat
