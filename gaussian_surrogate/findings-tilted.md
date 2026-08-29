# Findings: the tilted sampling-gradient loop, measured

Built and measured on 2026-08-29 (commits 1db4cd6 to 49cf5ef on `gaussian-surrogate`), one
RTX 4060 Laptop GPU shared with other processes, torch 2.13. Records: `experiments/tilted_mean_bias.md`
(CPU, enumeration), `experiments/seed_comparison.jsonl` and `.md` (GPU), `experiments/posterior_calibration.jsonl`
(kissat on the CPU; the loop's half on the GPU). What was built and what was left out is in
`method/not-built.md`; the design is `method/sampling-gradient-loop.md` as corrected by its review.

## Status of the two experiments

The GPU was free from 12:54 to about 13:12, then another process (5.5 GB, 100 %) took it back during
the uf50 phase of the seed comparison. The 11 records made under contention were dropped (the
uniform arm's polish time, 0.155 s alone, jumped to 0.21 s: that is the detector) and the run
stopped, per the rule that nothing runs on a held card. **Seed comparison: 71 clean records,
uf50-218 only, 9 instances; uf100 and uf250 pending. Posterior calibration: kissat's half done
(20 uuf250 instances), the loop's half pending.** The exact commands are at the end.

## Table 1: is the sampled tilted mean an estimate of anything? (n = 12, enumeration)

RMS error of the weighted sample mean against the exact E_tilted[x], 5 seeds, from
`experiments/tilted_mean_bias.md`:

| beta | move | 16n moves, S = 64 | S = 512 | S = 4096 | ESS at 4096 |
|---|---|---|---|---|---|
| 0.5 | metropolis (AIS weights) | 0.122 | 0.049 | 0.015 | 3801 |
| 0.5 | walk (SKC, exp(beta S) weights) | 0.564 | 0.542 | 0.545 | 4096 |
| 2.0 | metropolis (AIS weights) | 0.121 | 0.052 | 0.018 | 1580 |
| 2.0 | walk (SKC, exp(beta S) weights) | 0.249 | 0.219 | 0.223 | 4096 |

The annealed move is consistent (the error falls as 1/sqrt(S) at every rung count); the walk's
weights belong to no measure and its error does not move with S. The first run of this table
found a bug: freezing a chain at S = m biased the mean by 0.40 RMS.

## Table 2: per-restart success of one polish from four seeds (uf50-218, 9 instances, seeds 0 and 1)

512 slots, T = 500 seeding steps, polish = 10n SKC flips of the flip kernel; p = mean fraction of
slots satisfied, cost = median (seed + polish) seconds per slot, expected time = cost / p:

| seed | runs | p | cost / restart (ms) | expected time (ms) | seed s | p > uniform's, per run |
|---|---|---|---|---|---|---|
| uniform | 18 | 0.528 | 0.31 | 0.6 | 0.00 | - |
| all false | 18 | 0.519 | 0.31 | 0.6 | 0.00 | - |
| mu ascent | 18 | 0.582 | 0.87 | 1.5 | 0.32 | 16 / 17 |
| tilted loop (metropolis, consistent weights) | 17 | 0.557 | 34.7 | 62.3 | 17.67 | 11 / 17 |

The loop's final ESS was 19.6 of 32 and 28 % of its means were saturated; in 14 of 17 runs a
sample satisfied the formula during the seeding steps. Throughput: the kernel's polish ran at
3,196 flips per second per chain, 1.6 M per second over the 512 chains, against 6.26 M per second
for probSAT on one CPU core (uuf250-01, 20 M flips, seeds 1 and 2): one chain is 1959x slower,
and the whole batch is 4x slower than one core. The kernel is launch-bound (about 15 kernel
launches per flip); a fused kernel is the fix, not more slots.

## Table 3: the UNSAT posterior against kissat (uuf250-1065, 20 instances)

kissat refutes each instance in 1.16 to 4.23 s (median 2.52 s, fastest of three, exit 20 every
time). The loop's half (the Beta-mixture posterior's time to 0.99 and its reliability curve) is
pending; the rigorous posterior cannot move on this family, since Schöning's one-try bound at
n = 250 is (3/4)^250 / 2253 = 2.7e-35 (`posterior.py`, with the polynomial the FOCS 1999 text
leaves unwritten made explicit).

## What the tables show

The sampler half of the loop works as the theory says and the seed half does not pay. With
annealed-importance-sampling weights the loop's gradient is a consistent estimate of the tilted
mean minus p (Table 1); with the walk it estimates nothing, at any batch size, so the walk-mode
loop is a cross-entropy method with the SKC walk as its elite generator and must be reported as
such. On uf50-218 the tilted seed raises the per-restart success of the same polish by 6 % over a
uniform start (11 of 17 runs), less than mu ascent's 10 % (16 of 17), at 113x the cost per restart
against mu's 3x: its expected time to a solution is 100x a uniform start's and 40x mu's. The
seed does not pay for its gradient steps on uf50; whether that changes at n = 250, where a uniform
start's p is far lower, is the pending half of Table 2. The control variate the note asked for
adds noise rather than removing it at every beta measured (uf50-01: 8 % to 26x), because a
2n-flip move decorrelates the sample from its raw draw; its coefficient defaults to 0. On the
UNSAT side, only the Beta-mixture posterior can move at n = 250, kissat's 1 to 4 s is the number
it has to beat, and its calibration is pending.

## Caveats

- One GPU, shared: the run was interrupted by another process and the contended records dropped
  by a timing detector, not by a log of the other process's activity. Seeds {0, 1}; 9 instances
  of uf50 only so far; no confidence intervals.
- The polish is the repository's flip kernel, not probSAT; per chain it is three orders of
  magnitude slower, so the costs in Table 2 are those of this implementation. Putikhin and
  Kascheev (EWDTS 2017) seeded probSAT itself; this is a replication with a different local
  search and a different seed, and their per-restart number is not published.
- The tilted seed draws its slots from q_theta after T steps; rounding sign(p) per group would be
  a different seed (16 distinct starts, not 512) and was not measured.
- The annealed move at 2n rungs reaches S = m rarely (on uf100-01 the best sample went from 30 to
  7 violated clauses in 100 steps, CPU); the walk mode reaches it in one step because the SKC
  walk alone solves uf50 to uf250 at 512 slots. Which move makes the better seed is the
  `tilted_walk` arm, pending.
- No decimation, no tempered proposal correction beyond AIS, the Luby schedule kept on faith
  (`method/not-built.md`), the beta schedule and every other constant set once and never tuned.
- The Beta prior for the calibration is fitted on the seed comparison's `tilted_walk` fractions
  on uf250, so the calibration depends on that pending arm; without it the prior is Beta(1, 1).

## Pending commands (GPU free on two readings a minute apart, CPU under 85 C)

    cd gaussian_surrogate && PY=~/miniforge3/envs/flappy_bird/bin/python
    $PY experiments/seed_comparison.py --device cuda                                        # resumes: 71 of 480 records done
    $PY experiments/seed_comparison.py --device cuda --families uf250-1065 --seed-methods tilted_walk
    $PY experiments/seed_table.py
    $PY experiments/posterior_calibration.py --phase loop --device cuda                      # kissat phase already recorded
    $PY experiments/posterior_table.py
