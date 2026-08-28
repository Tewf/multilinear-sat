# The method: batched descent on the multilinear relaxation, with certificates

## Objective

A point x lives in [-1, 1]^n, with +1 meaning true. A clause c of length k with literal
values l_i (the variable's coordinate, negated for a negative literal) has energy

    E_c(x) = -1 + 2^{1-k} * prod_{i in c} (1 - l_i)

which is +1 at a vertex falsifying the clause, -1 at a vertex satisfying it, and in between
equals the expected value under independent rounding. F(x) = sum_c E_c(x) is multilinear,
so its minimum over the cube is attained at a vertex and equals -m exactly when the formula
is satisfiable: the relaxation changes nothing about the optimum, it only supplies a gradient
(FourierSAT's formulation, see `../literature/review.md`). The gradient of one clause with
respect to one of its variables is -sign(l_i) 2^{1-k} prod_{j != i} (1 - l_j): no clause
product is ever divided, so the cube boundary costs nothing.

## One iteration, for a batch of B independent starts

    for every (slot, clause):        mark the clause violated by the rounded point sign(x)
    per slot:                        violated count = number of marked clauses
    for every (slot, variable):
        g  = sum over the variable's occurrences of the clause gradient (occurrence lists,
             no atomics, each thread recomputes its k-1 products)
        kick = sigma * N(0, 1) if the variable occurs in a violated clause (focused kick), else 0
        v  = momentum * v - step_size * g
        x' = clip(x + v + kick, -1, 1)          # written to the second buffer, then swapped

The rounded point is checked every iteration; a slot whose count is zero is a certificate
and the loop stops. The kick is WalkSAT's escape move without a discrete choice: only the
variables of violated clauses are perturbed. Random numbers are a pure function of
(seed, epoch, slot, coordinate) (splitmix64 then Box-Muller), so a run is reproducible from
its seed on the CPU and CUDA backends alike and no random state lives on the device.

## Restarts

Each slot restarts on the Luby, Sinclair, Zuckerman schedule: the k-th run of a slot lasts
`luby_unit * luby(k)` iterations (1, 1, 2, 1, 1, 2, 4, ...). Optionally a slot also restarts
after `stall_patience` iterations without improving its own best count. The universal
schedule is within a logarithmic factor of the best fixed cutoff without knowing the
run-length distribution, which is exactly what is unknown here.

## What the algorithm is, and its cost

It is a Las Vegas procedure for the promise problem "find a satisfying assignment of a
satisfiable formula": an answer is always certified, the running time is random, and it
never claims unsatisfiability (no continuous method certifies UNSAT on random 3-CNF:
Polynomial Calculus and Sum-of-Squares need degree Omega(n) there). With a time limit it
becomes one-sided Monte Carlo: SATISFIABLE is never wrong, UNKNOWN carries the error.

Cost per iteration: Theta(sum of clause lengths) per slot, Theta(B * 3 * m) for 3-CNF, with
B * (n + m) bytes of state. Expected time to a solution with restarts is
L * cost / p(n, alpha), where p is the probability that one start reaches a solution
within its cutoff L. The GPU divides wall-clock by B and does not touch p. No bound on p
is known for gradient dynamics on random 3-SAT (the discrete walks have proven bounds,
Schoning's (4/3)^n and PPSZ's 1.307^n, through coupling arguments that do not transfer),
and no paper reports p measured; `../benchmark/results.md` reports what this implementation
achieves against probSAT and CaDiCaL.

## Contribution

An embeddable native implementation of the FourierSAT-style relaxation (the public ones are
Python: vardigroup/FourierSAT on CPU, seeder-research/FastFourierSAT on JAX), with batched
Luby restarts, the focused-noise kick, a CPU backend for machines without a GPU, a test
suite that checks the gradient against exact finite differences and the two backends against
each other, and a benchmark that publishes the comparison whatever it shows. Not claimed: a
win on uniform random 3-SAT over probSAT or CDCL; the families where continuous methods are
reported to win (cardinality, XOR, weighted MaxCut) need the Fourier expansion of non-clause
constraints, which is the next version.
