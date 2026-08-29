# Plan

## The measurement that is missing, and it is not a solver run

The benchmark answers "does `F` find more solutions than `mu`". It cannot answer "is `F` a good
approximation of what it claims to approximate", because nothing in the repository ever
computes the thing itself. That number is now cheap to get.

**Fidelity experiment.** Take points `p` sampled along the existing `F`, `mu` and `pair`
trajectories on `uf50-218` and, if the counter scales, `uf100-430`. At each point compute:

- the exact `log P(all clauses satisfied)` under the product measure, as a weighted model count
  with `Ganak` [ganak_repo], literal weights `(1 + p_i)/2` and `(1 - p_i)/2`;
- the four surrogates `mu`, `logsum`, `L_pair` and `log F` already implemented;
- optionally the exact gradient, by `2n` counter calls (central differences) at a subset of
  points, or from a compiled circuit with `PySDD` [pysdd_repo].

**Measured by:** Spearman rank correlation between each surrogate and the exact value over the
sampled points, the sign and size of the bias predicted in `regimes.md` (`log F` about
`-lambda/2` against `-lambda`), and the cosine between each surrogate gradient and the exact
gradient. A surrogate that ranks points as the truth does and points the same way is doing its
job; one that does not is winning the benchmark for another reason, which is worth knowing
before more objectives are built.

## The algorithmic comparison, with the baseline named

**Baselines:** `probSAT` [probsat_repo], the unbeaten stochastic local search baseline on
uniform random 3-SAT, and the repository's own `mu` ablation on identical scaffolding.
**Measured by:** expected time to a solution, that is the median cost of a restart divided by
the fraction of restarts that succeed, at fixed hardware, seeds and time caps. `findings.md`
already has both halves for `F` and `mu` and is missing the polish-only control it flags; add
that control and `probSAT` and the table is complete.

## The ladder, with one entry renamed

The ladder of `open-directions.md` stands, with `logsum` promoted from a curiosity to the
**factorised mean-field model count**, which is what it is, and with `L_pair` named as a cluster
expansion truncated at pairs [bissacot2011clusterlll]. If `L_pair` matches `F`, the gain is the
pair information; if not, it is the appetite for variance, which the tilted form makes tunable.

## What to reject on paper, and why

1. **Sampling to estimate the objective** (step 6 of the original skeleton). Redundant where the
   closed form exists, starved where it does not, and if pursued anyway the method already
   exists and is called the cross-entropy method [rubinstein1999ce], with SAT counting results
   since 2007 [rubinsteinkroese2007satcount]. Entering that branch means entering it against
   their baselines.
2. **Reporting `F` as a probability.** `regimes.md` shows no regime in which the normal tail is
   the right law on the way in, and the naming shows the criterion is a safety-first ratio
   [roy1952safetyfirst], the probability of improvement of an unknown quantity [kushner1964pi].
   Log the ratio `z`, call it `z`, and let the continuity correction be what it is, a schedule.
3. **Citing the second-moment method for thresholds as precedent** [achlioptas2006twomoments].
   Different probability space.
4. **Writing a Bethe objective from scratch.** If the tree-exact functional is wanted, its
   minimiser is published and convergent [yuille2002cccp], and its behaviour on random
   constraint satisfaction is characterised [bapst2016bethe, cojaoghlan2017bpdecimation],
   including the failure mode.
5. **The tempered objective `E[e^{beta S}]` as closed form.** Already corrected in
   `open-directions.md`; the correction stands, and the *tunable* version, `mu + (beta/2)
   sigma^2` with a schedule, is the mean-variance objective the chance-constrained literature
   calls a deterministic equivalent [charnes1959chance]. That one is worth a run: one extra
   `--obj`, one extra schedule, no new mathematics.

## Order

1. Fidelity experiment (no GPU, one counter, existing trajectories).
2. `logsum` and `pair` as `--obj`, then the full ladder on the existing harness.
3. `probSAT` and the polish-only control, then the expected-time-to-solution table.
4. Only then, a free `beta` schedule on the mean-variance objective.
