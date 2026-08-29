# Plan: what to reject on paper, what to measure, against what

## Rejected on paper, with the reason

1. **Clause reduction from ker Sigma.** The exact merge identity is resolution whose resolvent
   subsumes both antecedents, already removed by subsumption and bounded variable elimination
   [een2005satelite, biere2021preprocessing], and its expected count in uniform random 3-SAT is
   Theta(alpha^2 / n): about 0.45 clauses per uf50-218 instance and 0.083 per uf250-1065
   instance. There is nothing to remove, and what there is, is removed already.
2. **UNSAT certificates from a non-negative null vector.** A fixed linear combination of clause
   polynomials is a Nullstellensatz refutation with constant multipliers; random CNFs need
   degree Omega(n) [bensasson2010pc]. Keep it in the method note as a structural remark, as the
   brief already says, and build nothing.
3. **Literal reduction from exact Jacobian collinearity.** The condition is syntactic
   duplication of a variable's whole clause set with a constant relative sign, not logical
   equivalence; it does not occur in random 3-CNF, and its semantic cousin is handled by gate
   extraction plus congruence closure inside CaDiCaL [biere2024congruence].
4. **Instance decomposition by spectral partitioning of Sigma.** Connected components are found
   in linear time, and chapter 9 [biere2021preprocessing] reports that explicit component
   decomposition is "obsolete, at least for sequential plain CDCL solving" because phase saving
   already gets the effect. A spectral method would have to beat a linear-time one at a task
   the field has retired.
5. **Low-rank approximation of Sigma to make a gradient step cheaper.** Endorsed rejection, per
   claim 6 and section G of `2-review.md`: the matrix is exact and sparse, low-rank plus
   diagonal is a different model [tippingbishop1999ppca], and 1^T Sigma 1 needs no spectrum.
6. **Backbone or frozen-variable detection from Sigma.** Frozen variables are a property of the
   uniform measure on solutions inside a cluster [achlioptas2006geometry], not of a product
   measure at an interior p. The warm-start route the parent branch already lists, survey
   propagation marginals, is the one with a published precedent.

## What survives, in order, with its baseline and its measure

**Step 1, the diagnostic, cheap and worth having.** Compute the exact rank and kernel of the
non-constant Walsh coefficient matrix of the I_j (m rows, at most seven non-zeros each for
3-CNF), over the rationals, on uf50, uf100, uf250 and on a handful of application instances.

- Baseline: the exact polynomial-time Walsh decomposition of a k-SAT instance
  [suttonwhitleyhowe2009]. **Public code for it was not found** on three `gh search repos`
  phrasings, so the baseline has to be a re-implementation from the paper, cross-checked
  against the brute-force enumeration already in `gaussian_surrogate/tests/`.
- Measured by: agreement with brute force at n <= 10 to machine precision, and the rank
  deficiency per family. Measured on 2026-08-29 before this review landed (maestro,
  `2026-08-29_covariance-reduction/notes.md`): the deficiency is 0 on uf50-01,
  uf50-02, uf100-01, uf250-01 and on two toolkit GF(2) encodings, at p = 0 and at random p,
  with the Walsh rank cross-checked exactly mod 2^31 - 1; a merge pair present on uf50-01
  contributes no null vector, since its resolvent is not in the formula. The diagnostic is
  done and the exact-reduction question is closed.

**Step 2, the alignment question, only if step 1 is clean.** Compare the k-way clustering from
the leading eigenvectors of Sigma(0) with the community partition of the clause-clause sharing
graph.

- Baseline: modularity of the same graph, computed with `ekuiter/SATGraf` (Java, MIT, `gh repo
  view` verified), against the published finding [ansotegui2019community] that application
  instances have high modularity and random ones do not.
- Measured by: adjusted Rand index or normalised mutual information between the two partitions.
- **Run this on application instances, not on uf50.** On uniform random instances the published
  answer is that there is no community structure to align with, so a null result there measures
  nothing.

**Step 3, a reduction experiment, only if steps 1 and 2 produce something.** Any proposed
removal or tying must be run as a preprocessor and compared to the real one.

- Baseline: CaDiCaL with default preprocessing against `cadical --plain`, and SatELite-style
  bounded variable elimination as the named technique [een2005satelite]; solver
  `arminbiere/kissat` on the reduced formula. Both repositories `gh repo view` verified, MIT.
- Measured by: variables removed, clauses removed, literals removed, then solved count and
  PAR-2 of kissat on the reduced formula, on SATLIB and on the toolkit's GF(2) encodings.
- The bar, in the field's own words [een2005satelite]: a good reduction is "an additional
  factor of two in reduction" over the previous technique, and it converts into "a timeout of
  about 250 seconds to solve 275 problems with full preprocessing, but a timeout of more than
  600 seconds with no preprocessing". The honest negative from the same paper is the other half
  of the bar: on already well-encoded CNF, "reduction rates of less than 5% were achieved, and
  no measurable speedup".

## What to write regardless of the outcome

`gaussian_surrogate/covariance/method.md` should carry, corrected: that the kernel is
p-independent for elementary reasons and not a result; that merge pairs are not null vectors of
Sigma, are what preprocessing already removes, and number Theta(alpha^2 / n); that the non-negative
certificate is empty for random CNF by a degree lower bound; that the Jacobian condition is
duplication and not equivalence; and that Sigma is the zeroth-order Plefka susceptibility
[plefka1982], whose systematic correction is loop-corrected linear response
[wellingteh2004linearresponse, mooijkappen2007loopcorrections], which is where a multivariate
use of the clause Gaussian would actually have content.
