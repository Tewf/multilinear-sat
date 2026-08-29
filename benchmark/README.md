# Benchmark

Every measurement in this repository lives here with its provenance: the command that made
it, the seed, the commit, the sha256 of the frozen copy of the binary it ran, and the GPU's
state at the start. Tables are generated from the JSONL records by the script beside each;
nothing in a table is typed by hand. Timings come from one laptop (RTX 4060 Laptop GPU,
i5-12450H) whose chassis rides its thermal limit, so a ratio is reported only where the
thermal band cannot explain it ([arms/protocol.md](arms/protocol.md) states the rule).

## Reproduce

```
./build_baselines.sh                                  # probSAT and CaDiCaL into third_party/ (git-ignored)
python3 generate_instances.py --out instances --n 1000 5000 --ratios 4.2 4.26 --seeds 5
python3 ../gaussian_surrogate/benchmark/download_satlib.py    # SATLIB families into instances/: uf50-218, uf100-430, uf250-1065, uuf250-1065
python3 run_benchmark.py main && python3 report.py    # the 0.1 table, results.md
python3 seed_comparison.py && python3 seed_table.py   # each walk measurement is resumable
python3 arms/run_arms.py && python3 arms/dominance.py # the priced variants, the front, the rejected
```

Run from inside `benchmark/`; `instances/`, `raw/` (logs and frozen binaries) and
`third_party/` are git-ignored. Every stage skips the records it already holds.

## Files

| File | Role |
|---|---|
| `generate_instances.py` | reproducible uniform random 3-SAT instances from (n, ratio, seed) |
| `build_baselines.sh` | builds probSAT and CaDiCaL and records their commits |
| `run_benchmark.py`, `report.py`, `results.json`, `sweep_results.json`, `results.md` | the 0.1 harness: the ascent alone against probSAT and CaDiCaL at n = 200, 1000, 5000, and its parameter sweep |
| `walk_runs.py` | what every walk measurement shares: one solver or probSAT run as a record, the frozen binary, the provenance stamp |
| `walk_throughput.py`, `.jsonl`, `.md` | flips per second of the batched walk against probSAT on one core |
| `seed_comparison.py`, `seed_table.py`, `.jsonl`, `.md` | per-restart success and cost of each seed at 4096 slots, probSAT beside it |
| `posterior_calibration.py`, `posterior_table.py`, `.jsonl`, `.md` | the Beta-mixture posterior on uf250 against uuf250 and kissat |
| `parity_challenge.py`, `.jsonl`, `.md` | the native parity rows on MM-Challenge-1 and matmul_3x3x3 at 23 |
| `as-xnfsat/xnfsat` | an adapter answering to xnfsat's name and flags, so the tensor-rank toolkit's verification route can hand this solver an XNF |
| [`findings-walk/`](findings-walk/README.md) | what the four walk measurements show, their caveats and the port's departures |
| [`arms/`](arms/README.md) | the dominance set-up: the protocol, the variants as data, the resumable runner, the Pareto front and the rejected arms with their numbers |
