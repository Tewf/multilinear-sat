# gaussian_surrogate

The Python research record of the objective study, in PyTorch, which asks one question of the continuous
relaxation: does the *variance* of the satisfied-clause count help gradient ascent find a
satisfying assignment, or is its mean enough? The C++ library in `../solver` does not depend on it; the origin and derivation are in `method/`, the
results in `findings.md`, `findings-tilted/` and `findings-fidelity.md`, and what the library then measured of the same
seeds is `../benchmark/findings-walk/`.

Variables x in {-1, 1}^n are relaxed to independent means p in [-1, 1]^n. For a clause j
with literals (i, s), U_j(p) = (1/8) prod (1 - s p_i) is the probability that it is
unsatisfied. For two clauses that share a variable, U_jk(p) is the probability that both are:
a shared variable with the same sign appears once (factor 2 (1 - s p_i) against the 1/64),
with opposite signs the pair can never be jointly unsatisfied (U_jk = 0). Then

    mu(p)  = m - sum_j U_j                                       expected satisfied clauses
    var(p) = sum_j U_j (1 - U_j) + sum_{j != k sharing} (U_jk - U_j U_k)
    F(p)   = Phi((mu - m + 1/2) / sqrt(max(var, 1e-6)))          Gaussian surrogate of P(all satisfied)

Three methods share one scaffolding (Adam, a batch of random restarts, rounding x = sign(p)
every K steps with a short WalkSAT/SKC polish of the best slot, a clause-by-clause check of
any SATISFIABLE before it is printed):

| `--obj` | maximises | point |
|---|---|---|
| `F` | log F | p = tanh(theta), theta free |
| `mu` | mu | p = tanh(theta), theta free |
| `fourier` | mu, which is FourierSAT's multilinear energy up to an affine map | x on the box [-1, 1]^n, clipped after each step |
| `tilted` | log E[exp(beta S)] by sampling (`../method/sampling-gradient-loop.md`), its own loop | p = tanh(theta), one theta per group of slots |

`mu` and `fourier` optimise the same function: FourierSAT's clause polynomial on +-1 with
independent means is exactly 1 - U_j. What separates them is the relaxation.

## Run

    conda activate flappy_bird                    # torch 2.13 + CUDA, numpy, pysat, pytest
    cd gaussian_surrogate
    python solve.py ../benchmark/instances/uf50-218/uf50-01.cnf --obj F --seed 0 \   # --obj tilted for the loop; every Configuration field is a flag
        --log-trajectory trajectory.csv          # --device cpu|cuda, --time-limit SECONDS
    python -m pytest tests -q                     # brute-force moments, reader, search, every method

Output is SAT-competition style: `c` lines (one of them `c json {...}` with the run's
statistics), then `s SATISFIABLE` and a `v` line (exit code 10) or `s UNKNOWN` (exit 0).
The trajectory CSV has one row per Adam step for restart slot 0: `step, restart, mu, var,
log_F, F, min_unsat_at_rounding`; mu, var and F are logged for every method (for the
baselines they are evaluated without gradient); the last column is the batch minimum on
rounding steps and NaN otherwise.

## Layout

| File | Role |
|---|---|
| `configuration.py` | every tunable, one dataclass; each field is a flag of the same name in `solve.py` |
| `dimacs.py` | DIMACS reader (SATLIB `%` trailer included) and the `Formula` tensors |
| `adjacency.py` | clause pairs sharing a variable, laid out for a vectorised U_jk |
| `moments.py` | U_j, U_jk, mu, var, batched over restarts |
| `objective.py` | log F from the moments, and the value record every objective returns |
| `baseline_objectives.py` | mu as the ascent target |
| `relaxation.py` | tanh(theta) and the clipped box: parameters to point, and projection |
| `methods.py` | the `--obj` names: objective x relaxation for the gradient methods, and the sampling loop |
| `rounding.py` | sign(p) and the vectorised / plain-Python violated-clause counts |
| `walksat.py` | the WalkSAT/SKC polish and its application to the best slot |
| `solver.py` | the restart loop, rounding checks, polish, trajectory log |
| `solve.py` | the command line |
| `sampling.py` | Bernoulli draws from means p, weights from log weights, effective sample size |
| `flip_kernel.py` | a local-search walk vectorised over slots (SKC or Schöning rule), true-literal counts by scatter |
| `annealing.py` | annealed importance sampling toward q_theta exp(beta S) over a Metropolis kernel |
| `tilted_gradient.py` | the tilted objective's ascent direction: sampled mean, MuProp control variate, closed form |
| `group_optimizers.py` | plain and Adam steps on theta per group with a decreasing step size, resettable per group |
| `luby.py` | the Luby sequence and one restart budget per group |
| `failure_record.py` | counts failed rigorous and heuristic restarts and evaluates the two posteriors |
| `posterior.py` | P(UNSAT | failures): Schöning's bound and the Beta-mixture posterior, with the moment fit |
| `tilted_loop.py` | the tilted sampling-gradient loop, `--obj tilted`: draws, move, weights, step, schedule, log |
| `experiments/` | the seed comparison, the posterior calibration and the tilted-mean bias table, each with its table writer |
| `tests/` | pytest: moments against enumeration of {-1,1}^n, the reader, the search |
| `benchmark/` | SATLIB download, the run over families x methods, and the results table |

## Two choices that are not tunables

**The ascent maximises log F, not F.** At a random start sum_j U_j is about m/8, so on
uf250-1065 the argument of Phi is z = (1/2 - sum U_j) / sigma of order -12. There torch's Phi
is exactly 0 from z = -10 on, and where it is not, its derivative (2e-32 at z = -12) is far below
Adam's epsilon: an ascent on F does not move. log Phi (`torch.special.log_ndtr`) has the same
maximiser and a derivative of order |z|. F itself is still computed and logged.

**The covariance sum runs over unordered pairs and is doubled.** The definition of var above
sums over ordered pairs (j, k); `adjacency.py` stores each pair once with j < k, and
`moments.py` multiplies the pair sum by 2. Pairs sharing no variable are independent and
contribute nothing.

## Scope

3-SAT only: the reader rejects any other clause length, duplicate or tautological literals.
Nothing is claimed that `benchmark/results.md` does not show.
