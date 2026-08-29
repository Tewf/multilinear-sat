#!/usr/bin/env python3
"""The seed comparison of the Python record, re-run in C++: the per-restart success of one
polish (10n SKC flips) from a uniform start, all false, and the ascent at 50, 200 and 500
steps, at 4096 slots on the first 20 instances of uf50-218, uf100-430 and uf250-1065, seeds 0
and 1; probSAT's own time to a solution on the same instances and seeds beside it. One JSONL
record per (family, instance, arm, seed), resumable; the table is seed_table.py."""
import argparse
from datetime import datetime
from pathlib import Path

from walk_runs import BENCHMARK, append_record, frozen_binary, load_records, provenance, run_probsat, run_solver, satlib_instances

FAMILIES = ["uf50-218", "uf100-430", "uf250-1065"]
ARMS = {"uniform": ["--seed-kind", "uniform"], "all_false": ["--seed-kind", "all-false"],
        "ascent50": ["--seed-kind", "ascent", "--seed-steps", 50], "ascent200": ["--seed-kind", "ascent", "--seed-steps", 200],
        "ascent500": ["--seed-kind", "ascent", "--seed-steps", 500],
        "tilted500": ["--seed-kind", "tilted", "--seed-steps", 500, "--tilted-groups", 128]}
DEFAULT_ARMS = [arm for arm in ARMS if not arm.startswith("tilted")]


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--build", default="build-cuda")
    parser.add_argument("--backend", default="cuda")
    parser.add_argument("--families", nargs="+", default=FAMILIES)
    parser.add_argument("--instances", type=int, default=20)
    parser.add_argument("--slots", type=int, default=4096)
    parser.add_argument("--polish-flips-per-variable", type=int, default=10)
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1])
    parser.add_argument("--arms", nargs="*", default=DEFAULT_ARMS, choices=list(ARMS), help="none runs probSAT alone")
    parser.add_argument("--probsat-cap", type=float, default=60.0)
    parser.add_argument("--extra-flags", nargs="*", default=[], help="passed to every solver run, e.g. --walk-rule probsat")
    parser.add_argument("--output", type=Path, default=BENCHMARK / "seed_comparison.jsonl")
    return parser.parse_args()


def done_keys(records):
    return {(r["family"], r["instance"], r["arm"], r["seed"]) for r in records if r.get("kind") == "run"}


def variable_count(path):
    with open(path) as handle:
        for line in handle:
            if line.startswith("p "):
                return int(line.split()[2])
    raise ValueError(f"no header in {path}")


def solver_run(binary, arguments, family, path, arm, seed):
    flips = arguments.polish_flips_per_variable * variable_count(path)
    flags = ["--backend", arguments.backend, "--batch-size", arguments.slots, "--polish-flips", flips, "--walk-rule", "skc",
             "--run-limit", 1, "--seed", seed] + ARMS[arm] + arguments.extra_flags
    result = run_solver(binary, path, flags, 600)
    stats = result["json"] or {}
    heuristic = stats.get("polish_successes", 0) + stats.get("heuristic_failures", 0)
    cost_ms = (stats.get("seed_seconds", 0.0) + stats.get("polish_seconds", 0.0)) * 1000 / arguments.slots
    fraction = stats.get("polish_successes", 0) / heuristic if heuristic else None
    return dict(kind="run", family=family, instance=path.name, arm=arm, seed=seed, slots=arguments.slots, polish_flips=flips,
                success_fraction=fraction, seed_seconds=stats.get("seed_seconds"), polish_seconds=stats.get("polish_seconds"),
                cost_per_restart_ms=round(cost_ms, 5), expected_time_ms=round(cost_ms / fraction, 3) if fraction else None,
                flips=stats.get("flips"), wall_seconds=result["wall_seconds"], status=result["status"], command=result["command"],
                timestamp=datetime.now().isoformat(timespec="seconds"))


def main():
    arguments = parse_arguments()
    binary = frozen_binary(arguments.build)
    done = done_keys(load_records(arguments.output))
    append_record(arguments.output, provenance(binary, arguments))
    for family in arguments.families:
        for path in satlib_instances(family, arguments.instances):
            for seed in arguments.seeds:
                if (family, path.name, "probsat", seed) not in done:
                    result = run_probsat(path, seed, arguments.probsat_cap)
                    append_record(arguments.output, dict(kind="run", family=family, instance=path.name, arm="probsat", seed=seed,
                                                         status=result["status"], wall_seconds=result["wall_seconds"],
                                                         cpu_seconds=result["cpu_seconds"], flips=result["flips"],
                                                         command=result["command"], timestamp=datetime.now().isoformat(timespec="seconds")))
                    print(f"{family} {path.name} seed={seed} probsat {result['status']} {result['wall_seconds']:.3f}s", flush=True)
                for arm in arguments.arms:
                    if (family, path.name, arm, seed) in done:
                        continue
                    record = solver_run(binary, arguments, family, path, arm, seed)
                    append_record(arguments.output, record)
                    print(f"{family} {path.name} seed={seed} {arm:10s} p={record['success_fraction']} cost/restart={record['cost_per_restart_ms']:.4f}ms "
                          f"seed={record['seed_seconds']}s polish={record['polish_seconds']}s", flush=True)


if __name__ == "__main__":
    main()
