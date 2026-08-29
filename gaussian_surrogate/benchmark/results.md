# SATLIB benchmark: F against mu and fourier

## Provenance

- Date: 2026-08-29 01:02; branch commit c6f383cf9b
- Device: cuda (NVIDIA GeForce RTX 4060 Laptop GPU), torch 2.13.0+cu130
- Other GPU processes at start (nvidia-smi): 50779, python (conda env comfyui), 4824 MiB
- Runs started 2026-08-28T23:37:48; one warm-up solve per process, untimed, before any record
- Instances: SATLIB uniform random 3-SAT, satisfiable by construction (uf50-218, uf100-430, uf250-1065), the first N files by sorted name; fixed seeds; identical scaffolding for every method

## Scope actually run

uf50-218: 100 instances, seeds [0], cap 5 s; uf100-430: 100 instances, seeds [0], cap 15 s; uf250-1065: 100 instances, seeds [0], cap 30 s

Budget rule: with the caps fixed, the scope was reduced in the order N = 100 with seeds {0, 1}; seeds {0}; N = 50 for uf250 only; N = 50 for all, until a calibration on 5 instances per family estimated the run under 2.5 hours.

## Table

| family | method | runs | solve rate | median time (solved) | mean per-instance min #unsat at rounding | mean of mean #unsat over events | runs at cap |
|---|---|---|---|---|---|---|---|
| uf50-218 | F | 100 | 100/100 (100 %) | 0.05 s | 0.77 | 1.06 | 0 |
| uf50-218 | mu | 100 | 100/100 (100 %) | 0.04 s | 1.49 | 1.95 | 0 |
| uf50-218 | fourier | 100 | 100/100 (100 %) | 0.04 s | 1.29 | 1.78 | 0 |
| uf100-430 | F | 100 | 94/100 (94 %) | 0.32 s | 2.09 | 2.62 | 6 |
| uf100-430 | mu | 100 | 99/100 (99 %) | 0.11 s | 3.11 | 4.28 | 1 |
| uf100-430 | fourier | 100 | 98/100 (98 %) | 0.10 s | 2.65 | 3.85 | 2 |
| uf250-1065 | F | 100 | 38/100 (38 %) | 9.59 s | 4.92 | 7.07 | 62 |
| uf250-1065 | mu | 100 | 77/100 (77 %) | 2.00 s | 6.12 | 10.16 | 23 |
| uf250-1065 | fourier | 100 | 81/100 (81 %) | 3.59 s | 6.51 | 9.73 | 19 |

median time is over solved runs only; the per-instance minimum is over seeds and rounding events before the WalkSAT polish; a run is at cap when it did not solve within its time limit.

## What the table shows

- **uf50-218** (cap 5 s): solve rates F 100/100, mu 100/100, fourier 100/100; highest: F, mu, fourier. Mean per-instance min #unsat at rounding F 0.77, mu 1.49, fourier 1.29; lowest: F.
- **uf100-430** (cap 15 s): solve rates F 94/100, mu 99/100, fourier 98/100; highest: mu. Mean per-instance min #unsat at rounding F 2.09, mu 3.11, fourier 2.65; lowest: F.
- **uf250-1065** (cap 30 s): solve rates F 38/100, mu 77/100, fourier 81/100; highest: fourier. Mean per-instance min #unsat at rounding F 4.92, mu 6.12, fourier 6.51; lowest: F.

## Caveats

- This record (run 2, 2026-08-28 23:37 to 2026-08-29 01:02) supersedes run 1 (commit 28dc078), which computed the clause products with torch's prod; its CUDA backward is slow on rows holding an exact zero, which the box relaxation produces, so run 1's fourier column had a 24x per-step handicap. The moments are identical; only speed changed.
- An image-generation server (ComfyUI, pid 50779, 4.8 GB resident) was on the GPU from the start of run 2 to its end. It was idle when the run started (0 % utilisation) and was seen computing at least once during the uf250 phase (95 % total utilisation at 00:14 against about 66 % for this benchmark alone); no sampler ran, so its share is unknown. Under a 30 s cap that costs steps, rounding events and polishes to every method in the same way; treat the uf250 solve rates and medians as a lower bound and the per-instance minimum #unsat as the more robust column.
