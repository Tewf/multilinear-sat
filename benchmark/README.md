# Benchmark

## Reproduce

```
./build_baselines.sh                 # clones + builds probSAT and CaDiCaL into third_party/ (git-ignored)
python3 generate_instances.py --out instances \
    --n 200 1000 5000 20000 --ratios 4.0 4.2 4.26 --seeds 3   # instances/ is git-ignored
python3 run_benchmark.py sweep       # parameter sweep, ~8 min
python3 run_benchmark.py main        # main table, self-limits to a wall-clock budget
python3 report.py                    # regenerate results.md from the JSON only, no runs
```
Run from inside `benchmark/`. Each stage is resumable: it skips any (solver,
instance, seed) already recorded in `results.json` / `sweep_results.json`.
`raw/` (git-ignored) holds detached-run logs from `setsid nohup`.

## Files

- `generate_instances.py`: writes reproducible DIMACS 3-SAT instances (given).
- `build_baselines.sh`: builds probSAT and CaDiCaL, records their commits.
- `run_benchmark.py`: runs CaDiCaL/probSAT/multilinear-sat and writes `results.json`
  and `sweep_results.json` (both committed; raw per-run records).
- `report.py`: turns the JSON into `results.md` (provenance, protocol, sweep table,
  main table, reading, issues). Safe to re-run any time.
- `results.json`, `sweep_results.json`, `results.md`: committed outputs.
