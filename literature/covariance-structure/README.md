# Q5: the covariance of the clause vector, for literal and clause reduction

**The question, in one sentence.** Does the covariance matrix Sigma(p) of the clause-unsatisfied
indicator vector under the product measure, through its kernel, its small eigenvalues or its
leading eigenvectors, justify removing clauses, tying literals, decomposing the instance,
warm-starting a search or detecting a backbone?

## Verdict

1. Nobody has taken the spectrum of a clause-indicator covariance under a product measure, for
   any purpose. Not found on nine queries across three services and four `gh` phrasings.
2. That is not an opening. Every reduction the covariance can express, the field already does
   better by logic: the one identity the kernel could hold, a resolution merge, is not even a null
   vector of Sigma (its resolvent is not a clause of the formula; measured 2026-08-29, uf50-01
   carries one merge pair and Sigma has full rank), and as a substitution it is what every
   preprocessor removes, at Theta(alpha^2 / n) per instance, about 0.45 clauses on uf50.
3. A non-negative null vector is a Nullstellensatz certificate with constant multipliers. Random
   CNFs need degree Omega(n), so it provably does not exist for them.
4. The spectral refutation line does exist, and its matrices are n by n and indexed by
   variables, not m by m and indexed by clauses. It is a different object, not a precedent.
5. The exact correlation structure of k-SAT was computed in polynomial time by Walsh
   decomposition in 2009. It is a scalar autocorrelation along a hypercube walk, not our matrix,
   and its public code was not found.
6. The claim that the Jacobian's collinear columns are equivalent-literal structure is false;
   they are syntactic duplication, which does not occur in random 3-CNF.
7. On uniform random instances there is no community structure for the leading eigenvectors to
   align with. That experiment has to move to application instances or it measures nothing.
8. What is left worth doing is a diagnostic, not a solver: compute the exact rank of the
   non-constant Walsh coefficient matrix and see whether the kernel is bigger than the merge
   space. If it is, that is new; if it is not, the branch closes on paper.

## The baselines, and what "better" means

**Clause and literal reduction.** CaDiCaL with default preprocessing against `cadical --plain`,
and bounded variable elimination as the named technique [een2005satelite]; Kissat as the solver
run on the reduced formula. Both `gh repo view` verified on 2026-08-29, MIT. Measured by
variables, clauses and literals removed, then solved count and PAR-2 of the solver afterwards.
The bar, in the baseline's own words: a good reduction is "an additional factor of two in
reduction" over the previous technique and turns "a timeout of more than 600 seconds" into
"about 250 seconds to solve 275 problems"; the honest negative from the same paper is "reduction
rates of less than 5% were achieved, and no measurable speedup".

**Correlation structure.** The exact polynomial-time Walsh computation of a k-SAT instance's
correlation structure [suttonwhitleyhowe2009]. Its public code was **not found**, so the
baseline is a re-implementation from the paper, cross-checked against the brute-force
enumeration already in `gaussian_surrogate/tests/`. Measured by exact agreement at n <= 10 and
by the rank deficiency per instance family.

**Community structure.** Modularity of the clause graph computed with `ekuiter/SATGraf` (Java,
MIT, `gh repo view` verified), against the published finding that application instances have
high modularity and random ones do not [ansotegui2019community]. Measured by adjusted Rand index
between the eigenvector clustering and the community partition, on application instances.

## Files

- [1-naming.md](1-naming.md): the problem in one sentence, every name the field uses, why ours
  differs and where it misleads.
- [2-review.md](2-review.md): the map in eight lines of work, one to three lines per work, with
  how each was verified.
- [3-state-of-the-art.md](3-state-of-the-art.md): record holders, methods, measures, with upper
  bounds kept apart from lower bounds.
- [4-positioning.md](4-positioning.md): the brief's six claims one by one, true, false or open,
  with the corrected sentences quoted.
- [5-plan.md](5-plan.md): six things to reject on paper, three steps worth measuring.
- [queries.md](queries.md): every query, with every "not found".
- [references.bib](references.bib): 52 entries, each with its verification note.

Contract: `2026-08-28_gaussian-surrogate-sat/review-contract.md`. Question:
`2026-08-29_covariance-reduction/brief.md`. No solver was run and no code was
changed; the numbers quoted above are the cited papers' own.
