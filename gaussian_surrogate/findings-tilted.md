# Findings: the tilted sampling-gradient loop, measured

Built and measured on 2026-08-29 (commits 1db4cd6 to f40864c on `gaussian-surrogate`), one
RTX 4060 Laptop GPU, torch 2.13. Records: `experiments/tilted_mean_bias.md` (CPU, enumeration),
`experiments/seed_comparison.jsonl` and `.md` (GPU, 14:38 to 17:21), `experiments/posterior_calibration.jsonl`
and `.md` (kissat on the CPU at 13:15; the loop's half on the GPU, 17:21 to 17:42). No other process
was on the card at the start of any phase; the uniform arm's polish time, the contention detector,
spread over 0.151 to 0.173 s on uf50, 0.30 to 0.47 s on uf100 and 0.77 to 1.28 s on uf250, and the
tables use medians. What was built and left out is in `method/not-built.md`; the design is
`../method/sampling-gradient-loop.md` as corrected by its review. The Python package is now the
record: the implementation moved to C++ on branch `sampling-walk`.

## Table 1: is the sampled tilted mean an estimate of anything? (n = 12, enumeration)

RMS error of the weighted sample mean against the exact E_tilted[x], 5 seeds, 16n moves per sample:

| beta | move | S = 64 | S = 512 | S = 4096 | ESS at 4096 |
|---|---|---|---|---|---|
| 0.5 | metropolis (AIS weights) | 0.122 | 0.049 | 0.015 | 3801 |
| 0.5 | walk (SKC, exp(beta S) weights) | 0.564 | 0.542 | 0.545 | 4096 |
| 2.0 | metropolis (AIS weights) | 0.121 | 0.052 | 0.018 | 1580 |
| 2.0 | walk (SKC, exp(beta S) weights) | 0.249 | 0.219 | 0.223 | 4096 |

The annealed move is consistent (the error falls as 1/sqrt(S) at every rung count); the walk's
weights belong to no measure and its error does not move with S. The first run of this table
found a bug: freezing a chain at S = m biased the mean by 0.40 RMS.

## Table 2: per-restart success of one polish from five seeds (20 instances per family, seeds 0 and 1)

512 slots, T = 500 seeding steps, polish = 10n SKC flips of the flip kernel. p = mean over the 40
runs of the fraction of slots satisfied after the polish; "above uniform" counts the runs (of 40,
paired by instance and seed) whose p exceeds the uniform seed's; cost = median (seed + polish)
seconds per slot; expected time = cost / p. The last column is what each seed spends per slot
before the polish's 10n flips: mu 500 Adam steps and no flips; the tilted loop 500 steps of 2n
moves, so 1000n Metropolis proposals (tilted) or 1000n SKC flips (tilted_walk), 100 times the
polish's own budget.

| family | seed | p | above uniform | cost / restart (ms) | expected time (ms) | seed s | spent per slot before the polish |
|---|---|---|---|---|---|---|---|
| uf50-218 | uniform | 0.549 | - | 0.30 | 0.6 | 0.00 | 0 |
| uf50-218 | all false | 0.558 | 23 | 0.30 | 0.5 | 0.00 | 0 |
| uf50-218 | mu ascent | 0.588 | 33 | 0.86 | 1.5 | 0.31 | 500 Adam steps |
| uf50-218 | tilted (metropolis) | 0.562 | 22 | 34.5 | 61 | 17.6 | 1000n proposals |
| uf100-430 | uniform | 0.298 | - | 0.86 | 2.9 | 0.00 | 0 |
| uf100-430 | all false | 0.291 | 16 | 0.85 | 2.9 | 0.00 | 0 |
| uf100-430 | mu ascent | 0.336 | 30 | 1.90 | 5.7 | 0.49 | 500 Adam steps |
| uf100-430 | tilted (metropolis) | 0.321 | 31 | 80.5 | 251 | 39.4 | 1000n proposals |
| uf250-1065 | uniform | 0.086 | - | 2.35 | 27 | 0.00 | 0 |
| uf250-1065 | all false | 0.086 | 12 | 2.35 | 27 | 0.00 | 0 |
| uf250-1065 | mu ascent | 0.113 | 26 | 5.11 | 45 | 1.29 | 500 Adam steps |
| uf250-1065 | tilted (metropolis) | 0.096 | 21 | 191 | 2000 | 95.5 | 1000n proposals |
| uf250-1065 | tilted_walk (biased weights) | 0.354 | 29 | 169 | 477 | 87.1 | 1000n SKC flips |

Ties with uniform: 1 to 2 on uf50 and uf100, 5 to 7 on uf250 (both at p = 0). The loops' own
diagnostics at the last seeding step: tilted ESS 19.6 / 12.8 / 6.8 of 32 and 28 / 23 / 15 % of
means saturated on uf50 / uf100 / uf250, a sample satisfying the formula during seeding in
31 / 2 / 0 of 40 runs, best sample 8.9 clauses short on uf250; tilted_walk on uf250 ESS 20.7,
23 % saturated, a solution during seeding in 37 of 40 runs. Throughput: the polish ran at a
median 2,976 flips per second per chain, 1.5 M per second over the 512 chains, against 6.26 M per
second for probSAT on one CPU core (uuf250-01, 20 M flips, seeds 1 and 2): one chain is 2103x
slower, the whole batch 4x slower than one core.

## Table 3: the UNSAT posterior against kissat (uf250-1065 against uuf250-1065, 20 + 20 instances)

Loop in walk mode at the polish's budget (one heuristic restart = one tilted_walk restart), half
the groups rigorous, cap 60 s, prior P(SAT) = 0.5, Beta(0.455, 0.828) fitted by moments on the 40
tilted_walk fractions above (mean 0.354). The Beta-mixture posterior after k failed heuristic
restarts, and where the instances were:

| time | posterior on every uuf instance | uf instances still running | uuf instances | actually UNSAT among those reporting |
|---|---|---|---|---|
| 1 s (step 1, k = 256) | 0.940 | 3 of 20 (17 solved in step 1 at 0.78 s) | 20 | 18 of 38 = 0.47 |
| 5 s | 0.973 | 1 of 20 | 20 | 20 of 40 = 0.50 at each instance's last value |
| 45 s | 0.990 | 1 of 20 (solved at 42.6 s, posterior 0.990) | 20 | 18 of 18 above 0.99 |
| 60 s (cap) | 0.991 | 0 of 20 | 20 | 18 of 18 above 0.99; 2 below (53 and 57 steps) |

The posterior is the same number on every instance at a given step: it is a function of k alone,
0.93 to 0.94 after the first step on satisfiable and unsatisfiable instances alike, 0.99 after
17,700 to 20,000 failures. Time to 0.99: 18 of 20 uuf instances at 44.6 to 51.5 s (median 45.3 s),
2 never within the cap; kissat refutes the same instances in 1.16 to 4.23 s (median 2.52 s,
fastest of three, exit 20): median ratio 18.4. Satisfiable side: 17 solved in step 1, 2 in step 2,
1 at step 55 with the posterior at 0.990 when its solution arrived; posteriors at the moment of
solution 0.93 to 0.99. The rigorous posterior stayed at 0.5 throughout (Schöning's bound at
n = 250 is (3/4)^250 / 2253 = 2.7e-35 per try).

## What the tables show

The sampler half of the loop works as the theory says, and neither half pays. With annealed
weights the loop's gradient is a consistent estimate of E_tilted[x] minus p (Table 1); with the
walk it estimates nothing at any batch size. As a seed of the same polish, the consistent loop
raises the per-restart success by 2 %, 8 % and 11 % on uf50, uf100 and uf250 (22, 31 and 21 of 40
runs above a uniform start) while spending 1000n proposals per slot, a hundred times the polish's
budget, so its expected time to a solution is 100x, 87x and 73x a uniform start's; its chains
never reached a solution at n = 250 and its ESS fell below the schedule's floor there (6.8 of 32).
The biased walk-mode loop is the only seed that changes p by a large factor, 0.086 to 0.354 on
uf250 (29 of 40, and 28 of 40 above mu), but it does so by running 1000n SKC flips per slot, and
per unit of cost it is 17x worse than a uniform start; it is the cross-entropy method with the
walk as elite generator, and what it measures is that the walk solves uf250 by itself in 37 of 40
seeding runs. mu ascent is the only seed that helps at all per unit of cost: +7 %, +13 % and +31 %
in p (33, 30 and 26 of 40 runs), growing with n as the basin experiment found, at 2 to 3x the cost
per restart, so still 1.7 to 2.5x a uniform start's expected time; all false equals uniform. No
seed beats a uniform start on expected time on any family. On the UNSAT side the Beta-mixture
posterior is a clock, not a test: it reads the same on satisfiable and unsatisfiable instances at
every step, says 0.94 after one step on both, reaches 0.99 after 45 s where kissat refutes in
2.5 s, and its calibration fails in the review's predicted direction, over-confidence, at every
time before the cap (0.94 claimed against 0.47 observed at 1 s). What separates the two families
in this run is not the posterior but the loop itself: 19 of 20 satisfiable instances solved within
1.6 s and none of the unsatisfiable ones; the one hard satisfiable instance took 42.6 s and would
have been called UNSAT at 0.99 four seconds later.

## Caveats

- One GPU, seeds {0, 1}, 20 instances per family, no confidence intervals; the contention detector
  is the uniform arm's polish time, not a log of other processes.
- **The kernel is launch-bound (about 15 kernel launches per flip, 3k flips per second per
  chain), and every seed that runs the walk inside its steps pays that overhead 500 times over:**
  the cost columns of the tilted and tilted_walk rows are this implementation's, not the
  algorithm's. A fused kernel (the C++ port) would cut their seeding cost by the same factor as
  the polish, so the p column and the flips-per-slot column are what survive a port; the expected
  times do not, and per unit of flips the verdict is unchanged (tilted_walk spends 25x the flips
  per satisfied slot of a uniform start on uf250).
- The polish is the repository's flip kernel, not probSAT (three orders of magnitude slower per
  chain). Putikhin and Kascheev (EWDTS 2017) seeded probSAT itself with a different continuous
  extension; this is a replication with a different local search and seed, and their per-restart
  number is not published.
- The tilted seed draws its 512 slots from q_theta after T steps; rounding sign(p) per group
  (16 distinct starts) was not measured. T = 500, 2n moves per step, the beta schedule and every
  other constant were set once and never tuned; no decimation, no proposal correction beyond
  AIS, the Luby schedule kept on faith (`method/not-built.md`).
- The Beta prior was fitted on the tilted_walk arm's fractions after 500 seeding steps, while the
  calibration loop's early restarts come from a fresh theta; the moment fit gave a < 1, whose
  marginal likelihood decays as k^(-0.45), which is why 0.99 takes 20,000 failures. A prior with
  mass at p = 0 (a family-level survival function is a mixture) is the review's step 2, unmeasured.
- The rigorous groups spent half the slots on a bound that cannot move at n = 250; they are in the
  run because the brief asked for them.
