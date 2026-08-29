#!/usr/bin/env python3
"""Throughput of the walk against probSAT on one core: flips per second per chain and in
aggregate, on uuf250-01 (unsatisfiable, so no chain stops early), about 20 M flips per run,
at several batch sizes and both rules, cuda and cpu backends; probSAT for the same flips.
Records to walk_throughput.jsonl, the table to walk_throughput.md."""
import argparse
import statistics
from pathlib import Path

from walk_runs import (BENCHMARK, INSTANCES, append_record, frozen_binary, load_records, provenance, run_probsat,
                       run_solver)

INSTANCE = INSTANCES / "uuf250-1065" / "uuf250-01.cnf"
TOTAL_FLIPS = 20_000_000


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--build", default="build-cuda")
    parser.add_argument("--batches", nargs="+", type=int, default=[512, 1024, 4096, 16384])
    parser.add_argument("--rules", nargs="+", default=["probsat", "skc"])
    parser.add_argument("--backends", nargs="+", default=["cuda", "cpu"])
    parser.add_argument("--cpu-threads", type=int, default=4)
    parser.add_argument("--seeds", nargs="+", type=int, default=[1, 2])
    parser.add_argument("--flips-per-launch", nargs="+", type=int, default=[32])
    parser.add_argument("--output", type=Path, default=BENCHMARK / "walk_throughput.jsonl")
    return parser.parse_args()


def solver_record(binary, arguments, backend, batch, rule, seed, per_launch):
    flips_per_slot = TOTAL_FLIPS // batch
    flags = ["--backend", backend, "--batch-size", batch, "--seed-kind", "uniform", "--polish-flips", flips_per_slot,
             "--walk-rule", rule, "--run-limit", 1, "--seed", seed, "--walk-flips-per-launch", per_launch]
    environment = {"OMP_NUM_THREADS": str(arguments.cpu_threads)} if backend == "cpu" else None
    result = run_solver(binary, INSTANCE, flags, 600, environment)
    stats = result["json"] or {}
    flips, seconds = stats.get("flips", 0), stats.get("polish_seconds", 0.0)
    return dict(kind="solver", backend=backend, batch=batch, rule=rule, seed=seed, flips_per_launch=per_launch,
                cpu_threads=arguments.cpu_threads if backend == "cpu" else None, flips=flips, polish_seconds=seconds,
                flips_per_second=flips / seconds if seconds else None, per_chain=flips / seconds / batch if seconds else None,
                wall_seconds=result["wall_seconds"], command=result["command"])


def write_table(records, path):
    solver = [r for r in records if r["kind"] == "solver"]
    probsat = [r for r in records if r["kind"] == "probsat"]
    lines = ["# Walk throughput against probSAT on one core", "",
             f"uuf250-01 (250 variables, 1065 clauses, unsatisfiable so no chain stops), {TOTAL_FLIPS / 1e6:.0f} M flips "
             "per run split evenly over the batch, a uniform start, flips per second from the solver's own polish clock. "
             "probSAT: its printed flips/sec over the same number of flips on one core. Every record is in "
             "walk_throughput.jsonl with its command, commit and binary hash.", "",
             "| backend | rule | batch | flips per launch | aggregate M flips/s | per chain k flips/s | runs |", "|---|---|---|---|---|---|---|"]
    keys = sorted({(r["backend"], r["rule"], r["batch"], r["flips_per_launch"]) for r in solver}, key=lambda k: (k[0], k[1], k[2], k[3]))
    for backend, rule, batch, per_launch in keys:
        group = [r for r in solver if (r["backend"], r["rule"], r["batch"], r["flips_per_launch"]) == (backend, rule, batch, per_launch) and r["flips_per_second"]]
        if not group:
            continue
        aggregate = statistics.median(r["flips_per_second"] for r in group)
        threads = f" ({group[0]['cpu_threads']} threads)" if backend == "cpu" else ""
        lines.append(f"| {backend}{threads} | {rule} | {batch} | {per_launch} | {aggregate / 1e6:.2f} | {aggregate / batch / 1e3:.2f} | {len(group)} |")
    if probsat:
        rate = statistics.median(r["flips_per_second"] for r in probsat if r["flips_per_second"])
        lines += ["", f"probSAT on one core: {rate / 1e6:.2f} M flips/s (median of {len(probsat)} runs, seeds "
                  f"{sorted(r['seed'] for r in probsat)}, {TOTAL_FLIPS / 1e6:.0f} M flips each)."]
        best = max((r for r in solver if r["backend"] == "cuda" and r["flips_per_second"]), key=lambda r: r["flips_per_second"], default=None)
        if best:
            lines.append(f"Best cuda aggregate: {best['flips_per_second'] / 1e6:.2f} M flips/s at batch {best['batch']} with rule "
                         f"{best['rule']}, {best['flips_per_second'] / rate:.1f}x one probSAT core; its chains run at "
                         f"{best['per_chain'] / 1e3:.1f} k flips/s each, {rate / best['per_chain']:.0f}x slower than probSAT's one chain.")
    path.write_text("\n".join(lines) + "\n")
    print(f"wrote {path}")


def main():
    arguments = parse_arguments()
    binary = frozen_binary(arguments.build)
    append_record(arguments.output, provenance(binary, arguments))
    for seed in arguments.seeds:
        record = run_probsat(INSTANCE, seed, 600, max_flips=TOTAL_FLIPS)
        append_record(arguments.output, dict(kind="probsat", seed=seed, **record))
        print(f"probSAT seed {seed}: {record['flips_per_second']} flips/s")
    for backend in arguments.backends:
        for rule in arguments.rules:
            for batch in arguments.batches:
                for per_launch in arguments.flips_per_launch:
                    for seed in arguments.seeds:
                        record = solver_record(binary, arguments, backend, batch, rule, seed, per_launch)
                        append_record(arguments.output, record)
                        rate = record["flips_per_second"] or 0.0
                        print(f"{backend} {rule} batch {batch} launch {per_launch} seed {seed}: {rate / 1e6:.2f} M flips/s", flush=True)
    write_table(load_records(arguments.output), arguments.output.with_suffix(".md"))


if __name__ == "__main__":
    main()
