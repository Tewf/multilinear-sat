# The rejected arms, each with the arm that dominates it and the numbers

- 19 stages from 2026-08-29T20:58:20 to 2026-08-29T23:35:39; frozen binary multilinear-sat-4b98f0a2ea-20260829-205205 (sha256 fd00a7139329af3a), multilinear-sat-67c51ca66a-20260829-205205 (sha256 fd00a7139329af3a), multilinear-sat-7c32b6f259-20260829-205205 (sha256 fd00a7139329af3a), multilinear-sat-8124137c0d-20260829-205205 (sha256 fd00a7139329af3a), multilinear-sat-f15c737875-20260829-205205 (sha256 fd00a7139329af3a), named by the commit it was built from; HEAD at the stages: 10ec02cb75, 339ee7f1d0, 4b98f0a2ea, 672b5acee5, 674ca584d7, 6c97ae1769, 7c32b6f259, 9092e76858, dc063e6e07, f15c737875; GPU at the first stage: NVIDIA GeForce RTX 4060 Laptop GPU, 12 MiB, 0 %.
- Every run is in arms_results.jsonl with its command, seed, timeline, package temperature before and after, and the gate readings of its stage.
- An arm is dominated when another arm, measured on every family it was measured on, is at least as good on expected time on each and strictly better on one, or not distinguished on expected time anywhere and better on p on one; distinguished means beyond the 13% thermal band and beyond two standard errors of the log ratio under Poisson success counts (the satisfied slot-runs column). Nothing is deleted: every rejected arm keeps its cells here beside its dominator's.

## all_false (seed=all_false, rule=probsat, batch=4096, schedule=luby, polish_per_variable=10, rigorous=0.0)
- dominated by **base** on n1000-r4.26
- dominated by **ascent_10** on n1000-r4.26
- dominated by **ascent_30** on n1000-r4.26
- dominated by **ascent_50** on n1000-r4.20, n1000-r4.26
- dominated by **batch_16384** on uf250-1065

| family | arm | runs | satisfied slot-runs | p | cost / restart (ms) | expected time (ms) | flips per solution | median first solution (ms) | package C |
|---|---|---|---|---|---|---|---|---|---|
| uf250-1065 | all_false | 40 on 20 instances | 251791 | 0.2195 | 0.0516 | 0.235 | 16739 | 200.0 | 57 to 91 |
| uf250-1065 | base | 40 on 20 instances | 263316 | 0.2296 | 0.0514 | 0.224 | 15880 | 197.0 | 48 to 57 |
| uf250-1065 | ascent_10 | 40 on 20 instances | 288410 | 0.2515 | 0.0537 | 0.214 | 14136 | 209.5 | 49 to 69 |
| uf250-1065 | ascent_30 | 40 on 20 instances | 291583 | 0.2542 | 0.0596 | 0.235 | 13951 | 221.0 | 57 to 88 |
| uf250-1065 | ascent_50 | 40 on 20 instances | 292493 | 0.255 | 0.0653 | 0.256 | 13886 | 235.0 | 59 to 80 |
| uf250-1065 | batch_16384 | 40 on 20 instances | 1051342 | 0.2292 | 0.0268 | 0.117 | 15912 | 372.5 | 59 to 79 |
| n1000-r4.20 | all_false | 8 on 4 instances | 2 | 8.719e-06 | 0.2763 | 31683.000 | 1966069856 | 7980.5 | 66 to 69 |
| n1000-r4.20 | base | 8 on 4 instances | 7 | 3.052e-05 | 0.2749 | 9006.857 | 561729861 | 7957.0 | 48 to 67 |
| n1000-r4.20 | ascent_10 | 8 on 4 instances | 10 | 4.36e-05 | 0.2984 | 6845.400 | 393208969 | 8604.5 | 55 to 64 |
| n1000-r4.20 | ascent_30 | 8 on 4 instances | 6 | 2.616e-05 | 0.3454 | 13205.167 | 655349646 | 9990.0 | 64 to 77 |
| n1000-r4.20 | ascent_50 | 8 on 4 instances | 14 | 6.104e-05 | 0.3930 | 6438.571 | 280858840 | 11317.0 | 67 to 91 |
| n1000-r4.20 | batch_16384 | 8 on 4 instances | 29 | 3.161e-05 | 0.4860 | 15376.276 | 542357752 | 55721.0 | 63 to 96 |
| n1000-r4.26 | all_false | 6 on 3 instances | 783 | 0.004551 | 0.2767 | 60.797 | 3758125 | 2726.0 | 63 to 86 |
| n1000-r4.26 | base | 6 on 3 instances | 1217 | 0.007074 | 0.2766 | 39.104 | 2414070 | 1071.5 | 63 to 93 |
| n1000-r4.26 | ascent_10 | 6 on 3 instances | 1488 | 0.00865 | 0.2999 | 34.675 | 1972692 | 1883.5 | 59 to 87 |
| n1000-r4.26 | ascent_30 | 6 on 3 instances | 1537 | 0.008934 | 0.3472 | 38.862 | 1909218 | 904.5 | 66 to 83 |
| n1000-r4.26 | ascent_50 | 6 on 3 instances | 1626 | 0.009452 | 0.3956 | 41.851 | 1804584 | 1014.5 | 66 to 95 |
| n1000-r4.26 | batch_16384 | 6 on 3 instances | 4963 | 0.007212 | 0.4873 | 67.565 | 2367959 | 4789.0 | 68 to 96 |

## ascent_50 (seed=ascent_50, rule=probsat, batch=4096, schedule=luby, polish_per_variable=10, rigorous=0.0)
- dominated by **base** on uf250-1065
- dominated by **ascent_10** on uf250-1065, n1000-r4.26

| family | arm | runs | satisfied slot-runs | p | cost / restart (ms) | expected time (ms) | flips per solution | median first solution (ms) | package C |
|---|---|---|---|---|---|---|---|---|---|
| uf250-1065 | ascent_50 | 40 on 20 instances | 292493 | 0.255 | 0.0653 | 0.256 | 13886 | 235.0 | 59 to 80 |
| uf250-1065 | base | 40 on 20 instances | 263316 | 0.2296 | 0.0514 | 0.224 | 15880 | 197.0 | 48 to 57 |
| uf250-1065 | ascent_10 | 40 on 20 instances | 288410 | 0.2515 | 0.0537 | 0.214 | 14136 | 209.5 | 49 to 69 |
| n1000-r4.20 | ascent_50 | 8 on 4 instances | 14 | 6.104e-05 | 0.3930 | 6438.571 | 280858840 | 11317.0 | 67 to 91 |
| n1000-r4.20 | base | 8 on 4 instances | 7 | 3.052e-05 | 0.2749 | 9006.857 | 561729861 | 7957.0 | 48 to 67 |
| n1000-r4.20 | ascent_10 | 8 on 4 instances | 10 | 4.36e-05 | 0.2984 | 6845.400 | 393208969 | 8604.5 | 55 to 64 |
| n1000-r4.26 | ascent_50 | 6 on 3 instances | 1626 | 0.009452 | 0.3956 | 41.851 | 1804584 | 1014.5 | 66 to 95 |
| n1000-r4.26 | base | 6 on 3 instances | 1217 | 0.007074 | 0.2766 | 39.104 | 2414070 | 1071.5 | 63 to 93 |
| n1000-r4.26 | ascent_10 | 6 on 3 instances | 1488 | 0.00865 | 0.2999 | 34.675 | 1972692 | 1883.5 | 59 to 87 |

## ascent_200 (seed=ascent_200, rule=probsat, batch=4096, schedule=luby, polish_per_variable=10, rigorous=0.0)
- dominated by **base** on uf250-1065, n1000-r4.26
- dominated by **all_false** on uf250-1065, n1000-r4.26
- dominated by **ascent_10** on uf250-1065, n1000-r4.26
- dominated by **ascent_30** on uf250-1065, n1000-r4.26
- dominated by **ascent_50** on uf250-1065, n1000-r4.20, n1000-r4.26
- dominated by **batch_16384** on uf250-1065, n1000-r4.26

| family | arm | runs | satisfied slot-runs | p | cost / restart (ms) | expected time (ms) | flips per solution | median first solution (ms) | package C |
|---|---|---|---|---|---|---|---|---|---|
| uf250-1065 | ascent_200 | 40 on 20 instances | 294168 | 0.2565 | 0.1101 | 0.429 | 13784 | 338.0 | 61 to 83 |
| uf250-1065 | base | 40 on 20 instances | 263316 | 0.2296 | 0.0514 | 0.224 | 15880 | 197.0 | 48 to 57 |
| uf250-1065 | all_false | 40 on 20 instances | 251791 | 0.2195 | 0.0516 | 0.235 | 16739 | 200.0 | 57 to 91 |
| uf250-1065 | ascent_10 | 40 on 20 instances | 288410 | 0.2515 | 0.0537 | 0.214 | 14136 | 209.5 | 49 to 69 |
| uf250-1065 | ascent_30 | 40 on 20 instances | 291583 | 0.2542 | 0.0596 | 0.235 | 13951 | 221.0 | 57 to 88 |
| uf250-1065 | ascent_50 | 40 on 20 instances | 292493 | 0.255 | 0.0653 | 0.256 | 13886 | 235.0 | 59 to 80 |
| uf250-1065 | batch_16384 | 40 on 20 instances | 1051342 | 0.2292 | 0.0268 | 0.117 | 15912 | 372.5 | 59 to 79 |
| n1000-r4.20 | ascent_200 | 8 on 4 instances | 12 | 5.232e-05 | 0.7675 | 14670.500 | 327673475 | 22042.0 | 68 to 73 |
| n1000-r4.20 | base | 8 on 4 instances | 7 | 3.052e-05 | 0.2749 | 9006.857 | 561729861 | 7957.0 | 48 to 67 |
| n1000-r4.20 | all_false | 8 on 4 instances | 2 | 8.719e-06 | 0.2763 | 31683.000 | 1966069856 | 7980.5 | 66 to 69 |
| n1000-r4.20 | ascent_10 | 8 on 4 instances | 10 | 4.36e-05 | 0.2984 | 6845.400 | 393208969 | 8604.5 | 55 to 64 |
| n1000-r4.20 | ascent_30 | 8 on 4 instances | 6 | 2.616e-05 | 0.3454 | 13205.167 | 655349646 | 9990.0 | 64 to 77 |
| n1000-r4.20 | ascent_50 | 8 on 4 instances | 14 | 6.104e-05 | 0.3930 | 6438.571 | 280858840 | 11317.0 | 67 to 91 |
| n1000-r4.20 | batch_16384 | 8 on 4 instances | 29 | 3.161e-05 | 0.4860 | 15376.276 | 542357752 | 55721.0 | 63 to 96 |
| n1000-r4.26 | ascent_200 | 6 on 3 instances | 1590 | 0.009242 | 0.7786 | 84.243 | 1844909 | 1915.0 | 69 to 74 |
| n1000-r4.26 | base | 6 on 3 instances | 1217 | 0.007074 | 0.2766 | 39.104 | 2414070 | 1071.5 | 63 to 93 |
| n1000-r4.26 | all_false | 6 on 3 instances | 783 | 0.004551 | 0.2767 | 60.797 | 3758125 | 2726.0 | 63 to 86 |
| n1000-r4.26 | ascent_10 | 6 on 3 instances | 1488 | 0.00865 | 0.2999 | 34.675 | 1972692 | 1883.5 | 59 to 87 |
| n1000-r4.26 | ascent_30 | 6 on 3 instances | 1537 | 0.008934 | 0.3472 | 38.862 | 1909218 | 904.5 | 66 to 83 |
| n1000-r4.26 | ascent_50 | 6 on 3 instances | 1626 | 0.009452 | 0.3956 | 41.851 | 1804584 | 1014.5 | 66 to 95 |
| n1000-r4.26 | batch_16384 | 6 on 3 instances | 4963 | 0.007212 | 0.4873 | 67.565 | 2367959 | 4789.0 | 68 to 96 |

## skc (seed=uniform, rule=skc, batch=4096, schedule=luby, polish_per_variable=10, rigorous=0.0)
- dominated by **base** on n1000-r4.20, n1000-r4.26
- dominated by **all_false** on n1000-r4.20, n1000-r4.26
- dominated by **ascent_10** on uf250-1065, n1000-r4.20, n1000-r4.26
- dominated by **ascent_30** on n1000-r4.20, n1000-r4.26
- dominated by **ascent_50** on n1000-r4.20, n1000-r4.26
- dominated by **batch_16384** on uf250-1065, n1000-r4.20, n1000-r4.26

| family | arm | runs | satisfied slot-runs | p | cost / restart (ms) | expected time (ms) | flips per solution | median first solution (ms) | package C |
|---|---|---|---|---|---|---|---|---|---|
| uf250-1065 | skc | 40 on 20 instances | 173531 | 0.1513 | 0.0372 | 0.246 | 25543 | 160.0 | 57 to 73 |
| uf250-1065 | base | 40 on 20 instances | 263316 | 0.2296 | 0.0514 | 0.224 | 15880 | 197.0 | 48 to 57 |
| uf250-1065 | all_false | 40 on 20 instances | 251791 | 0.2195 | 0.0516 | 0.235 | 16739 | 200.0 | 57 to 91 |
| uf250-1065 | ascent_10 | 40 on 20 instances | 288410 | 0.2515 | 0.0537 | 0.214 | 14136 | 209.5 | 49 to 69 |
| uf250-1065 | ascent_30 | 40 on 20 instances | 291583 | 0.2542 | 0.0596 | 0.235 | 13951 | 221.0 | 57 to 88 |
| uf250-1065 | ascent_50 | 40 on 20 instances | 292493 | 0.255 | 0.0653 | 0.256 | 13886 | 235.0 | 59 to 80 |
| uf250-1065 | batch_16384 | 40 on 20 instances | 1051342 | 0.2292 | 0.0268 | 0.117 | 15912 | 372.5 | 59 to 79 |
| n1000-r4.20 | skc | 8 on 4 instances | 0 | 0 | 0.2054 | inf | inf | inf | 58 to 91 |
| n1000-r4.20 | base | 8 on 4 instances | 7 | 3.052e-05 | 0.2749 | 9006.857 | 561729861 | 7957.0 | 48 to 67 |
| n1000-r4.20 | all_false | 8 on 4 instances | 2 | 8.719e-06 | 0.2763 | 31683.000 | 1966069856 | 7980.5 | 66 to 69 |
| n1000-r4.20 | ascent_10 | 8 on 4 instances | 10 | 4.36e-05 | 0.2984 | 6845.400 | 393208969 | 8604.5 | 55 to 64 |
| n1000-r4.20 | ascent_30 | 8 on 4 instances | 6 | 2.616e-05 | 0.3454 | 13205.167 | 655349646 | 9990.0 | 64 to 77 |
| n1000-r4.20 | ascent_50 | 8 on 4 instances | 14 | 6.104e-05 | 0.3930 | 6438.571 | 280858840 | 11317.0 | 67 to 91 |
| n1000-r4.20 | batch_16384 | 8 on 4 instances | 29 | 3.161e-05 | 0.4860 | 15376.276 | 542357752 | 55721.0 | 63 to 96 |
| n1000-r4.26 | skc | 6 on 3 instances | 55 | 0.0003197 | 0.2072 | 648.127 | 53610070 | 2044.5 | 57 to 71 |
| n1000-r4.26 | base | 6 on 3 instances | 1217 | 0.007074 | 0.2766 | 39.104 | 2414070 | 1071.5 | 63 to 93 |
| n1000-r4.26 | all_false | 6 on 3 instances | 783 | 0.004551 | 0.2767 | 60.797 | 3758125 | 2726.0 | 63 to 86 |
| n1000-r4.26 | ascent_10 | 6 on 3 instances | 1488 | 0.00865 | 0.2999 | 34.675 | 1972692 | 1883.5 | 59 to 87 |
| n1000-r4.26 | ascent_30 | 6 on 3 instances | 1537 | 0.008934 | 0.3472 | 38.862 | 1909218 | 904.5 | 66 to 83 |
| n1000-r4.26 | ascent_50 | 6 on 3 instances | 1626 | 0.009452 | 0.3956 | 41.851 | 1804584 | 1014.5 | 66 to 95 |
| n1000-r4.26 | batch_16384 | 6 on 3 instances | 4963 | 0.007212 | 0.4873 | 67.565 | 2367959 | 4789.0 | 68 to 96 |

## fixed_cutoff (seed=uniform, rule=probsat, batch=4096, schedule=fixed, polish_per_variable=10, rigorous=0.0)
- dominated by **base** on uf250-1065
- dominated by **all_false** on uf250-1065
- dominated by **ascent_10** on uf250-1065
- dominated by **ascent_30** on uf250-1065
- dominated by **batch_16384** on uf250-1065
- dominated by **polish_20n** on uf250-1065
- dominated by **batch_16384+polish_20n** on uf250-1065

| family | arm | runs | satisfied slot-runs | p | cost / restart (ms) | expected time (ms) | flips per solution | median first solution (ms) | package C |
|---|---|---|---|---|---|---|---|---|---|
| uf250-1065 | fixed_cutoff | 40 on 20 instances | 279320 | 0.1421 | 0.0319 | 0.224 | 16701 | 197.0 | 55 to 62 |
| uf250-1065 | base | 40 on 20 instances | 263316 | 0.2296 | 0.0514 | 0.224 | 15880 | 197.0 | 48 to 57 |
| uf250-1065 | all_false | 40 on 20 instances | 251791 | 0.2195 | 0.0516 | 0.235 | 16739 | 200.0 | 57 to 91 |
| uf250-1065 | ascent_10 | 40 on 20 instances | 288410 | 0.2515 | 0.0537 | 0.214 | 14136 | 209.5 | 49 to 69 |
| uf250-1065 | ascent_30 | 40 on 20 instances | 291583 | 0.2542 | 0.0596 | 0.235 | 13951 | 221.0 | 57 to 88 |
| uf250-1065 | batch_16384 | 40 on 20 instances | 1051342 | 0.2292 | 0.0268 | 0.117 | 15912 | 372.5 | 59 to 79 |
| uf250-1065 | polish_20n | 40 on 20 instances | 439146 | 0.3829 | 0.0946 | 0.247 | 16437 | 324.5 | 58 to 61 |
| uf250-1065 | batch_16384+polish_20n | 40 on 20 instances | 1755650 | 0.3827 | 0.0460 | 0.120 | 16452 | 609.0 | 54 to 96 |

## no_restart (seed=uniform, rule=probsat, batch=4096, schedule=none, polish_per_variable=10, rigorous=0.0)
- dominated by **base** on uf250-1065
- dominated by **all_false** on uf250-1065
- dominated by **ascent_10** on uf250-1065
- dominated by **ascent_30** on uf250-1065
- dominated by **ascent_50** on uf250-1065
- dominated by **skc** on uf250-1065
- dominated by **batch_16384** on uf250-1065
- dominated by **fixed_cutoff** on uf250-1065
- dominated by **polish_5n** on uf250-1065
- dominated by **polish_20n** on uf250-1065
- dominated by **batch_16384+polish_20n** on uf250-1065

| family | arm | runs | satisfied slot-runs | p | cost / restart (ms) | expected time (ms) | flips per solution | median first solution (ms) | package C |
|---|---|---|---|---|---|---|---|---|---|
| uf250-1065 | no_restart | 40 on 20 instances | 112637 | 0.6875 | 0.2672 | 0.389 | 22519 | 1344.0 | 58 to 61 |
| uf250-1065 | base | 40 on 20 instances | 263316 | 0.2296 | 0.0514 | 0.224 | 15880 | 197.0 | 48 to 57 |
| uf250-1065 | all_false | 40 on 20 instances | 251791 | 0.2195 | 0.0516 | 0.235 | 16739 | 200.0 | 57 to 91 |
| uf250-1065 | ascent_10 | 40 on 20 instances | 288410 | 0.2515 | 0.0537 | 0.214 | 14136 | 209.5 | 49 to 69 |
| uf250-1065 | ascent_30 | 40 on 20 instances | 291583 | 0.2542 | 0.0596 | 0.235 | 13951 | 221.0 | 57 to 88 |
| uf250-1065 | ascent_50 | 40 on 20 instances | 292493 | 0.255 | 0.0653 | 0.256 | 13886 | 235.0 | 59 to 80 |
| uf250-1065 | skc | 40 on 20 instances | 173531 | 0.1513 | 0.0372 | 0.246 | 25543 | 160.0 | 57 to 73 |
| uf250-1065 | batch_16384 | 40 on 20 instances | 1051342 | 0.2292 | 0.0268 | 0.117 | 15912 | 372.5 | 59 to 79 |
| uf250-1065 | fixed_cutoff | 40 on 20 instances | 279320 | 0.1421 | 0.0319 | 0.224 | 16701 | 197.0 | 55 to 62 |
| uf250-1065 | polish_5n | 40 on 20 instances | 121048 | 0.1055 | 0.0271 | 0.257 | 18959 | 132.0 | 57 to 60 |
| uf250-1065 | polish_20n | 40 on 20 instances | 439146 | 0.3829 | 0.0946 | 0.247 | 16437 | 324.5 | 58 to 61 |
| uf250-1065 | batch_16384+polish_20n | 40 on 20 instances | 1755650 | 0.3827 | 0.0460 | 0.120 | 16452 | 609.0 | 54 to 96 |

## polish_5n (seed=uniform, rule=probsat, batch=4096, schedule=luby, polish_per_variable=5, rigorous=0.0)
- dominated by **base** on uf250-1065
- dominated by **all_false** on uf250-1065
- dominated by **ascent_10** on uf250-1065
- dominated by **ascent_30** on uf250-1065
- dominated by **ascent_50** on uf250-1065
- dominated by **skc** on uf250-1065
- dominated by **batch_16384** on uf250-1065
- dominated by **fixed_cutoff** on uf250-1065
- dominated by **polish_20n** on uf250-1065
- dominated by **batch_16384+polish_20n** on uf250-1065

| family | arm | runs | satisfied slot-runs | p | cost / restart (ms) | expected time (ms) | flips per solution | median first solution (ms) | package C |
|---|---|---|---|---|---|---|---|---|---|
| uf250-1065 | polish_5n | 40 on 20 instances | 121048 | 0.1055 | 0.0271 | 0.257 | 18959 | 132.0 | 57 to 60 |
| uf250-1065 | base | 40 on 20 instances | 263316 | 0.2296 | 0.0514 | 0.224 | 15880 | 197.0 | 48 to 57 |
| uf250-1065 | all_false | 40 on 20 instances | 251791 | 0.2195 | 0.0516 | 0.235 | 16739 | 200.0 | 57 to 91 |
| uf250-1065 | ascent_10 | 40 on 20 instances | 288410 | 0.2515 | 0.0537 | 0.214 | 14136 | 209.5 | 49 to 69 |
| uf250-1065 | ascent_30 | 40 on 20 instances | 291583 | 0.2542 | 0.0596 | 0.235 | 13951 | 221.0 | 57 to 88 |
| uf250-1065 | ascent_50 | 40 on 20 instances | 292493 | 0.255 | 0.0653 | 0.256 | 13886 | 235.0 | 59 to 80 |
| uf250-1065 | skc | 40 on 20 instances | 173531 | 0.1513 | 0.0372 | 0.246 | 25543 | 160.0 | 57 to 73 |
| uf250-1065 | batch_16384 | 40 on 20 instances | 1051342 | 0.2292 | 0.0268 | 0.117 | 15912 | 372.5 | 59 to 79 |
| uf250-1065 | fixed_cutoff | 40 on 20 instances | 279320 | 0.1421 | 0.0319 | 0.224 | 16701 | 197.0 | 55 to 62 |
| uf250-1065 | polish_20n | 40 on 20 instances | 439146 | 0.3829 | 0.0946 | 0.247 | 16437 | 324.5 | 58 to 61 |
| uf250-1065 | batch_16384+polish_20n | 40 on 20 instances | 1755650 | 0.3827 | 0.0460 | 0.120 | 16452 | 609.0 | 54 to 96 |

## polish_20n (seed=uniform, rule=probsat, batch=4096, schedule=luby, polish_per_variable=20, rigorous=0.0)
- dominated by **ascent_10** on uf250-1065
- dominated by **batch_16384** on uf250-1065
- dominated by **batch_16384+polish_20n** on uf250-1065

| family | arm | runs | satisfied slot-runs | p | cost / restart (ms) | expected time (ms) | flips per solution | median first solution (ms) | package C |
|---|---|---|---|---|---|---|---|---|---|
| uf250-1065 | polish_20n | 40 on 20 instances | 439146 | 0.3829 | 0.0946 | 0.247 | 16437 | 324.5 | 58 to 61 |
| uf250-1065 | ascent_10 | 40 on 20 instances | 288410 | 0.2515 | 0.0537 | 0.214 | 14136 | 209.5 | 49 to 69 |
| uf250-1065 | batch_16384 | 40 on 20 instances | 1051342 | 0.2292 | 0.0268 | 0.117 | 15912 | 372.5 | 59 to 79 |
| uf250-1065 | batch_16384+polish_20n | 40 on 20 instances | 1755650 | 0.3827 | 0.0460 | 0.120 | 16452 | 609.0 | 54 to 96 |

## rigorous_half (seed=uniform, rule=probsat, batch=4096, schedule=luby, polish_per_variable=10, rigorous=0.5)
- dominated by **base** on uf250-1065
- dominated by **all_false** on uf250-1065
- dominated by **ascent_10** on uf250-1065
- dominated by **ascent_30** on uf250-1065
- dominated by **ascent_50** on uf250-1065
- dominated by **skc** on uf250-1065
- dominated by **batch_16384** on uf250-1065
- dominated by **fixed_cutoff** on uf250-1065
- dominated by **no_restart** on uf250-1065
- dominated by **polish_5n** on uf250-1065
- dominated by **polish_20n** on uf250-1065
- dominated by **batch_16384+polish_20n** on uf250-1065

| family | arm | runs | satisfied slot-runs | p | cost / restart (ms) | expected time (ms) | flips per solution | median first solution (ms) | package C |
|---|---|---|---|---|---|---|---|---|---|
| uf250-1065 | rigorous_half | 40 on 20 instances | 131586 | 0.2295 | 0.0908 | 0.396 | 19154 | 183.0 | 49 to 78 |
| uf250-1065 | base | 40 on 20 instances | 263316 | 0.2296 | 0.0514 | 0.224 | 15880 | 197.0 | 48 to 57 |
| uf250-1065 | all_false | 40 on 20 instances | 251791 | 0.2195 | 0.0516 | 0.235 | 16739 | 200.0 | 57 to 91 |
| uf250-1065 | ascent_10 | 40 on 20 instances | 288410 | 0.2515 | 0.0537 | 0.214 | 14136 | 209.5 | 49 to 69 |
| uf250-1065 | ascent_30 | 40 on 20 instances | 291583 | 0.2542 | 0.0596 | 0.235 | 13951 | 221.0 | 57 to 88 |
| uf250-1065 | ascent_50 | 40 on 20 instances | 292493 | 0.255 | 0.0653 | 0.256 | 13886 | 235.0 | 59 to 80 |
| uf250-1065 | skc | 40 on 20 instances | 173531 | 0.1513 | 0.0372 | 0.246 | 25543 | 160.0 | 57 to 73 |
| uf250-1065 | batch_16384 | 40 on 20 instances | 1051342 | 0.2292 | 0.0268 | 0.117 | 15912 | 372.5 | 59 to 79 |
| uf250-1065 | fixed_cutoff | 40 on 20 instances | 279320 | 0.1421 | 0.0319 | 0.224 | 16701 | 197.0 | 55 to 62 |
| uf250-1065 | no_restart | 40 on 20 instances | 112637 | 0.6875 | 0.2672 | 0.389 | 22519 | 1344.0 | 58 to 61 |
| uf250-1065 | polish_5n | 40 on 20 instances | 121048 | 0.1055 | 0.0271 | 0.257 | 18959 | 132.0 | 57 to 60 |
| uf250-1065 | polish_20n | 40 on 20 instances | 439146 | 0.3829 | 0.0946 | 0.247 | 16437 | 324.5 | 58 to 61 |
| uf250-1065 | batch_16384+polish_20n | 40 on 20 instances | 1755650 | 0.3827 | 0.0460 | 0.120 | 16452 | 609.0 | 54 to 96 |

## n = 5000: the one-factor arms, not run, the base arm's zero standing for all of them
- ascent_10, ascent_30, all_false, ascent_50, ascent_200, skc, batch_16384, fixed_cutoff, no_restart, polish_5n, polish_20n, rigorous_half: cut on the base stage's own numbers (protocol.md). The base arm found nothing at n = 5000 in the family's budget of 200n flips per slot, so a one-factor change of it would carry the same zero and price nothing; the long-walk arm is the n = 5000 test.

| family | arm | runs | satisfied slot-runs | p | cost / restart (ms) | expected time (ms) | flips per solution | median first solution (ms) | package C |
|---|---|---|---|---|---|---|---|---|---|
| n5000-r4.20 | base | 10 on 5 instances | 0 | 0 | 1.8451 | inf | inf | inf | 47 to 81 |

| family | arm | runs | | | wall ms per solution | flips per solution | |
|---|---|---|---|---|---|---|---|
| n5000-r4.20 | probSAT, one core | 10/10 solved | - | - | mean 2056.62, median 1857.55 | 10619433 | - |

## tilted seed (rejected on the sampling-walk records, not run here)
- On the 7 uf250-1065 runs the tilted arm completed in benchmark/seed_comparison.jsonl, the mean over runs of each run's expected time is 291.5 ms against 2.99 ms for a uniform start on the same (instance, seed) runs, 97x (the record's table, pooling the runs, says 94x); the brief admits it only within 2x of uniform somewhere, so it is not an arm.

