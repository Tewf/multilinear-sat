# The seeds priced per restart, the tilted seed included

Part of [the findings of the walk](README.md); the sections read in that file's order.

## 2. The seeds (`../seed_comparison.md`, commit 26a0ddb)

The Python record's protocol at 4096 slots: 20 instances of each family, seeds 0 and 1, one
polish of 10n SKC flips (noise 0.5) from each seed; p = fraction of slots satisfied after
the polish, cost = (seed + polish seconds) / slots, expected time = cost / p. The ascent is
the library's projected gradient with its defaults for 50, 200 or 500 iterations, rounded by
sign. probSAT: one run to a solution per instance and seed on one core (process start and
parse included), its mean flips per solution beside the walk's polish flips / p.

| family | seed | p | vs uniform | cost / restart (ms) | expected time (ms) | flips per solution |
|---|---|---|---|---|---|---|
| uf50-218 | uniform | 0.5448 | | 0.0027 | 0.005 | 920 |
| uf50-218 | all false | 0.5581 | +2 % | 0.0026 | 0.005 | 900 |
| uf50-218 | ascent 50 / 200 / 500 | 0.5821 / 0.5865 / 0.5873 | +7 / +8 / +8 % | 0.0045 / 0.0110 / 0.0237 | 0.008 / 0.019 / 0.040 | |
| uf50-218 | probSAT, one core | solved 40/40 | | | mean 3.92, median 4.10 | 700 |
| uf100-430 | uniform | 0.2985 | | 0.0071 | 0.024 | 3350 |
| uf100-430 | all false | 0.2956 | -1 % | 0.0071 | 0.024 | 3380 |
| uf100-430 | ascent 50 / 200 / 500 | 0.3358 / 0.3380 / 0.3399 | +12 / +13 / +14 % | 0.0105 / 0.0211 / 0.0422 | 0.031 / 0.062 / 0.124 | |
| uf100-430 | probSAT, one core | solved 40/40 | | | mean 6.71, median 5.95 | 6.8 k |
| uf250-1065 | uniform | 0.0856 | | 0.0227 | 0.265 | 29 200 |
| uf250-1065 | all false | 0.0884 | +3 % | 0.0227 | 0.257 | 28 300 |
| uf250-1065 | ascent 50 / 200 / 500 | 0.1096 / 0.1125 / 0.1135 | +28 / +31 / +33 % | 0.0311 / 0.0561 / 0.1057 | 0.284 / 0.499 / 0.932 | |
| uf250-1065 | probSAT, one core | solved 40/40 | | | mean 17.93, median 8.15 | 75.6 k |

The per-restart success reproduces the Python record to the third decimal (its uniform
0.549 / 0.298 / 0.086, its mu ascent 0.588 / 0.336 / 0.1125), so the seed's lift is the
algorithm's and not an artefact of either implementation. With the walk at the card's speed
the seed's cost is the algorithm's too: at 50 iterations it costs 1.7 / 1.5 / 1.4x a uniform
restart for +7 / +12 / +28 % in p, and the uniform start still wins on expected time at every
size, by 60 % on uf50, 29 % on uf100 and 7 % on uf250; 200 and 500 iterations widen the gap
(1.9x and 3.5x on uf250). The verdict of the record stands with the artefact removed, and
the margin narrows with n: the seed helps most where p is smallest. What the batch buys is
the other column: the expected time to a solution of 4096 chains on uf250 is 0.27 ms against
probSAT's 8 to 18 ms on one core.

## 5. The tilted seed (`../seed_comparison.md`, arm tilted500)

The Python record's loop as a seed: 128 groups of 32 slots, 500 steps of draw, annealing
ladder of 2n Metropolis proposals with AIS weights, and a decreasing step on theta, no control
variate; then the same 10n SKC polish. Run on uf250 first, seeds 0 and 1, and stopped by hand
after 7 of its 120 runs when the package reached 97 C under a 30-minute ceiling on the card.

| runs | seed | p | runs above uniform's | cost / restart (ms) | expected time (ms) |
|---|---|---|---|---|---|
| 7 (uf250-01, 010, 0100, 011; seeds 0 and 1) | tilted, 500 steps | 0.0707 | 4/7 | 2.512 | 35.5 |
| the same 7 | uniform | 0.0598 | | 0.0227 | 0.38 |
| the same 7 | ascent 50 | 0.0850 | | 0.0311 | 0.37 |

On uf250-01 the tilted seed lifts p from 0.19 to 0.22 and 0.24; on the three harder instances
it moves p by less than the binomial spread of 4096 draws. Its restart costs 110x a uniform
one (9.1 to 10.2 s of seeding per run against 0.09 s of polish at 4096 slots), so its
expected time is 94x the uniform start's on the same runs. The Python record measured +11 %
in p at 81x the cost on the full 40 runs of uf250 (`../../gaussian_surrogate/findings-tilted/`,
its seed table); the C++ verdict is the same and the arm stops here.
