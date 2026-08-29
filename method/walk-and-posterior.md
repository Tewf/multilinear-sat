# The Las Vegas framing: the rigorous half, the posteriors, the tilted seed, the cost

## What the algorithm is

A Las Vegas procedure for the promise problem "find a satisfying assignment of a satisfiable
formula": an answer is always certified (the checker in the solver loop, independent of the
backends, rejects a lying backend), the running time is random, and it never claims
unsatisfiability. With a time limit it becomes one-sided Monte Carlo: SATISFIABLE is never
wrong, UNKNOWN carries the error. No continuous method certifies UNSAT on random 3-CNF
(Polynomial Calculus and Sum-of-Squares need degree Omega(n) there), and a confidence that
grows meaningfully in polynomial time on every instance would put SAT in RP, hence NP = RP.

## The rigorous half

A `rigorous_fraction` of the batch ignores the seed: those slots start uniformly at random
and walk Schöning's rule for 3n steps every run. Schöning (FOCS 1999) proves that one such
try satisfies a satisfiable 3-CNF with probability within a polynomial factor of (3/4)^n
and leaves the polynomial unwritten; `solver/posterior.hpp` derives it from his ballot
inequality, p >= (3/4)^n / (3 (3n + 1)), so that after K failed rigorous tries
P(no solution seen | SAT) <= (1 - p)^K, one-sided and valid for every 3-CNF. At n = 250 the
bound is 2.7e-35 per try and the posterior cannot move: the rigorous half is the reason the
other posterior is not a proof, stated once. It is refused on parities and on clauses longer
than three, where the bound does not apply.

## The posteriors

With a prior pi = P(SAT) for the instance's family and S the probability of the observed
failures given SAT, P(UNSAT | failures) = (1 - pi) / ((1 - pi) + pi S). The rigorous
posterior takes S = (1 - p)^K from the bound above. The Beta-mixture posterior takes the
heuristic slots' k failed polishes and a Beta(a, b) prior on a satisfiable instance's
per-restart success probability, fitted by moments on the family (the seed comparison's
uniform arm), so that S = B(a, b + k) / B(a, b), exact for the mixture and instance-adaptive.
Both are reported in the `c json` line and in the verbose run lines, and neither ever turns
the status into UNSAT; [../benchmark/findings-walk/posterior.md](../benchmark/findings-walk/posterior.md) gives the reliability curve on uf250-1065
against uuf250-1065 and the time to 0.99 against kissat's refutation.

## The tilted seed

Groups of slots share a natural parameter vector theta, p = tanh theta. Each step draws the
group's slots from the product measure q_theta, runs an annealed-importance-sampling ladder
of 2n Metropolis proposals toward q_theta exp(beta S) (S the satisfied-row count; a uniform
variable accepted with min(1, exp(beta_k dS - 2 theta_i x_i)), log weights summed along the
ladder), and steps theta by the self-normalised weighted mean of the samples minus p, which
is the exact ascent direction of log E_theta[exp(beta S)] (the identity of
[sampling-gradient-loop.md](sampling-gradient-loop.md), checked in the Python record by enumeration and
here by `tests/test_tilted.cpp`). The step decreases as eta_0 / (1 + t / half_life), beta
rises by a factor while the effective sample size holds above a floor, groups restart on the
Luby schedule in steps, and no control variate is used. After the seed steps a fresh draw
from q_theta is the walk's start.

## Cost

Per slot, a gradient iteration is Theta(sum of row lengths); a walk step is Theta(sum of the
occurrence counts of the row's variables) for the rules that read break counts, once for
`schoening`, twice for `probsat`; a ladder rung costs one flip effect and at most one flip.
State is B * (n + m) floats for the gradient and B * (n + 9m) bytes for the walk. Expected
time to a solution with restarts is cost per restart / p, where p is the per-restart success
probability of the seed and the polish together; the GPU divides the cost by the batch and
does not touch p, which is why the seed comparison reports p and cost separately.
