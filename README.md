# multilinear-sat

A SAT solver by continuous relaxation and batched local search: a C++20 library with a CUDA
backend and a CPU (OpenMP) backend that compute the same thing from the same seed. Each run
of the batch is a seed then a polish: thousands of slots start from a random point, all
false, a short projected gradient ascent on the multilinear (Fourier) energy of the formula,
or the tilted sampling loop, and then walk (WalkSAT/SKC, probSAT, Schöning or Metropolis)
from the rounded point, with restarts on the Luby schedule. Every answer is a certificate:
the solver reports SATISFIABLE only after checking that an assignment satisfies every row.
It never claims UNSAT; it reports two posteriors on it, numbers about the failed restarts
and never a verdict. Version 0.2 reads k-CNF (DIMACS) and XNF (`x` lines, odd parities): a
parity is one Walsh monomial in the energy and a toggle in the walk.

**What it does not claim.** On uniform random 3-SAT the gradient alone does not beat probSAT
or CaDiCaL (`benchmark/results.md`), and the walk is probSAT's algorithm, slower per chain
than probSAT's hand-tuned loop; what the batch buys, what each seed buys per restart, what
the posterior is worth against kissat, and what the native parity does on MM-Challenge-1 are
measured in `benchmark/findings-walk/`, whatever they show.

## What is here

| Directory | Role |
|---|---|
| `solver/`, `cli/`, `tests/` | the library (formula with parity rows, energies, hash randomness, the walk, the tilted seed, both backends, the run loop, the posteriors), its DIMACS and XNF command line, and the doctest suite |
| [`gaussian_surrogate/`](gaussian_surrogate/README.md) | the Python research record of the objective study: does the variance of the satisfied-clause count help the ascent (it lands closer and pays 3 to 86x per step), the tilted loop, the seeds priced with a launch-bound kernel; its findings in `findings.md`, `findings-tilted/` and `findings-fidelity.md` (no surrogate approximates the exact count; the seeds act through basin geometry) |
| [`literature/`](literature/README.md) | seven reviews, each a folder of thesis steps with verified references, and the index |
| [`method/`](method/README.md) | the method as built, the two design notes (the design as proposed), and `algorithm.md`, the surviving variant written as pseudocode with the number behind each choice |
| [`benchmark/`](benchmark/README.md) | every measurement with its provenance (command, seed, commit, binary hash, GPU state), the findings of the walk, and `arms/`: the variants priced on one protocol, the dominance front and the rejected arms with their numbers |

## Build

    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release          # CUDA backend if nvcc is found
    cmake --build build -j
    ctest --test-dir build --output-on-failure

`-DMULTILINEAR_SAT_CUDA=OFF` builds the CPU backend only. With a CUDA toolkit outside the
default path, pass `-DCMAKE_CUDA_COMPILER=/path/to/nvcc`. Requires CMake 3.24, a C++20
compiler, optionally OpenMP and CUDA 12. The Python record runs in any environment with
torch, numpy and pytest: `python -m pytest gaussian_surrogate/tests -q`.

## Use

    ./build/multilinear-sat instance.cnf --seed-kind uniform --polish-flips 2500    # the walk alone (probSAT's shape)
    ./build/multilinear-sat instance.cnf --seed-steps 200 --polish-flips 2500       # the ascent, then the walk
    ./build/multilinear-sat instance.xnf --seed-kind all-false --polish-flips 100000 --batch-size 1024
    # prints "c json {...}" with the run statistics, then "s SATISFIABLE" and "v ..." lines
    # (exit code 10) or "s UNKNOWN" (exit code 0)

`--run-limit N` completes N runs of the whole batch instead of stopping at the first
certificate and counts every polish outcome, which is how the per-restart success
probability is measured. `--rigorous-fraction X` makes a share of the batch walk Schöning's
rule from uniform starts for 3n flips; their failures feed the rigorous posterior, the
others' the Beta-mixture one. Every tunable lives in `solver/configuration.hpp` and has a
command-line flag of the same name.

From C++:

```cpp
#include "formula.hpp"
#include "solver.hpp"
using namespace multilinear_sat;
Formula formula = read_dimacs("instance.xnf");     // DIMACS or XNF; or make_formula(n, clauses, parities)
SolverConfiguration configuration;                 // every tunable, with its default
configuration.seed_kind = SeedKind::Uniform;       // Uniform, AllFalse, Ascent or Tilted
configuration.polish_flips = 2500;                 // walk flips per slot per run, times luby(run)
configuration.walk.walk_rule = WalkRule::ProbSat;  // Skc, ProbSat, Schoening or Metropolis
SolveResult result = solve(formula, configuration);
if (result.status == Status::Satisfiable) {
    // result.assignment[v] is +1 (true) or -1 (false) for variable v + 1
}
```

To embed it in another CMake project, `add_subdirectory(multilinear-sat)` (or FetchContent)
and `target_link_libraries(your_target PRIVATE multilinear_sat)`; the tests and the command
line are built only when this is the top-level project.

## Citation and licence

MIT. Cite the software (`CITATION.cff`) together with FourierSAT (Kyrillidis, Shrivastava,
Vardi, Zhang, AAAI 2020), whose relaxation this implements; the GPU line continues with
FastFourierSAT (Cen, Zhang, Fong, AAAI 2025), whose Corollary 2 is the parity gradient. The
walk's rules are WalkSAT/SKC (Selman, Kautz, Cohen 1994), probSAT (Balint, Schöning, SAT
2012) and Schöning's algorithm (FOCS 1999); the annealed weights are Neal's (2001). Third-party
notices in `NOTICE`. `README.fr.md` says the same in French.
