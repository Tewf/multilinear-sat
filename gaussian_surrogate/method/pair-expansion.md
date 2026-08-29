# The cluster expansion of log P(N = 0) and the pair objective

Notation as in [objective.md](objective.md); U_S = E[prod_{j in S} I_j], all of S unsatisfied.

## Inclusion and exclusion

prod_j (1 - I_j) = sum_S (-1)^|S| prod_{j in S} I_j over the subsets S of clauses, so

    P(N = 0) = 1 - sum_j U_j + sum_{j<k} U_jk - sum_{j<k<l} U_jkl + ...

Every U_S is closed-form: reduce the product of the indicators by x_i^2 = 1, a variable
shared by r clauses with the same sign giving (1 - s x)^r = 2^{r-1} (1 - s x), any opposite-sign
sharing giving 0; the result is multilinear, so U_S is its value at p (prod_j U_j if disjoint).

## Second order

Write a = sum_j U_j, b = sum_{j<k} U_jk, c = sum_{j<k<l} U_jkl. Then

    log P(N = 0) = log(1 - a + b - c + ...)
                 = (-a + b - c) - (-a + b)^2 / 2 + (-a)^3 / 3 + ...
                 = -a + b - a^2 / 2 + (third order in the U's).

Since a^2 = sum_j U_j^2 + 2 sum_{j<k} U_j U_k,

    log P(N = 0) = [ -sum_j U_j - (1/2) sum_j U_j^2 ] + sum_{j<k} (U_jk - U_j U_k) + ...
                 = sum_j log(1 - U_j) + sum_{j<k sharing} Cov(I_j, I_k) + (third order),

the bracket being sum_j log(1 - U_j) to second order and a non-sharing pair having
U_jk = U_j U_k. The first term is `logsum` (-lambda at first order), the second the covariance sum.

## The pair closure

With S_j = 1 - U_j and S_jk = 1 - U_j - U_k + U_jk = P(j and k both satisfied), the pair
objective of [open-directions.md](open-directions.md) is

    L_pair(p) = sum_j log S_j + sum_{j<k sharing} [ log S_jk - log S_j - log S_k ].

Since S_jk - S_j S_k = U_jk - U_j U_k = Cov(I_j, I_k), each bracket is
log(1 + Cov / (S_j S_k)) = Cov / (S_j S_k) + ..., so L_pair agrees with the expansion to second
order and differs at third: the Kirkwood superposition closure, the one-clause laws times
S_jk / (S_j S_k) on each sharing pair.

**Where it is exact, and where it is not.** For two clauses L_pair = log S_jk, exact. Not on a
chain of three: with j = (x or a or b), k = (x or y or u), l = (y or c or d) at p = 0,
enumeration gives P(all three satisfied) = 89/128 = 0.6953, the closure gives
S_jk S_kl / S_k = (25/32)^2 / (7/8) = 0.6975, the second-order expansion e^{3 log(7/8) + 2/64}
= 0.6912. The closure would be exact if I_j and I_l were independent given I_k, and they are
not: conditioning on k being satisfied correlates x and y. The exact object on a tree-shaped
factor graph is the Bethe free energy over variable and clause beliefs (Yedidia, Freeman and
Weiss, 2005), a different functional. What holds is that the error of L_pair is third order in
the U's, so it shrinks as the ascent drives the U_j down; small on sparse neighbourhoods is
expected, not proved here.

## Gradient and cost

For a literal (i, s) of clause j, while 1 - s p_i != 0,

    dU_j / dp_i = -s U_j / (1 - s p_i),      dU_jk / dp_i = -s U_jk / (1 - s p_i),

the second holding also for a shared same-sign variable (its factor 2 (1 - s p_i) has the
same ratio); where 1 - s p_i = 0 the product without that factor is used. With d_j the number
of clauses sharing a variable with j, L_pair = sum_j (1 - d_j) log S_j + sum_{j<k} log S_jk,
so dL_pair / dp_i runs over the clauses containing i and their sharing neighbours, the
traversal sigma^2 already makes. `pair` costs what F costs, without Phi.

## Properties

- A sum of logarithms of multilinear functions, so not multilinear: the vertex theorem of
  objective.md does not apply; interior maxima are an open question.
- L_pair = 0 at a satisfying vertex, but not bounded above by 0 in general: with d same-sign
  neighbours per clause and U_j = 1/8, a clause contributes (1 - d) log(7/8) + (d/2) log(25/32),
  positive from d = 14 on, the known defect of Kirkwood superposition; random signs largely cancel.
- dL_pair / dCov(I_j, I_k) = 1 / S_jk > 0: it rewards failures that co-occur, the Gaussian's
  appetite for variance in a linear and bounded form.

## Third order

The next term collects the connected triples of the clause graph (j sharing with k and k with
l, whether or not j and l share), each closed-form by the same reduction: at most
m (9 alpha)^2 / 2 of them, about 40 alpha^3 n, near 3000 n at alpha = 4.26, forty times the
pair count. Its size against the pair term says whether truncating at pairs is adequate.
