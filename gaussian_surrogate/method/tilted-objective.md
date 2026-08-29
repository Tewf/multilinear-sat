# One generating function behind the three laws, and the tilted objective

Notation as in [regimes.md](regimes.md).

## The generating function

K(t) = log E[e^{-tN}] = sum_{n >= 1} kappa_n (-t)^n / n!, and since N is a non-negative integer,
P(N = 0) = lim_{t -> infinity} E[e^{-tN}]. The Gaussian keeps kappa_1 and kappa_2, a quadratic K
with no point mass at 0 (hence the continuity correction). The Poisson sets every
kappa_n = lambda: K(t) = lambda (e^{-t} - 1), whose limit is -lambda. The saddlepoint
approximation (Daniels, 1954; Lugannani and Rice, 1980, for tail probabilities) uses all of K
and reduces to the normal law when K is quadratic. The cluster expansion of
[pair-expansion.md](pair-expansion.md) expands the limit itself.

## What the Gaussian was doing

The same view says what the Gaussian was doing. The tilted objective
log E[e^{beta S}] = beta mu + beta^2 sigma^2 / 2 + O(beta^3), truncated at second order, is the
mean-variance objective mu + (beta / 2) sigma^2, a Plefka-type expansion around the product
measure (1982), whose second order is the TAP correction in the spin-glass case. F
ascends in the direction of that objective for one value of beta: the ratio of the
sigma-derivative to the mu-derivative of log Phi(z') is (lambda - 1/2) / sigma exactly, and
for mu + (beta / 2) sigma^2 it is beta sigma, so

    beta_eff = (lambda - 1/2) / sigma^2,

a match of directions at the current point, not an identity. It is positive while
lambda > 1/2 (the ascent rewards variance) and crosses zero at lambda = 1/2: point 2 of
objective.md restated, the continuity correction being the schedule of beta.

