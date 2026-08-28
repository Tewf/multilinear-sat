# SATLIB benchmark: F against mu and fourier

## Provenance

- Date: 2026-08-28 22:33; branch commit 8b50f89bf8
- Device: cuda (NVIDIA GeForce RTX 4060 Laptop GPU), torch 2.13.0+cu130
- Other GPU processes at start (nvidia-smi): none
- Runs started 2026-08-28T18:50:14; one warm-up solve per process, untimed, before any record
- Instances: SATLIB uniform random 3-SAT, satisfiable by construction (uf50-218, uf100-430, uf250-1065), the first N files by sorted name; fixed seeds; identical scaffolding for every method

## Scope actually run

uf50-218: 100 instances, seeds [0], cap 5 s; uf100-430: 100 instances, seeds [0], cap 15 s; uf250-1065: 100 instances, seeds [0], cap 30 s

Budget rule: with the caps fixed, the scope was reduced in the order N = 100 with seeds {0, 1}; seeds {0}; N = 50 for uf250 only; N = 50 for all, until a calibration on 5 instances per family estimated the run under 2.5 hours.

## Table

| family | method | runs | solve rate | median time (solved) | mean per-instance min #unsat at rounding | mean of mean #unsat over events | runs at cap |
|---|---|---|---|---|---|---|---|
| uf50-218 | F | 100 | 100/100 (100 %) | 0.08 s | 0.77 | 1.06 | 0 |
| uf50-218 | mu | 100 | 100/100 (100 %) | 0.04 s | 1.49 | 1.95 | 0 |
| uf50-218 | fourier | 100 | 100/100 (100 %) | 0.05 s | 1.29 | 1.78 | 0 |
| uf100-430 | F | 100 | 94/100 (94 %) | 0.37 s | 2.09 | 2.62 | 6 |
| uf100-430 | mu | 100 | 99/100 (99 %) | 0.11 s | 3.11 | 4.28 | 1 |
| uf100-430 | fourier | 100 | 95/100 (95 %) | 0.24 s | 2.68 | 3.86 | 5 |
| uf250-1065 | F | 100 | 42/100 (42 %) | 7.69 s | 4.75 | 7.00 | 58 |
| uf250-1065 | mu | 100 | 75/100 (75 %) | 1.91 s | 6.11 | 10.15 | 25 |
| uf250-1065 | fourier | 100 | 53/100 (53 %) | 8.26 s | 6.79 | 9.73 | 47 |

median time is over solved runs only; the per-instance minimum is over seeds and rounding events before the WalkSAT polish; a run is at cap when it did not solve within its time limit.

## What the table shows

- **uf50-218** (cap 5 s): solve rates F 100/100, mu 100/100, fourier 100/100; highest: F, mu, fourier. Mean per-instance min #unsat at rounding F 0.77, mu 1.49, fourier 1.29; lowest: F.
- **uf100-430** (cap 15 s): solve rates F 94/100, mu 99/100, fourier 95/100; highest: mu. Mean per-instance min #unsat at rounding F 2.09, mu 3.11, fourier 2.68; lowest: F.
- **uf250-1065** (cap 30 s): solve rates F 42/100, mu 75/100, fourier 53/100; highest: mu. Mean per-instance min #unsat at rounding F 4.75, mu 6.11, fourier 6.79; lowest: F.

## Caveats

- 2026-08-28 run: the GPU was shared from 19:14 to the end (20:29) with an image-generation server (ComfyUI, 4.8 GB resident, memory constant); uf50 and uf100 finished before it started, uf250 ran from 18:59 to 20:29. In the sampled part of the overlap (19:51-20:29, 302 samples at 15 s) GPU utilisation averaged 80 % against about 66 % for this benchmark alone, so the co-tenant computed at times; its share cannot be separated from the log. Under a 30 s cap that costs steps, rounding events and polishes to every method in the same way; treat the uf250 solve rates and medians as a lower bound, and the per-instance minimum #unsat as the more robust column.
