# State of the art for this question

Not the state of the art of SAT solving, which `../review.md` already records (probSAT and
CDCL on uniform random 3-SAT, FastFourierSAT on hybrid constraints). This page is about who
holds the record for the three things our objective needs: computing `P(all satisfied)`,
approximating it, and descending it.

## Computing the object exactly

- **Weighted model counters.** `Ganak` [ganak_repo] is public C++ under the MIT licence and
  its README states support for weighted and projected counting, with literal weights given
  by a `c p weight` directive. This is the only way found to obtain the ground truth our
  surrogates approximate, at sizes where enumeration is impossible.
- **Knowledge compilation with a differentiable circuit.** `PySDD` [pysdd_repo], Python over
  the C sentential decision diagram package, Apache 2.0, performs weighted model counting with
  settable literal weights. Its README documents no derivative, so a gradient must come from
  the circuit's own two-pass evaluation, as in semantic loss [xu2018semanticloss], or from
  finite differences. Measured in circuit size, which is instance dependent, not in `n`.

## Approximating it

- **Under a Local Lemma condition** the cluster expansion gives a strictly positive lower bound
  on `P(no bad event)` and an improvement over the classical Local Lemma
  [bissacot2011clusterlll], and approximate counting and sampling are possible when the width
  is logarithmic in the maximum degree [moitra2019counting]. Both are *sufficient conditions*
  at low density; neither says anything at ratio 4.26, where our benchmark sits.
- **Under local dependence** the normal approximation has an explicit error of order
  `m^{-1/2}` on the absolute scale [chen2004localdependence] and the Poisson approximation an
  explicit error in `b_1 + b_2` [arratia1989poisson]. `regimes.md` already shows which of these
  covers our trajectory; the record for the tail itself is the saddlepoint family, which no
  source found applies to a clause count.

## Descending it

- **Exactly, as a loss:** semantic loss [xu2018semanticloss], on constraints small enough to
  compile. State of the art for neurosymbolic training, never reported as a SAT solver.
- **By sampling:** the cross-entropy method and its splitting variant
  [rubinstein1999ce, rubinsteinkroese2007satcount, botev2008splitting], for counting satisfying
  assignments; variational classical annealing [hibatallah2021vna] for spin glasses, with
  public code that carries no SAT reader [vna_repo].
- **By a mean-field surrogate:** the whole continuous local search line, which maximises the
  *sum* of clause polynomials, not a probability. The current record holder on that line is
  **AFSAT** [christopher2026afsat], June 2026, an engineered GPU pseudo-Boolean solver in JAX
  with just-in-time compilation, automatic vectorisation and array sharding across
  accelerators, reporting improved numerical stability, runtime and memory against
  FastFourierSAT. Its abstract gives no head-to-head figure against a discrete solver, so it is
  a record on its own line only.

## Upper bounds and lower bounds, kept apart

- **Lower bounds on the satisfiability threshold** come from the second-moment method over
  random formulas: `2^k ln 2 - O(k)` [achlioptas2004threshold], with the not-all-equal weighting
  that makes the method work [achlioptas2006twomoments]. These bound where solutions exist. They
  say nothing about any algorithm, and nothing about a fixed formula at a fixed `p`.
- **Upper bounds on an algorithm class** come from the analysis of belief-propagation-guided
  decimation, which provably fails on random formulas well below the threshold
  [cojaoghlan2017bpdecimation], and from the overlap-gap results already recorded in
  `../review.md`. These bound what marginal-based methods can do, and a product measure is a
  weaker object than the marginals they use, so they are the pessimistic side of our own case.
- **No bound was found** on what a second-moment-corrected mean-field objective can reach, in
  either direction. That is the honest state: an unbounded, unmeasured method.
