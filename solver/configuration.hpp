// Every tunable of the solver in one place. Defaults are the values the benchmark
// in benchmark/results.md was run with; the command line overrides any of them.
#pragma once
#include <cstdint>

namespace multilinear_sat {

enum class BackendKind { Cpu, Cuda, Auto };

struct StepParameters {
    float step_size = 0.1f;      // gradient step on the cube
    float momentum = 0.9f;       // heavy-ball momentum
    float kick_sigma = 0.3f;     // standard deviation of the Gaussian kick; 0 disables it
    bool focused_kick = true;    // kick only variables of clauses the rounded point violates
    float kick_decay = 1.0f;     // multiplies kick_sigma every iteration (1 = constant)
};

struct SolverConfiguration {
    BackendKind backend = BackendKind::Auto;
    int batch_size = 1024;            // parallel starts; the unit of work on the GPU
    uint64_t seed = 1;
    double time_limit_seconds = 60.0;
    int64_t iteration_limit = 0;      // 0 = unlimited
    int luby_unit = 200;              // restart cutoff = luby_unit * luby(k) iterations
    int stall_patience = 0;           // restart a slot after this many non-improving iterations; 0 = off
    StepParameters step;
    bool verbose = false;
};

}  // namespace multilinear_sat
