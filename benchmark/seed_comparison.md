# Seed comparison in C++: per-restart success of one polish from five seeds, probSAT beside it

- First record 2026-08-29T17:44:03; commit 040ea98efb; binary sha256 c3a97ba6bb8be97e; backend cuda; GPU at start: NVIDIA GeForce RTX 4060 Laptop GPU, 12 MiB, 0 %.
- 4096 slots per run, polish = 10 n SKC flips (noise 0.5), the ascent = the library's projected gradient with its defaults for 50, 200 or 500 iterations rounded by sign; instances: the first 20 of each family in name order; seeds [0, 1].
- p = mean over runs of the fraction of slots satisfied after the polish; cost = median over runs of (seed seconds + polish seconds) / slots, from the solver's own clocks; expected time = cost / p. probSAT: wall seconds of one run to a solution (its default flip and try limits), mean and median over instances and seeds, which is a draw of its expected time to a solution (process start and parse included); its mean flips per solution sit in the cost column, against polish flips / p for the walk.

| family | seed | runs | p | runs with p > 0 | runs with p above uniform's | cost / restart (ms) | expected time (ms) | seed s | polish s |
|---|---|---|---|---|---|---|---|---|---|
| uf50-218 | uniform | 40 | 0.5448 | 40/40 | 0/40 | 0.0027 | 0.005 | 0.000 | 0.010 |
| uf50-218 | all_false | 40 | 0.5581 | 40/40 | 22/40 | 0.0026 | 0.005 | 0.000 | 0.010 |
| uf50-218 | ascent50 | 40 | 0.5821 | 40/40 | 39/40 | 0.0045 | 0.008 | 0.009 | 0.010 |
| uf50-218 | ascent200 | 40 | 0.5865 | 40/40 | 39/40 | 0.0110 | 0.019 | 0.035 | 0.010 |
| uf50-218 | ascent500 | 40 | 0.5873 | 40/40 | 39/40 | 0.0237 | 0.040 | 0.087 | 0.010 |
| uf50-218 | probSAT, one core | 40 | solved 40/40 | - | - | mean 0.7 k flips | mean 3.92, median 4.10 | - | - |
| uf100-430 | uniform | 40 | 0.2985 | 40/40 | 0/40 | 0.0071 | 0.024 | 0.000 | 0.029 |
| uf100-430 | all_false | 40 | 0.2956 | 40/40 | 15/40 | 0.0071 | 0.024 | 0.000 | 0.029 |
| uf100-430 | ascent50 | 40 | 0.3358 | 40/40 | 35/40 | 0.0105 | 0.031 | 0.015 | 0.028 |
| uf100-430 | ascent200 | 40 | 0.3380 | 40/40 | 34/40 | 0.0211 | 0.062 | 0.058 | 0.028 |
| uf100-430 | ascent500 | 40 | 0.3399 | 40/40 | 37/40 | 0.0422 | 0.124 | 0.145 | 0.028 |
| uf100-430 | probSAT, one core | 40 | solved 40/40 | - | - | mean 6.8 k flips | mean 6.71, median 5.95 | - | - |
| uf250-1065 | uniform | 40 | 0.0856 | 39/40 | 0/40 | 0.0227 | 0.265 | 0.000 | 0.093 |
| uf250-1065 | all_false | 40 | 0.0884 | 38/40 | 14/40 | 0.0227 | 0.257 | 0.000 | 0.092 |
| uf250-1065 | ascent50 | 40 | 0.1096 | 38/40 | 36/40 | 0.0311 | 0.284 | 0.034 | 0.092 |
| uf250-1065 | ascent200 | 40 | 0.1125 | 39/40 | 36/40 | 0.0561 | 0.499 | 0.136 | 0.092 |
| uf250-1065 | ascent500 | 40 | 0.1135 | 38/40 | 36/40 | 0.1057 | 0.932 | 0.340 | 0.092 |
| uf250-1065 | probSAT, one core | 40 | solved 40/40 | - | - | mean 75.6 k flips | mean 17.93, median 8.15 | - | - |

Every run is in seed_comparison.jsonl with its command, seed, commit, binary hash and timestamp.
