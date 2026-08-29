# multilinear-sat

A SAT solver by continuous relaxation and batched local search, written in C++20 with a
CUDA backend and a CPU (OpenMP) backend that compute the same thing from the same seed.
Each run of the batch is a seed then a polish: thousands of slots start from a random point,
all false, a short projected gradient ascent on the multilinear (Fourier) energy of the
formula, or the tilted sampling loop, and then walk (WalkSAT/SKC, probSAT, Schöning or
Metropolis) from the rounded point, on the Luby schedule. Every answer is a certificate: the
solver reports SATISFIABLE only after checking that an assignment satisfies every row. It
never claims UNSAT; it reports two posteriors on it, numbers about the failed restarts and
never a verdict.

Version 0.2 handles k-CNF (DIMACS) and XNF (`x` lines, odd parities, the format cnf2xnf and
xnfSAT read): a parity is one Walsh monomial in the energy and a toggle in the walk. It is a
library first (a static library with no Python runtime, made to be linked into other C++
code), with a command line for measuring.

**What it does not claim.** On uniform random 3-SAT the gradient alone does not beat probSAT
or CaDiCaL (`benchmark/results.md`), and the walk is the same algorithm as probSAT's, so
per chain it is slower than probSAT's hand-tuned loop; what the batch buys, what each seed
buys per restart, what the posterior is worth against kissat, and what the native parity
does on the MM-Challenge-1 instances are all measured in `findings-walk.md`, whatever they
show. See `literature/review.md` for who did what before this, and `method/README.md` for
the algorithm and its cost.

## Build

    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release          # CUDA backend if nvcc is found
    cmake --build build -j
    ctest --test-dir build --output-on-failure

`-DMULTILINEAR_SAT_CUDA=OFF` builds the CPU backend only. With a CUDA toolkit outside the
default path, pass `-DCMAKE_CUDA_COMPILER=/path/to/nvcc`. Requires CMake 3.24, a C++20
compiler, optionally OpenMP and CUDA 12.

## Use

    ./build/multilinear-sat instance.cnf --time-limit 60 --backend cuda            # the ascent alone, as in 0.1
    ./build/multilinear-sat instance.cnf --seed-kind uniform --polish-flips 2500    # the walk alone (probSAT's shape)
    ./build/multilinear-sat instance.cnf --seed-steps 200 --polish-flips 2500       # the ascent, then the walk
    ./build/multilinear-sat instance.xnf --seed-kind all-false --polish-flips 100000 --batch-size 1024
    # prints "c json {...}" with the run statistics, then "s SATISFIABLE" and "v ..." lines
    # (exit code 10) or "s UNKNOWN" (exit code 0)

`--run-limit N` completes N runs of the whole batch instead of stopping at the first
certificate and counts every polish outcome, which is how the per-restart success
probability in `findings-walk.md` is measured. `--rigorous-fraction X` makes a share of the
batch walk Schöning's rule from uniform starts for 3n flips; their failures feed the rigorous
posterior in the json line, the others' the Beta-mixture one.

From C++:

```cpp
#include "formula.hpp"
#include "solver.hpp"
using namespace multilinear_sat;
Formula formula = read_dimacs("instance.xnf");     // DIMACS or XNF; or make_formula(n, clauses, parities)
SolverConfiguration configuration;                 // every tunable, with its default
configuration.seed_kind = SeedKind::Ascent;        // Uniform, AllFalse, Ascent or Tilted
configuration.seed_steps = 200;                    // gradient iterations per run, times luby(run)
configuration.polish_flips = 2500;                 // walk flips per slot per run, times luby(run)
configuration.walk.walk_rule = WalkRule::ProbSat;  // Skc, ProbSat, Schoening or Metropolis
SolveResult result = solve(formula, configuration);
if (result.status == Status::Satisfiable) {
    // result.assignment[v] is +1 (true) or -1 (false) for variable v + 1
}
```

Every tunable (batch size, step size, momentum, kick, seed kind and steps, polish flips, walk
rule and its constants, rigorous fraction, the priors, the tilted loop's schedule, seed) lives
in `solver/configuration.hpp` and has a command-line flag of the same name.

To embed it in another CMake project, `add_subdirectory(multilinear-sat)` (or FetchContent)
and `target_link_libraries(your_target PRIVATE multilinear_sat)`; the tests and the command
line are built only when this is the top-level project.

## Layout

| directory | role |
|---|---|
| `solver/` | the library: formula with parity rows, energies, hash randomness, the walk's bookkeeping and rules, the tilted seed, CPU and CUDA backends, the run loop's phases, the posteriors |
| `cli/` | the DIMACS and XNF command line |
| `tests/` | doctest suite: parser, energy and gradient (exact finite differences, parities too), randomness, Luby, walk bookkeeping against recounts, every rule against the checker, Schöning's rate, brute force on tiny XNFs, posteriors, tilted mean by enumeration, backend agreement |
| `benchmark/` | instance generator, baseline build script, the 0.1 harness and `results.md`, and the walk's four measurements with their records (`walk_throughput`, `seed_comparison`, `posterior_calibration`, `parity_challenge`) |
| `method/` | the algorithm, its pseudocode, cost and Las Vegas framing |
| `literature/` | the review and `references.bib` |
| `findings-walk.md` | what the walk, the seeds, the posterior and the parities measured |

## Citation and licence

MIT. Cite the software (`CITATION.cff`) together with FourierSAT (Kyrillidis, Shrivastava,
Vardi, Zhang, AAAI 2020), whose relaxation this implements; the GPU line continues with
FastFourierSAT (Cen, Zhang, Fong, AAAI 2025), whose Corollary 2 is the parity gradient. The
walk's rules are WalkSAT/SKC (Selman, Kautz, Cohen 1994), probSAT (Balint, Schöning, SAT
2012) and Schöning's algorithm (FOCS 1999); the annealed weights are Neal's (2001). Third-party
notices in `NOTICE`.
