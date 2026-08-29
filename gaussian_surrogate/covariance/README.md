# The covariance of the clause vector: what its structure allows

The branch asks whether the multivariate Gaussian N(U(p), Sigma(p)) of the clause-unsatisfied
vector can be simplified through its covariance (principal components, collinearity, null
space) and whether that simplification reduces literals or clauses. The objective of the
parent package uses one number of Sigma, 1'Sigma 1; everything here is about the rest of it.

## The object

Under the product measure with means p, I_j(x) = 2^{-k} prod_{(i,s) in C_j} (1 - s x_i) has
mean U_j and the pair (j, k) has covariance U_jk - U_j U_k, nonzero only when the clauses
share a variable (`../adjacency.py`, `../moments.py`). At p = 0 the Walsh monomials are
orthonormal, so Sigma(0) is the Gram matrix of the clause polynomials with the constant
removed: its zero eigenvalues are exactly the linear dependencies among the clause
indicators. For any interior p the measure has full support, so Var(c'I) = 0 if and only if
c'I is constant on the cube: the null space of Sigma(p) is the same subspace at every
interior p, an invariant of the formula and not of the point.

## Measured (2026-08-29, dense eigendecomposition, one CPU, seconds)

Six instances: SATLIB uf50-01, uf50-02, uf100-01, uf250-01, and two of the tensor-rank
toolkit's GF(2) encodings written with `--plain-cnf` (f2_2x3 at r = 5: 291 variables, 858
clauses of width 1 to 3; matmul_2x2x2 at r = 7: 1028 variables, 3280 clauses). At p = 0 and at
three random points in (-0.8, 0.8)^n:

| quantity | random 3-SAT | toolkit GF(2) |
|---|---|---|
| nullity of Sigma | 0 on all four, at every p | 0 on both, at every p |
| exact rank of the Walsh matrix (mod 2^31 - 1) | m, agrees | not computed (Sigma(0) suffices) |
| eigenvalue range at p = 0 | 0.03 to 0.52 | 0.03 to 0.72 and 1.40 |
| share of the trace in the top ten eigenvalues | 18, 18, 9, 4 % | 6, 3 % |
| off-diagonal part of 1'Sigma 1, absolute | 1 to 11 % | 5 to 12 % |
| Jacobian dU/dp: collinear column pairs, max abs correlation | 0, 0.32 | 0, 0.29 |
| variable sets carrying more than one clause | 1, 0, 0, 0 | 96 and 384 (four each) |

Scripts: `2026-08-29_covariance-reduction/out/` (not in this repository until
the literature review says what they should be measured against).

## Reading

- **No exact reduction exists on either family.** A dependence must cancel every
  top-degree monomial, and x_a x_b x_c belongs only to the clauses on that triple; random
  3-SAT almost never repeats a triple, and the toolkit's parity expansions put four sign
  patterns on one triple whose indicators sum to (1 - xyz)/2, not to a constant. A null
  vector needs all eight patterns, which is a trivially unsatisfiable formula.
- **A resolution merge is not a null vector.** I_{x or y or z} + I_{x or y or not z} equals
  I_{x or y}, a clause that is not in the formula; the merge shortens the formula and is
  found from the Walsh support in O(m), not from Sigma.
- **No literal to tie**: the Jacobian has full column rank and no correlation above 0.32.
- **Nothing low-rank to compress**: after diagonal scaling the Gaussian is close to
  isotropic. The toolkit CNFs show a threefold-degenerate top eigenvalue carried by binary
  Tseitin clauses, the r copies of one gate pattern: a symmetry signature the toolkit's
  orbit reduction already exploits, not a reduction.

## What survives

The off-diagonal covariance is a small fraction of the variance, which makes the diagonal
Gaussian a rung of the ladder in `../method/open-directions.md`:

    F_diag   Phi( (1/2 - sum_j U_j) / sqrt( sum_j U_j (1 - U_j) ) )

It costs what `mu` costs and separates the two ingredients of F: if its basin matches F's
2 to 4x, the pair term is not where the gain comes from and the cost objection to F goes
away; if it does not, the pairs earn their price. Not run before the literature review
(`../../literature/covariance-structure/`) names the baseline for the exact-dependence
and merge machinery, which has content only on instances with repeated variable sets.
