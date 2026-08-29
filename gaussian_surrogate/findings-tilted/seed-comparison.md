# Table 2: per-restart success of one polish from five seeds

Part of [the findings of the tilted loop](README.md); the sections read in that file's order.

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
