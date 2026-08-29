# FFT and Fourier analysis as a tool to study SAT relaxations

**The question.** What does the Walsh-Hadamard spectrum of a CNF and of its multilinear
relaxation tell us: how sparse it is, what it costs to compute, what landscape statistics
follow, and whether any of it predicts where our gradient ascent lands?

## Verdict

1. The Fourier spectrum of a MAX-SAT function has been in closed form, computable in time
   linear in the formula, since 1998 [rana1998walsh]. Our `mu` is that function's multilinear
   extension, so its spectrum is already sparse (at most 7m + 1 coefficients on 3-CNF),
   already degree 3, already known, and no FFT is needed: the FFT in this line evaluates
   elementary symmetric polynomials for cardinality and XOR [cen2025fastfouriersat].
2. The exact landscape statistics of k-SAT have been computed from that spectrum for
   twenty-five years [heckendorn2002embedded, sutton2009correlation, sutton2012moments], and
   that literature's own conclusion is a warning: the low-order information is nearly flat,
   and having every moment in polynomial time still leaves an NP-complete problem.
3. Nobody found has computed the spectrum of a *relaxation* to predict a continuous
   trajectory or a basin. `../review.md` needs three corrections (`4-positioning.md`).

## The baseline

**Baseline A, reproduction.** Theorem 1 of [rana1998walsh] with its published numbers:
w_0 = 7m/8; every Walsh coefficient a multiple of 1/8; on 3-CNF at most n order-1, 3m
order-2 and m order-3 nonzero coefficients (its Table 2, for n = 100 with 100, 500 and 1000
clauses). Measured by exact agreement on all four quantities computed from `dimacs.py`'s
`variable_index` and `sign`, and agreement of w_0 with `moments.py`'s `mu` at p = 0.

**Baseline B, prediction.** The exact autocorrelation and correlation length of
[sutton2009correlation], whose published ensemble result is that the expectation "is
invariant to the constrainedness of the problem as measured by the ratio of clauses to
variables". Measured against our own basin fractions in
`../../gaussian_surrogate/experiments/basin_of_attraction.md`, which fall from 0.383 to
0.0078 for `F` between ratio 3.0 and 4.26 at n = 100. Either the correlation length tracks
that collapse or it does not, and either answer is a result.

**Caveat on the baseline.** No public code exists for either: `gh search repos` returned
zero on five phrasings (`queries.md`). Both baselines are published numbers to be
reproduced, not a program to be run. The review is finished in the contract's sense, but
the reproduction is ours to write.

## Files

- [1-naming.md](1-naming.md): the problem in one sentence and every name the field uses.
- [2-review.md](2-review.md): the map, grouped by line, each work with how it was verified.
- [3-state-of-the-art.md](3-state-of-the-art.md): record holders, measure, hardware; upper
  bounds kept apart from lower bounds.
- [4-positioning.md](4-positioning.md): not done in the world against not done here, and
  six corrections to our notes, quoted.
- [5-plan.md](5-plan.md): three measurements, what to reject on paper and why.
- [queries.md](queries.md): every query, service and hit count, including the zeros.
- [references.bib](references.bib): one entry per work, each with its verification note.

The fourth, smaller question of the brief is answered separately in
[../tanh-parametrisation.md](../tanh-parametrisation.md).
