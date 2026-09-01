# Fidelity: what each surrogate actually approximates (Q1, measured 2026-09-01)

The question of [`literature/gaussian-like-objectives/5-plan.md`](../literature/gaussian-like-objectives/5-plan.md):
does any surrogate rank points, and point its gradient, the way the exact
`log P(all satisfied)` does? Nothing in the repository had ever computed the exact
value. Setup and per-instance numbers: [`experiments/fidelity.md`](experiments/fidelity.md)
(generated), records in `experiments/fidelity.jsonl`; the ground truth is one SDD
compilation per instance ([`experiments/exact_count.py`](experiments/exact_count.py)),
whose construction is verified against enumeration, against PySDD's own CNF
compiler (equal to 7e-15 at four points), and by a corner self-check per instance.
uf50-218, first ten instances, ~165 points each pooled from the F, mu and fourier
trajectories (logsum and the pair expansion were planned as `--obj` and never
built, so the points come from the three implemented dynamics).

## The ranking, by median Spearman against the exact value

| surrogate | rho | gradient cosine | slope |
|---|---|---|---|
| pair (cluster expansion at pairs) | **0.554** | 0.202 | 3.1 |
| logsum (factorised mean-field count) | 0.318 | 0.126 | 0.042 |
| log F (the Gaussian) | 0.271 | **-0.037** | 0.144 |
| mu (expected satisfied clauses) | -0.007 | **-0.287** | -0.003 |

## What this settles

1. **No surrogate is a good approximation of what F claims to approximate.** The
   best of the four, the pair expansion, ranks points at rho 0.55; the ladder's
   ordering (pair > logsum > F > mu) is exactly the cluster-expansion ordering,
   so the pair information is real and the Gaussian's variance term is not a
   substitute for it.
2. **mu's gradient points away from the truth at these points**: cosine negative
   on all ten instances (-0.14 to -0.46). Yet the mu-seeded walk is the only seed
   that raises per-restart success (`benchmark/arms/front.md`). Both being true is
   the plan's "winning the benchmark for another reason", now with the number:
   the seeds work through basin geometry, not through probability fidelity, which
   is why no fidelity argument can rescue the seed line and the walk verdict of
   `method/algorithm.md` stands on its own.
3. **The regimes prediction fails quantitatively**: `regimes.md` argued log F
   about -lambda/2 against the exact -lambda (slope 0.5); the median measured
   slope is 0.144, and on two instances (uf50-0103, uf50-0106) saturation of
   log Phi at z > 8 makes the slope meaningless (602 and 6824) while Spearman,
   the robust column, stays in range. F compresses the truth far more than its
   own analysis predicted.
4. **The gradient story is worse than the value story everywhere**: the best
   median cosine is 0.20. At these trajectory points, no implemented ascent
   direction tracks the exact one; the exact gradient is dominated by the nearest
   few models (uf50 instances near the threshold hold ~24 solutions), which no
   product-form surrogate sees.

## What it does not settle

uf100 was not attempted (the uf50 answer is decisive for the ladder's order and
the counter's cost grows with the circuit); points are trajectory-biased by
construction, which is the plan's own design (fidelity where the dynamics
actually goes); and the polish-only control of the algorithmic table is a
separate, still-open row.
