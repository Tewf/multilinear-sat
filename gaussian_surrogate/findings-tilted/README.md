# Findings: the tilted sampling-gradient loop, measured

Built and measured on 2026-08-29 (commits 1db4cd6 to f40864c of the Python record), one
RTX 4060 Laptop GPU, torch 2.13. Records: `../experiments/tilted_mean_bias.md` (CPU, enumeration),
`../experiments/seed_comparison.jsonl` and `.md` (GPU, 14:38 to 17:21), `../experiments/posterior_calibration.jsonl`
and `.md` (kissat on the CPU at 13:15; the loop's half on the GPU, 17:21 to 17:42). No other process
was on the card at the start of any phase; the uniform arm's polish time, the contention detector,
spread over 0.151 to 0.173 s on uf50, 0.30 to 0.47 s on uf100 and 0.77 to 1.28 s on uf250, and the
tables use medians. What was built and left out is in `../method/not-built.md`; the design is
`../../method/sampling-gradient-loop.md` as corrected by its review. The Python package is the
record: the implementation moved to the C++ library (`../../solver/`), whose measurement of the
same seeds at the kernel's speed is `../../benchmark/findings-walk/`.

| File | Table |
|---|---|
| [tilted-mean-estimate.md](tilted-mean-estimate.md) | 1: the sampled tilted mean against the exact one by enumeration, annealed weights against walk weights |
| [seed-comparison.md](seed-comparison.md) | 2: per-restart success of one polish from five seeds, 20 instances per family, seeds 0 and 1 |
| [posterior-against-kissat.md](posterior-against-kissat.md) | 3: the Beta-mixture posterior on uf250 against uuf250 and kissat's refutation time |
| [caveats.md](caveats.md) | what the numbers carry, and the launch-bound kernel that the C++ port removes |

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
