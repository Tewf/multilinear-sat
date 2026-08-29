# Plan: what to measure, against what, and what to reject on paper

## Reject on paper, before any code

**A Walsh-Hadamard transform of the objective.** The FWHT costs n 2^n, and subset
convolution in the transform domain costs O(n^2 2^n) [bjorklund2007subset]. Neither is ever
needed: the spectrum of `mu` is written down in closed form by [rana1998walsh], with at most
7m + 1 nonzero coefficients on 3-CNF. Do not implement a transform of the formula.

**Sparse Walsh-Hadamard machinery.** [cheraghchi2016sparse] and [li2015spright] recover a
k-sparse spectrum from queries to an unknown function. We are given the formula, so the
spectrum is free. Their regime is not ours.

**The product-tree FFT, for the current benchmark.** It evaluates elementary symmetric
polynomials [cen2025fastfouriersat], and uniform random 3-CNF has no symmetric constraint.
It belongs to the XOR and cardinality work, where AFSAT's numerical-stability finding
[christopher2026afsat] also applies.

**Any claim that low-degree hardness covers our ascent.** [bresler2022lowdegree] measures
degree in the random instance, and states its threshold asymptotically in k. Repeating
`../review.md`'s caution rather than weakening it.

## Measure 1: reproduce the published spectrum on our own instances

Compute every nonzero Walsh coefficient of each benchmark formula from Theorem 1 of
[rana1998walsh], using the `variable_index` and `sign` tensors of `dimacs.py`'s `Formula`.
**Baseline, published numbers:** w_0 = 7m/8; every coefficient a multiple of 1/8; on 3-CNF
at most n order-1, 3m order-2 and m order-3 nonzero coefficients (that paper's Table 2 for
n = 100 with 100, 500 and 1000 clauses). **Measured by:** exact agreement on all four
quantities, and agreement of w_0 with `moments.py`'s `mu` at p = 0 to floating-point
tolerance. Cost: O(m), one pass. This is the correctness gate for everything below, and it
is the check we can run with no baseline code, since none was found.

## Measure 2: does the landscape's correlation length predict our basins?

Compute the exact autocorrelation function and correlation length of each instance by the
polynomial-time Walsh decomposition of [sutton2009correlation], and compare against the
basin fractions already recorded in `../../gaussian_surrogate/experiments/basin_of_attraction.md`.
**Baseline, a published claim with a definite prediction:** that paper's ensemble
expectation "is invariant to the constrainedness of the problem as measured by the ratio of
clauses to variables". Our measured basin fraction at n = 100 falls from 0.383 at ratio 3.0
to 0.0078 at ratio 4.26 for `F`, a factor near 50. **Measured by:** the correlation length
computed exactly at each ratio, against that factor. The prediction is that correlation
length explains none of it. If it does not, the honest result is that the standard
ruggedness statistic of this field is blind to what our restarts see, and the search for a
predictor moves to a different statistic. If it does, we have found the predictor.
Reimplementation is required: no public code was found (`queries.md`).

## Measure 3: which coefficients does the ascent actually use?

Zero the Walsh coefficients of `mu` by order, or by magnitude, rebuild the polynomial, and
run the same batched ascent. Order 1 alone is the linear part that [rana1998walsh] says
dominates the schema averages; orders 1 and 2 add the pair structure that
`method/pair-expansion.md` already computes. **Baseline:** the `mu`, `fourier` and `F`
columns of `../../gaussian_surrogate/findings.md`, same seeds, same loop, same budgets.
**Measured by:** the basin fraction and the mean violated clauses at rounding, the two
numbers that table already reports. This is the one experiment that turns the 1998 flatness
result into a statement about a gradient method, and no paper found does it.

## Order and cost

Measure 1 is an afternoon and gates the rest. Measure 3 reuses the existing loop and the
existing tables, so it is the cheapest new number. Measure 2 needs the autocorrelation
formula re-derived from the two abstracts plus [sutton2012moments], which is the only part
that could fail for want of the full text; if it does, say so and stop there rather than
guessing the formula.

## What would make this line worth a paper

Only Measure 3 with a positive result: a truncation of the spectrum that keeps the basin.
Measures 1 and 2 are reproduction and refutation, which is what the review is for.
