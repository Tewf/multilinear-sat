# Walk throughput against probSAT on one core

uuf250-01 (250 variables, 1065 clauses, unsatisfiable so no chain stops), 20 M flips per run split evenly over the batch, a uniform start, flips per second from the solver's own polish clock. probSAT: its printed flips/sec over the same number of flips on one core. Every record is in walk_throughput.jsonl with its command, commit and binary hash.

| backend | rule | batch | flips per launch | aggregate M flips/s | per chain k flips/s | runs |
|---|---|---|---|---|---|---|
| cpu (4 threads) | probsat | 4096 | 32 | 9.42 | 2.30 | 2 |
| cpu (4 threads) | skc | 4096 | 32 | 12.87 | 3.14 | 2 |
| cuda | probsat | 512 | 32 | 11.17 | 21.82 | 2 |
| cuda | probsat | 1024 | 32 | 22.50 | 21.97 | 2 |
| cuda | probsat | 4096 | 32 | 77.06 | 18.81 | 2 |
| cuda | probsat | 16384 | 32 | 125.71 | 7.67 | 2 |
| cuda | skc | 512 | 32 | 16.00 | 31.25 | 2 |
| cuda | skc | 1024 | 32 | 31.85 | 31.10 | 2 |
| cuda | skc | 4096 | 32 | 109.27 | 26.68 | 2 |
| cuda | skc | 16384 | 32 | 137.38 | 8.38 | 2 |

probSAT on one core: 6.28 M flips/s (median of 4 runs, seeds [1, 1, 2, 2], 20 M flips each).
Best cuda aggregate: 137.85 M flips/s at batch 16384 with rule skc, 22.0x one probSAT core; its chains run at 8.4 k flips/s each, 746x slower than probSAT's one chain.
