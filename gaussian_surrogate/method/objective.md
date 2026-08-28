# The objective as built

## Setting

x in {-1, 1}^n, +1 meaning true, relaxed to independent x_i with E[x_i] = p_i in (-1, 1),
p = tanh(theta) in the code. Clause j is a set of literals (i, s), satisfied when some s x_i = +1.

## One clause

P(x_i = -s) = (1 - s p_i)/2, and the literals of a clause are distinct variables, so

    U_j(p) = P(clause j unsatisfied) = (1/8) prod_{(i,s) in C_j} (1 - s p_i).

This is the expectation of the indicator (1/8) prod (1 - s x_i), which is multilinear, so the
expectation is the polynomial at p. FourierSAT's clause polynomial is 1 - U_j.

## Two clauses

The indicator that j and k are both unsatisfied is (1/64) prod_{C_j} (1 - s x_i) prod_{C_k}
(1 - s' x_i). When a variable is shared the product is not multilinear; reduce it with
x_i^2 = 1:

    same sign      (1 - s x)^2      = 1 - 2 s x + x^2 = 2 (1 - s x)
    opposite sign  (1 - s x)(1 + s x) = 1 - x^2       = 0

After the reduction the product is multilinear again and its expectation is its value at p:

    U_jk(p) = (1/64) prod over the variables of C_j ∪ C_k of
                2 (1 - s p_i)   if shared with the same sign,
                0 for the whole product if any variable is shared with opposite signs,
                (1 - s p_i)     otherwise.

`adjacency.py` lays this out as six (variable, sign) slots per pair (the three of j and the
three of k, with k's shared slots padded to a factor of 1) and one scalar per pair,
2^(number of same-sign shared variables) / 64, or 0. A pair sharing two variables follows the
same rule; two identical clauses give U_jk = U_j. Clauses sharing nothing have U_jk = U_j U_k.

## Mean and variance of the satisfied count

Let I_j be the indicator that clause j is unsatisfied, N = sum_j I_j and S = m - N. Then

    mu(p)      = E[S]   = m - sum_j U_j
    sigma^2(p) = Var[N] = sum_j U_j (1 - U_j) + sum_{j != k} (U_jk - U_j U_k),

and only pairs sharing a variable contribute to the second sum. `moments.py` sums over
unordered pairs j < k and doubles. Both quantities are checked against enumeration of
{-1, 1}^n for n <= 10 in `tests/test_moments.py`, including same-sign, opposite-sign and
doubly-shared pairs.

## The surrogate

The I_j are dependent only through shared variables: the dependency graph is the
clause-variable graph, and in uniform random 3-SAT at ratio alpha a clause shares a variable
with about 9 alpha others, a bounded neighbourhood in a graph of m = alpha n nodes. Under such
local dependence the sum is approximately normal (Chen and Shao, 2004). With a continuity
correction, P(S = m) = P(S >= m - 1/2) is approximated by

    F(p) = Phi( (mu - m + 1/2) / sigma ) = Phi( (1/2 - sum_j U_j) / sigma ).

Two implementation facts. The ascent maximises log F (`torch.special.log_ndtr`): at a random
start sum_j U_j is about m/8, so on uf250-1065 z is of order -12; in float32 torch's `ndtr`
returns exactly 0 from z = -10 on and its derivative at z = -12 is 2e-32, below Adam's epsilon
of 1e-8, so an ascent on F itself does not move, while log Phi has the same maximiser and
derivative |z| there. And sigma^2 is floored at 1e-6 before the square root: it vanishes when
p saturates.

## What the function says about itself

Each point below is a property of the formula, not a measurement.

1. F is not multilinear (Phi of a ratio of two multilinear polynomials, one under a square
   root), so the theorem that a multilinear polynomial attains its maximum at a vertex does
   not apply. Interior local maxima are possible in principle; whether they occur on random
   3-SAT is not known here.
2. With z = (1/2 - sum U_j)/sigma, dF/dsigma = -phi(z) z / sigma, positive while z < 0. Until
   sum_j U_j falls below 1/2 the ascent rewards a larger variance: for a fixed mean, more
   mass at N = 0 needs more spread, which means making clause failures co-occur. The
   preference flips sign exactly when sum_j U_j < 1/2.
3. Near a solution N is a small count, closer to Poisson than to normal, and the Gaussian tail
   is the wrong law there. F is a guide for the ascent, not a calibrated probability.

Which of these matters in practice is what the benchmark measures.
