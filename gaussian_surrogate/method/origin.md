# Origin of the objective

Condensed from the author's working notes (August 2026); the derivations are re-done in
[objective.md](objective.md).

## From Las Vegas algorithms to a relaxation

The thread began with Las Vegas algorithms, always correct and random in their running time,
and the classical randomised SAT solvers in that class: Papadimitriou's random walk for 2-SAT,
Schöning's (4/3)^n walk for 3-SAT, then WalkSAT and probSAT, which flip variables of violated
clauses. From there it reached FourierSAT (Kyrillidis, Shrivastava, Vardi and Zhang, 2020):
encode x_i in {-1, 1}, write each clause indicator as a multilinear (Walsh-Fourier) polynomial,
relax the cube's vertices to the cube, and maximise the sum of clause polynomials by
box-constrained gradient ascent. Its strength is hybrid instances (clauses with XOR and
cardinality constraints), where the working notes credited it with a product-tree FFT for
symmetric constraints. FourierSAT has none (it expands prod_i (a_i + t) directly, in O(k^2));
the FFT is FastFourierSAT's (2025), a batched length-(k+1) DFT whose gain is parallel, and a
parity needs no transform at all, being a single Walsh monomial
(`../../literature/fft-walksat-las-vegas/4-positioning.md`).

Three observations from that stage carried over. The relaxation is a probability, not a
device: for a multilinear f and independent x_i with means y_i, E[f(x)] = f(y) exactly. The
±1 encoding and a Bernoulli encoding are the same thing under y = 2p - 1. And production SAT
solving is CDCL; continuous methods are incomplete and never certify UNSAT, so their place is
research, and the open gap the author named is combining correlated marginals of the Survey
Propagation kind with gradient machinery.

## The Bernoulli proposal and what scrutiny kept

The proposal was to build the objective from the probabilistic side rather than reuse
FourierSAT's sum: encode each variable as a Bernoulli; transform each clause; combine clauses
multiplicatively, since SAT is an AND; invert the transform so the product becomes a sum of
random variables; argue the sum is Gaussian for large m; estimate by sampling; simplify the
covariance of the sum by exploiting its structure.

What survived:

- The relaxation is an exact expectation (above), and within one clause the literals are
  distinct variables, so a clause's generating function is a legitimate one.
- Product ↔ convolution is a theorem, and it is what re-derives FourierSAT's FFT trick.
- The inversion, read correctly, is over a *counting* variable, not over assignments. With
  f_j = P(clause j satisfied) under the product measure,

      G(z) = prod_j (1 - f_j + f_j z)

  is the generating function of the number of satisfied clauses *if the clauses were
  independent*; inverting it (evaluate at roots of unity, product tree, O(m log^2 m)) gives
  that Poisson-binomial law. Its top coefficient is prod_j f_j = prod_j (1 - U_j), which is the
  probability that all clauses are satisfied, under clause independence, and needs no inversion.

What did not survive, as four caveats:

1. Clauses share variables, and that sharing is the problem: E[prod_j f_j(x)] is not
   prod_j f_j(p). Beyond one constraint everything is a mean-field approximation.
2. A transform over assignments has 2^n coefficients, not m; the product of clause
   polynomials is a convolution that blows up.
3. Sampling is either redundant (the objective has a closed form) or starved (the target
   "all clauses satisfied" is a rare event whose samples are almost always zero).
4. The product of clause polynomials is not multilinear, so its expectation is no longer the
   polynomial evaluated at p.

Two salvage directions were named: the log-sum objective sum_j log f_j(p), and correlated
parameterisations where sampling earns its place. The second is not a direction but a field:
Bernoulli parameters sampled and updated by gradient is the cross-entropy method (Rubinstein
1999), used for counting satisfying assignments since 2007, and in neural form variational
annealing; see `../../literature/gaussian-like-objectives/`. The follow-up dropped the transform step
altogether (the clause polynomial *is* its Fourier expansion), took the sum of clause
indicators as the object, and used the sparsity of its dependency graph to write its mean and
variance in closed form and justify a Gaussian surrogate by the central limit theorem for
locally dependent sums. That surrogate is the objective of this branch.
