# The front: the arms no other arm dominates, with their numbers

- 17 stages from 2026-08-29T20:58:20 to 2026-08-29T23:15:59; frozen binary multilinear-sat-4b98f0a2ea-20260829-205205 (sha256 fd00a7139329af3a), multilinear-sat-67c51ca66a-20260829-205205 (sha256 fd00a7139329af3a), multilinear-sat-f15c737875-20260829-205205 (sha256 fd00a7139329af3a), named by the commit it was built from; HEAD at the stages: 10ec02cb75, 339ee7f1d0, 4b98f0a2ea, 672b5acee5, 674ca584d7, 9092e76858, dc063e6e07, f15c737875; GPU at the first stage: NVIDIA GeForce RTX 4060 Laptop GPU, 12 MiB, 0 %.
- Every run is in arms_results.jsonl with its command, seed, timeline, package temperature before and after, and the gate readings of its stage.
- Rule: [protocol.md](protocol.md); two cells are distinguished only when their ratio exceeds the 13% thermal band and two standard errors of the log ratio under Poisson success counts, exp(2 sqrt(1/k_a + 1/k_b)); an arm dominates only arms it was measured beside on every one of their families.

## Overall

- **base** (seed=uniform, rule=probsat, batch=4096, schedule=luby, polish_per_variable=10, rigorous=0.0), measured on uf50-218, uf100-430, uf250-1065, n1000-r4.20, n1000-r4.26, n5000-r4.20
- **ascent_10** (seed=ascent_10, rule=probsat, batch=4096, schedule=luby, polish_per_variable=10, rigorous=0.0), measured on uf250-1065, n1000-r4.20, n1000-r4.26
- **ascent_30** (seed=ascent_30, rule=probsat, batch=4096, schedule=luby, polish_per_variable=10, rigorous=0.0), measured on uf250-1065, n1000-r4.20, n1000-r4.26
- **batch_16384** (seed=uniform, rule=probsat, batch=16384, schedule=luby, polish_per_variable=10, rigorous=0.0), measured on uf250-1065, n1000-r4.20, n1000-r4.26
- **polish_100n** (seed=uniform, rule=probsat, batch=4096, schedule=luby, polish_per_variable=100, rigorous=0.0), measured on n1000-r4.20

## Per family: every arm on the family's front, then probSAT beside it

### uf50-218: 20 satisfiable, 0 unsatisfiable, 0 undecided of 20 instances (cells over the satisfiable ones)

| family | arm | runs | satisfied slot-runs | p | cost / restart (ms) | expected time (ms) | flips per solution | median first solution (ms) | package C |
|---|---|---|---|---|---|---|---|---|---|
| uf50-218 | base | 40 on 20 instances | 796199 | 0.6942 | 0.0045 | 0.006 | 586 | 79.0 | 47 to 50 |

| family | arm | runs | | | wall ms per solution | flips per solution | |
|---|---|---|---|---|---|---|---|
| uf50-218 | probSAT, one core | 40/40 solved | - | - | mean 10.39, median 10.60 | 742 | - |

### uf100-430: 20 satisfiable, 0 unsatisfiable, 0 undecided of 20 instances (cells over the satisfiable ones)

| family | arm | runs | satisfied slot-runs | p | cost / restart (ms) | expected time (ms) | flips per solution | median first solution (ms) | package C |
|---|---|---|---|---|---|---|---|---|---|
| uf100-430 | base | 40 on 20 instances | 545462 | 0.4756 | 0.0139 | 0.029 | 2422 | 104.0 | 48 to 53 |

| family | arm | runs | | | wall ms per solution | flips per solution | |
|---|---|---|---|---|---|---|---|
| uf100-430 | probSAT, one core | 40/40 solved | - | - | mean 11.71, median 11.25 | 6802 | - |

### uf250-1065: 20 satisfiable, 0 unsatisfiable, 0 undecided of 20 instances (cells over the satisfiable ones)

| family | arm | runs | satisfied slot-runs | p | cost / restart (ms) | expected time (ms) | flips per solution | median first solution (ms) | package C |
|---|---|---|---|---|---|---|---|---|---|
| uf250-1065 | batch_16384 | 40 on 20 instances | 1051342 | 0.2292 | 0.0268 | 0.117 | 15912 | 372.5 | 59 to 79 |

| family | arm | runs | | | wall ms per solution | flips per solution | |
|---|---|---|---|---|---|---|---|
| uf250-1065 | probSAT, one core | 40/40 solved | - | - | mean 24.15, median 16.50 | 75632 | - |

### n1000-r4.20: 4 satisfiable, 0 unsatisfiable, 1 undecided of 5 instances (cells over the satisfiable ones)

| family | arm | runs | satisfied slot-runs | p | cost / restart (ms) | expected time (ms) | flips per solution | median first solution (ms) | package C |
|---|---|---|---|---|---|---|---|---|---|
| n1000-r4.20 | polish_100n | 8 on 4 instances | 2451 | 0.01069 | 2.7385 | 256.283 | 15937564 | 6639.0 | 47 to 65 |

| family | arm | runs | | | wall ms per solution | flips per solution | |
|---|---|---|---|---|---|---|---|
| n1000-r4.20 | probSAT, one core | 8/8 solved | - | - | mean 1849.42, median 2299.70 | 10605418 | - |

### n1000-r4.26: 3 satisfiable, 0 unsatisfiable, 2 undecided of 5 instances (cells over the satisfiable ones)

| family | arm | runs | satisfied slot-runs | p | cost / restart (ms) | expected time (ms) | flips per solution | median first solution (ms) | package C |
|---|---|---|---|---|---|---|---|---|---|
| n1000-r4.26 | ascent_10 | 6 on 3 instances | 1488 | 0.00865 | 0.2999 | 34.675 | 1972692 | 1883.5 | 59 to 87 |
| n1000-r4.26 | ascent_30 | 6 on 3 instances | 1537 | 0.008934 | 0.3472 | 38.862 | 1909218 | 904.5 | 66 to 83 |

| family | arm | runs | | | wall ms per solution | flips per solution | |
|---|---|---|---|---|---|---|---|
| n1000-r4.26 | probSAT, one core | 6/6 solved | - | - | mean 2909.47, median 76.20 | 16741861 | - |

### n5000-r4.20: 5 satisfiable, 0 unsatisfiable, 0 undecided of 5 instances (cells over the satisfiable ones)

| family | arm | runs | satisfied slot-runs | p | cost / restart (ms) | expected time (ms) | flips per solution | median first solution (ms) | package C |
|---|---|---|---|---|---|---|---|---|---|
| n5000-r4.20 | base | 10 on 5 instances | 0 | 0 | 1.8451 | inf | inf | inf | 47 to 81 |

| family | arm | runs | | | wall ms per solution | flips per solution | |
|---|---|---|---|---|---|---|---|
| n5000-r4.20 | probSAT, one core | 10/10 solved | - | - | mean 2056.62, median 1857.55 | 10619433 | - |

### n5000-r4.26: no instance decided satisfiable of 5 (0 unsatisfiable, the rest undecided: probSAT capped, CaDiCaL without a verdict, no walk certificate); no cell

