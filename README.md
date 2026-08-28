# multilinear-sat

A SAT solver by continuous relaxation, written in C++20 with a CUDA backend and a CPU
(OpenMP) backend that compute the same thing from the same seed. Each clause becomes its
multilinear (Fourier) energy on the cube [-1, 1]^n; thousands of random starts descend on
the sum in parallel, with momentum, a noise kick focused on the variables of violated
clauses, and Luby restarts per start. Every answer is a certificate: the solver reports
SATISFIABLE only after checking that a rounded point satisfies every clause. It never claims
UNSAT.

Version 0.1 handles k-CNF (DIMACS). It is a library first (a static library with no Python
runtime, made to be linked into other C++ code), with a command line for measuring.

**What it does not claim.** On uniform random 3-SAT it does not beat probSAT or CaDiCaL;
`benchmark/results.md` shows the measured comparison. Continuous relaxations are reported to
win where CNF encodings hurt (cardinality, XOR, weighted MaxCut); those constraint types are
the next version. See `literature/review.md` for who did what before this, and
`method/README.md` for the algorithm and its cost.

## Build

    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release          # CUDA backend if nvcc is found
    cmake --build build -j
    ctest --test-dir build --output-on-failure

`-DMULTILINEAR_SAT_CUDA=OFF` builds the CPU backend only. With a CUDA toolkit outside the
default path, pass `-DCMAKE_CUDA_COMPILER=/path/to/nvcc`. Requires CMake 3.24, a C++20
compiler, optionally OpenMP and CUDA 12.

## Use

    ./build/multilinear-sat instance.cnf --time-limit 60 --backend cuda
    # prints "c json {...}" with the run statistics, then "s SATISFIABLE" and "v ..." lines
    # (exit code 10) or "s UNKNOWN" (exit code 0)

From C++:

```cpp
#include "formula.hpp"
#include "solver.hpp"
using namespace multilinear_sat;
Formula formula = read_dimacs("instance.cnf");     // or make_formula(n, clauses)
SolverConfiguration configuration;                 // every tunable, with its default
configuration.time_limit_seconds = 10.0;
SolveResult result = solve(formula, configuration);
if (result.status == Status::Satisfiable) {
    // result.assignment[v] is +1 (true) or -1 (false) for variable v + 1
}
```

Every tunable (batch size, step size, momentum, kick, Luby unit, seed) lives in
`solver/configuration.hpp` and has a command-line flag of the same name.

## Layout

| directory | role |
|---|---|
| `solver/` | the library: formula, shared inline math, CPU and CUDA backends, the restart loop |
| `cli/` | the DIMACS command line |
| `tests/` | doctest suite: parser, energy and gradient (exact finite differences), randomness, Luby, solver, backend agreement |
| `benchmark/` | instance generator, baseline build script, harness, `results.md` with provenance |
| `method/` | the algorithm, its pseudocode, cost and Las Vegas framing |
| `literature/` | the review and `references.bib` |

## Citation and licence

MIT. Cite the software (`CITATION.cff`) together with FourierSAT (Kyrillidis, Shrivastava,
Vardi, Zhang, AAAI 2020), whose relaxation this implements; the GPU line continues with
FastFourierSAT (Cen, Zhang, Fong, AAAI 2025). Third-party notices in `NOTICE`.
