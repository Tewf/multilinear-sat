# Which approximation of P(N = 0), under which conditions

Notation as in [objective.md](objective.md): I_j is the indicator that clause j is unsatisfied,
U_j = E[I_j], N = sum_j I_j, lambda = sum_j U_j = E[N], sigma^2 = Var N, and z = lambda / sigma
is the distance from the mean of N to 0 in standard deviations. The target of the ascent is
P(N = 0). Which law approximates it depends on where p is, and every indicator below is
computable from the U_j and U_jk the code already evaluates.

## Where the ascent starts

At p = 0 every factor 1 - s p_i is 1, so U_j = 1/8 and lambda = m/8. The diagonal of the
variance is sum_j U_j (1 - U_j) = 7m/64. For two clauses sharing one variable with the same
sign, U_jk = 2/64 against U_j U_k = 1/64, a covariance of +1/64; with opposite signs U_jk = 0,
a covariance of -1/64. A clause shares a variable with about 9 alpha others, of both kinds
under random signs, so the covariance sum is small against the diagonal (on uf250-01 it is
+8.6 against 116.5) and

    sigma^2 = 7m/64 = 0.109 m,    z = (m/8) / (0.33 sqrt(m)) = 0.38 sqrt(m),

which is 11.9 on uf250-01 (lambda = 133.1, sigma^2 = 125.1). The event N = 0 sits z standard
deviations from the mean with z large: a large-deviation event, of probability of order
e^{-lambda}. A central limit theorem for this locally dependent sum (Chen and Shao, 2004)
comes with an error of order 1/sqrt(m) in the absolute scale, which says nothing about a
probability of order e^{-m/8}: the normal law describes deviations of order sigma. The point
0 enters that range only once lambda is a few units, and there N is a small count, closer to
Poisson than to normal.

## Three regimes

**Large deviation, z >> 1.** The whole ascent until lambda is a few units. The right object is
the cluster expansion of log P(N = 0), whose second order is the pair objective of
[pair-expansion.md](pair-expansion.md).

**Poisson, lambda of order 1 with weak dependence.** P(N = 0) is about e^{-lambda}, so the
objective is -lambda, which is mu up to the constant m. The error is certified by Arratia,
Goldstein and Gordon (1989, Theorem 1). Let B_j be the set of clauses sharing a variable with
j, j included. Under the product measure I_j is a function of the variables of C_j alone, and
every clause outside B_j is a function of other, independent variables, so I_j is independent
of {I_k : k not in B_j} and the theorem's third term b_3 is zero. Then

    |P(N = 0) - e^{-lambda}| <= (1 - e^{-lambda}) / lambda * (b_1 + b_2),
    b_1 = sum_j sum_{k in B_j} U_j U_k,    b_2 = sum_j sum_{k in B_j, k != j} U_jk,

both over ordered pairs. They are the quantities sigma^2 is built from.

**Central limit, z of order 1 and N large.** The Gaussian F with its continuity correction.
Its first Edgeworth correction is the test of validity: with gamma = kappa_3 / sigma^3 and
z' = (1/2 - lambda) / sigma,

    P(N <= 0) = Phi(z') - phi(z') (gamma / 6) (z'^2 - 1) + ...,

and in the tail (z' <= -2, where Phi(z') is about phi(z') / |z'|) the correction is small
against the leading term when |gamma| |z'|^3 << 6. For a sparse count the cumulants are close
to a Poisson law's, kappa_3 and sigma^2 both about lambda, so gamma is about lambda^{-1/2} and
|z'| about sqrt(lambda), and the condition reads lambda << 6: the normal tail is admissible
only when the expected number of unsatisfied clauses is a few units, which is the Poisson
regime, where e^{-lambda} is available directly. On the way in there is no window in which the
Gaussian is the right law, and its error has a definite sign: for N ~ Poisson(lambda),
log Phi(z') = -z'^2 / 2 - log(|z'| sqrt(2 pi)) + o(1) with z'^2 = lambda - 1 + 1/(4 lambda), so
log F is about -lambda / 2 against the true -lambda, half the slope, an overestimate of
P(N = 0) by a factor of order e^{lambda / 2}.

## One generating function behind the three

The cumulant-generating function of N ties the three laws together and says what the
Gaussian was implicitly doing: [tilted-objective.md](tilted-objective.md).

## Decision rule

| regime | indicator | objective | cost | caveat |
|---|---|---|---|---|
| large deviation | z >> 1, all of the way in | pair expansion | 3m factors and the pairs | truncation error is the third-order term |
| Poisson | lambda of order 1, b_1 + b_2 << lambda | -lambda (mu) or sum log(1 - U_j) | 3m factors | certified by the bound above |
| central limit | z of order 1, N large | Gaussian with correction | pairs and Phi | needs lambda << 6, where Poisson already holds |

The count is a large-deviation object for the whole ascent. The pair expansion is the
second-order object in that regime and its Poisson limit is the mu objective, so it degrades
gracefully as lambda falls. The Gaussian's useful content is its appetite for variance, which
the tilted form makes explicit and tunable through beta; whether a beta schedule matches or
beats the correction's implicit one is conjecture until measured.
