# The method: batched seed and polish on the multilinear relaxation, with certificates

## Objective

A point x lives in [-1, 1]^n, with +1 meaning true. A clause c of length k with literal
values l_i (the variable's coordinate, negated for a negative literal) has energy

    E_c(x) = -1 + 2^{1-k} * prod_{i in c} (1 - l_i)

which is +1 at a vertex falsifying the clause, -1 at a vertex satisfying it, and in between
equals the expected value under independent rounding. An odd parity over k literals (an XNF
`x` line) is one Walsh monomial,

    E_x(x) = (-1)^k * prod_{i in x} l_i,

with the same three properties. F(x) = sum of the rows is multilinear, so its minimum over
the cube is attained at a vertex and equals -m exactly when the formula is satisfiable: the
relaxation changes nothing about the optimum, it only supplies a gradient (FourierSAT's
formulation, see `../literature/review.md`). The gradient of a clause with respect to one of
its variables is -sign(l_i) 2^{1-k} prod_{j != i} (1 - l_j), that of a parity the product
without one factor (FastFourierSAT, Corollary 2): no row product is ever divided, so the
cube boundary costs nothing, and a parity costs O(k) with no transform.

## One gradient iteration, for a batch of B independent slots

    for every (slot, row):           mark the row violated by the rounded point sign(x)
    per slot:                        violated count = number of marked rows
    for every (slot, variable):
        g  = sum over the variable's occurrences of the row gradient (occurrence lists,
             no atomics, each thread recomputes its k-1 products)
        kick = sigma * N(0, 1) if the variable occurs in a violated row (focused kick), else 0
        v  = momentum * v - step_size * g
        x' = clip(x + v + kick, -1, 1)          # written to the second buffer, then swapped

The rounded point is checked every iteration; a slot whose count is zero is a certificate
and the loop stops. The kick is WalkSAT's escape move without a discrete choice: only the
variables of violated rows are perturbed.

## One walk step, for the same batch

Each slot holds an assignment, the true-literal count of every row, and the violated rows as
a list with each row's position in it (probSAT's pair), so a violated row is drawn in O(1)
and a flip costs O(occurrences of the variable). A step draws a violated row uniformly and a
variable of it by the rule: `skc` (a zero-break variable if any, else with probability
walk_noise a uniform one, else the first minimum break), `probsat` (weight (eps + break)^-cb,
2.06 and 0.9 for 3-SAT), `schoening` (uniform); `metropolis` instead proposes a uniform
variable of the formula and accepts with min(1, exp(beta (make - break))). A parity breaks
when satisfied and makes when violated, whichever of its variables flips. The two
real-valued rules draw from integer tables, so the CPU and CUDA walks agree bit for bit.
Random numbers are a pure function of (seed, stream, epoch, slot, coordinate), three streams
(restart, kick, walk), splitmix64 then Box-Muller for the Gaussian.

## Runs, seeds and the Luby schedule

Run k of the batch is `seed_steps * luby(k)` gradient iterations, or none, then
`polish_flips * luby(k)` walk steps per slot, in launches of `walk_flips_per_launch` with the
certificate check between them; then every slot restarts (Luby, Sinclair, Zuckerman 1993:
1, 1, 2, 1, 1, 2, 4, ...). The walk starts from the rounding of the ascent's point
(`ascent`), the rounding of the slot's fresh random point (`uniform`), all false
(`all-false`, xnfSAT's default), or a draw of the tilted loop's final q_theta (`tilted`,
[walk-and-posterior.md](walk-and-posterior.md)). With `run_limit` the batch completes N runs
whatever it finds, and the fraction of slots satisfied at the end of a polish is the
per-restart success probability p; expected time to a solution is cost per restart / p.

The rigorous half, the two posteriors, the tilted seed and the cost of each part:
[walk-and-posterior.md](walk-and-posterior.md). What all of it measures, whatever it shows:
[../benchmark/findings-walk/](../benchmark/findings-walk/README.md).

## Contribution

An embeddable native implementation of the FourierSAT-style relaxation with the discrete
polish the literature's record holders use, from one set of inline functions on both
backends, with tests for every closed form (gradients against exact finite differences,
walk counts against recounts and the independent checker, the tilted mean against
enumeration, the posteriors against their formulas) and measurements that are published with
the commands, seeds and binary hashes that produced them. Not claimed: a win on uniform
random 3-SAT over probSAT or CDCL, or on Brent equations over xnfSAT; the tables say what
each part buys per restart and per second.
