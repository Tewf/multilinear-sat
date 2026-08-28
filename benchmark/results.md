# multilinear-sat benchmark results

## Provenance

- Date: 2026-08-28 22:29 (local, Europe/Paris)
- Solver git commit: HEAD 692d2ef4de (clean)
- Prebuilt binary: `build-cuda/multilinear-sat`, built from commit 06ba842, last built 2026-08-28 12:08:30; commits after 06ba842 touch neither `solver/` nor `cli/`
- All recorded runs used the single binary build at mtime 2026-08-28 12:08:30.
- GPU: NVIDIA GeForce RTX 4060 Laptop GPU
- CPU: 12th Gen Intel(R) Core(TM) i5-12450H
- CUDA: Cuda compilation tools, release 12.9, V12.9.86
- Baseline commits (`benchmark/third_party/versions.txt`):
  - probSAT d5e1d4c80fdcc89ff5db3b5e4afebd303bf78fa6
  - cadical c60730422e758ef1cebe7aeddf2dda31c996bf04
- Exact flags:
  - CaDiCaL: `cadical -t <cap> -q -n <file>` (cap 300s for n<=5000, 600s for n=20000)
  - probSAT: `timeout <cap> probSAT <file> <seed>` (cap 60s for n<=5000, 120s for n=20000; probSAT has no internal time cap, only flip/try counts, both left at their default of unlimited, so `timeout` is what stops it)
  - multilinear-sat: `multilinear-sat <file> --time-limit <cap> --seed <seed> --backend cuda --no-model --step-size 0.1 --momentum 0.9 --kick-sigma 0.3 --kick-decay 1.0 --focused-kick 1 --luby-unit 200 --batch-size 1024` (these are the compiled-in defaults from `solver/configuration.hpp`, passed explicitly)

## Protocol

One run per (solver, instance, seed) cell, no other GPU load during the run (checked with `nvidia-smi` before starting). CaDiCaL runs first on every instance with a generous limit (300s for n<=5000, 600s for n=20000) purely to decide satisfiability; an instance it cannot decide within that limit is reported as "undecided" and excluded from the rates below (it still counts against the compute budget). probSAT and multilinear-sat (cuda backend) then each run once per seed on every CaDiCaL-SAT instance, at the per-solver limit (60s for n<=5000, 120s for n=20000).

**Scope cut from the brief.** Calibration on 2026-08-28 showed CaDiCaL frequently needs its full cap even at n=1000-5000 on uniform random 3-SAT (consistent with the literature: CDCL scales poorly on random k-SAT well below the satisfiability threshold, which is exactly why local-search solvers are competitive here). To stay under the ~75 minute total compute budget, the two prescribed cuts were both applied up front: n=20000 was dropped first, then seeds were reduced from 3 to 2. Scope actually run: n in {200, 1000, 5000}, ratios in {4.0, 4.2, 4.26}, seeds in {0, 1} (18 instances).

## Parameter sweep

n=1000, ratio=4.2, seeds=[0, 1], 15s per run, cuda backend, one factor varied at a time from the `configuration.hpp` defaults (step_size=0.1, momentum=0.9, kick_sigma=0.3, kick_decay=1.0, focused_kick=1, luby_unit=200, batch_size=1024). `best_violated` is min-max over the runs at that setting (0 = solved).

| factor | value | runs | solved | best_violated range |
|---|---|---|---|---|
| step_size | 0.05 | 2 | 0/2 | 17-18 |
| step_size | 0.1 | 2 | 0/2 | 21-22 |
| step_size | 0.2 | 2 | 0/2 | 22-25 |
| kick_sigma | 0.0 | 2 | 0/2 | 40-42 |
| kick_sigma | 0.1 | 2 | 0/2 | 26-26 |
| kick_sigma | 0.3 | 2 | 0/2 | 21-22 |
| kick_sigma | 0.6 | 2 | 0/2 | 15-16 |
| luby_unit | 50 | 2 | 0/2 | 21-23 |
| luby_unit | 200 | 2 | 0/2 | 21-22 |
| luby_unit | 1000 | 2 | 0/2 | 20-23 |
| batch_size | 256 | 2 | 0/2 | 21-22 |
| batch_size | 1024 | 2 | 0/2 | 21-22 |
| batch_size | 4096 | 2 | 0/2 | 24-25 |
| focused_kick | 0 | 2 | 0/2 | 24-24 |

No swept setting solved the sweep instance, so the settings are ranked by the fewest violated clauses reached: step_size: 0.05 (best_violated 17-18); kick_sigma: 0.6 (best_violated 15-16); luby_unit: 1000 (best_violated 20-23); batch_size: 256 (best_violated 21-22); focused_kick: 0 (best_violated 24-24). The main table below uses the compiled-in defaults; the sweep's direction (a smaller step, a larger kick) is untested there.

## Main table

| n | ratio | instances tested (CaDiCaL-SAT) | multilinear-sat rate | multilinear-sat median | probSAT rate | probSAT median | CaDiCaL median decision time |
|---|---|---|---|---|---|---|---|
| 200 | 4.00 | 2 | 2/2 | 0.59s | 2/2 | 0.00s | 0.0s |
| 200 | 4.20 | 1/2 | 1/1 | 15.27s | 1/1 | 0.01s | 0.2s |
| 200 | 4.26 | 1/2 | 1/1 | 2.50s | 1/1 | 0.00s | 0.1s |
| 1000 | 4.00 | 2 | 0/2 | - | 2/2 | 0.01s | 1.1s |
| 1000 | 4.20 | 2 | 0/2 | - | 2/2 | 2.26s | 112.0s |
| 1000 | 4.26 | 1/2 | 0/1 | - | 1/1 | 0.04s | 4.6s |
| 5000 | 4.00 | 2 | 0/2 | - | 2/2 | 0.07s | 37.7s |
| 5000 | 4.20 | 0/2 | 0/0 | - | 0/0 | - | - |
| 5000 | 4.26 | 0/2 | 0/0 | - | 0/0 | - | - |

(rate = solved/attempted on the CaDiCaL-SAT instances; median is over solved instances only; "instances tested" shows fewer than planned when CaDiCaL left some undecided.)

## Reading the results

Across the cells actually tested, multilinear-sat solved 4/11 runs (36%) and probSAT solved 11/11 runs (100%); probSAT wins on raw solve rate here. CaDiCaL, run only to decide satisfiability, needed its full generous cap on several instances above n=200, which is why some cells show fewer than the planned number of CaDiCaL-SAT instances: those larger/harder cells were left undecided rather than wrongly counted as unsolved by any solver.
Cells where multilinear-sat solved anything, with both medians: n=200 ratio 4.00 (multilinear-sat 0.59s, probSAT 0.00s), n=200 ratio 4.20 (multilinear-sat 15.27s, probSAT 0.01s), n=200 ratio 4.26 (multilinear-sat 2.50s, probSAT 0.00s).
Where multilinear-sat did not solve within its cap, the fewest violated clauses it reached were 10-19 at n=1000; 119-126 at n=5000: the residual grows with n.

## Issues

- 2026-08-28 main run: a ComfyUI server (pid 26518, 1.9 GB resident, 0 % utilisation) stayed on the GPU throughout. Its memory never changed across the 686 samples of `raw/gpu-monitor.log` (one every 15 s) and every interval of non-zero utilisation coincides with a multilinear-sat run, so no cell is affected.
