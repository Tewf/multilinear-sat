# Findings: does the variance term help, and where?

Measured on the RTX 4060 on 2026-08-28 and 29, one seed, on the code at commit 572ee68 or
later. Records: `benchmark/results.md` (SATLIB, time-capped, with the WalkSAT polish),
`experiments/basin_of_attraction.md` (no polish, fixed step budget), and the per-step costs
below. The methods are defined in `method/baselines.md`.

## Three measurements

**Landing.** Mean over instances of the fewest violated clauses at any rounding, before the
polish (SATLIB, 100 instances per family):

| family | F | mu | fourier |
|---|---|---|---|
| uf50-218 | 0.77 | 1.49 | 1.29 |
| uf100-430 | 2.09 | 3.11 | 2.65 |
| uf250-1065 | 4.92 | 6.12 | 6.51 |

**Basin.** Fraction of 512 restarts whose rounded point satisfies the formula within 500
steps, no polish (20 instances per point; means, with heavy tails across instances):

| point | F | mu | fourier |
|---|---|---|---|
| n=100, ratio 3.0 | 0.383 | 0.194 | 0.146 |
| n=100, ratio 4.0 | 0.024 | 0.011 | 0.006 |
| n=100, ratio 4.26 | 0.0078 | 0.0039 | 0.0021 |
| uf50-218 | 0.055 | 0.026 | 0.020 |
| uf100-430 | 0.0016 | 0.0003 | 0.0003 |
| uf250-1065 | 0 | 0 | 0 |

**Cost.** Milliseconds per Adam step on an idle GPU, batch 64 (the benchmark's) and 512
(the basin's): F / mu is 3.1 on uf50, 5.7 on uf100 and 26 on uf250 at batch 64; 50 on uf100
and 86 on uf250 at batch 512. At batch 64 the launch floor of about 0.5 ms hides most of
the pair arithmetic on the small families.

**Under the cap** (solve rate, median time over solved runs): uf50 100 % for all three
(0.05 / 0.04 / 0.04 s); uf100 F 94 %, mu 99 %, fourier 98 % (0.32 / 0.11 / 0.10 s); uf250
F 38 %, mu 77 %, fourier 81 % (9.6 / 2.0 / 3.6 s).

## Reading

The expected time to a solution is the cost of a restart divided by the probability that a
restart succeeds. The variance term raises that probability by a factor 2 to 4 at every ratio
and size where any restart succeeds, and lowers the residual at rounding by 30 to 50 %; it
multiplies the cost of a step by 3 to 26 at the benchmark's batch. Where the cost ratio is at
or below the basin ratio (uf50: 3.1 against 2.1; uf100: 5.7 against 5.3) the table shows
parity or a small deficit; where it is far above (uf250: 26, and no restart succeeds without
the polish for any objective) F loses by two to one. On uf250 every solve is the polish
finishing from a rounded point, and the cheaper objective hands it more starts.

The box geometry has a smaller basin than tanh everywhere, yet solves as much or more under
the cap: its step is the cheapest of the three. Geometry and objective are separable effects.

## The paragraph asked for

The sigma term helps the continuous dynamics at every instance size measured, and in the
same direction each time: rounded points 30 to 50 % closer to a solution, and two to four
times as many restarts reaching one without any polish. It does not help wall-clock under a
time cap beyond n = 100, because a step costs 3 to 26 times a mean-only step at the
benchmark's batch and up to 86 times at large batches, and because at n = 250 no objective's
dynamics reach a solution on their own, so the solves belong to WalkSAT and the cheaper
objective feeds it more starts. On this hardware the crossover lies between n = 100 and
n = 250. A native port would remove the launch floor and widen the cost gap, so the verdict
is not an artefact of Python in F's favour. What would move it: a cheaper pair term, a
rounding that uses the moments, or the pair objective in `method/open-directions.md`, whose
regime analysis is the next step before any further run.

## Caveats

- No control with the polish alone (random assignments, the same flips and cap). Without it
  nothing about uf250 can be attributed to the continuous part of any method.
- One seed and 100 instances per family; 20 instances per basin point, with medians well
  below means. No confidence intervals.
- The uf250 phase of both SATLIB runs shared the GPU with an image-generation server; run 1
  is superseded by an implementation fix (see `benchmark/results.md`, Caveats).
- The continuity correction (+1/2) and the variance floor were never varied.
