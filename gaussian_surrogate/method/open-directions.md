# Open directions

Nothing on this page is built. Each item is stated so that it can be built as one more
`--obj` on the same loop, or rejected on paper.

## A ladder of objectives

The Gaussian surrogate combines two ingredients — the pair probabilities U_jk and a normal
tail — and the benchmark cannot tell which one earns its cost. A ladder would:

    mu       sum_j (1 - U_j)                                 first order, no pairs
    logsum   sum_j log (1 - U_j)                             exact top coefficient of G(z)
    pair     sum_j log S_j + sum_{j<k sharing} [ log S_jk - log S_j - log S_k ]
    F        Phi( (1/2 - sum_j U_j) / sigma )               pairs, through a normal tail

with S_j = 1 - U_j and S_jk = 1 - U_j - U_k + U_jk = P(both satisfied).

`logsum` is log prod_j (1 - U_j): the probability that all clauses are satisfied if the clauses
were independent, which is also the top coefficient of the generating function in
[origin.md](origin.md) and the author's "log-sum" salvage direction. It needs no product tree.

`pair` is the pair (Kirkwood, or Bethe) approximation of P(all satisfied): the joint law of the
indicators is approximated by the product of the one-clause laws times a correction factor
S_jk / (S_j S_k) for each dependent pair. It is exact when the dependency graph is a tree, its
first-order expansion is `logsum`, and its second-order term is the same covariance
U_jk - U_j U_k that sigma^2 uses — but as an additive log-probability with a bounded, Poisson-
like tail, and without Phi or a division by sigma. If `pair` matches or beats `F`, the gain of
F comes from the pair information; if it does not, it comes from the Gaussian's appetite for
variance (point 2 of [objective.md](objective.md)).

## The count distribution

The Poisson-binomial law of the satisfied count under clause independence is computable in
O(m log^2 m) by inverting G(z). Comparing its P[N = m] — which is `logsum`, so the inversion
is only needed for the rest of the law — with the Gaussian F and with the truth by
enumeration on small instances would put a number on what the normal approximation costs.

## A correction to one proposed direction

The author's notes list a tempered objective E[exp(beta S)], annealed in beta, as closed-form
under the product measure. It is not: exp(beta S) = prod_j (1 + (e^beta - 1)(1 - I_j)) is a
product over dependent clauses, the same object as P(all satisfied) — which it becomes as
beta -> infinity — and its expectation expands over all subsets of clauses. It is closed-form
only if the clauses are treated as independent, which is `logsum` again.

## Further directions from the author's notes

- Higher cumulants from clause triples sharing variables, the next dependence correction.
- Correlated parameterisations of p (a latent variable, an autoregressive model), where
  sampling becomes necessary and the method becomes variational annealing.
- Survey Propagation marginals as a warm start or as a correlated parameterisation for the
  gradient step: the gap the author identified between message passing and continuous
  optimisation.
- Constraints other than clauses (XOR, cardinality), where continuous methods have their
  documented wins and where the product-tree FFT of FastFourierSAT is needed; the C++ library
  in `../../solver` is where that would go.
