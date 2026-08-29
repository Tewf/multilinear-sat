#!/usr/bin/env python3
"""The markdown table of a seed comparison run: one row per (family, arm) with the
per-restart success probability, the median cost of a restart, their ratio (the expected
time to a solution), and probSAT's measured time to a solution on the same instances."""
import argparse
import statistics
from pathlib import Path

from walk_runs import BENCHMARK, load_records

ARM_ORDER = ["uniform", "all_false", "ascent50", "ascent200", "ascent500", "tilted500"]


def summarise(runs):
    rows = []
    for family in dict.fromkeys(r["family"] for r in runs):
        for arm in ARM_ORDER:
            group = [r for r in runs if r["family"] == family and r["arm"] == arm and r["success_fraction"] is not None]
            if not group:
                continue
            p = statistics.fmean(r["success_fraction"] for r in group)
            cost = statistics.median(r["cost_per_restart_ms"] for r in group)
            above_uniform = sum(r["success_fraction"] > next((u["success_fraction"] for u in runs if u["family"] == family and u["arm"] == "uniform"
                                                              and u["instance"] == r["instance"] and u["seed"] == r["seed"]), 2.0) for r in group)
            rows.append(dict(family=family, arm=arm, runs=len(group), p=p, cost=cost, expected=cost / p if p > 0 else None,
                             with_success=sum(r["success_fraction"] > 0 for r in group), above_uniform=above_uniform,
                             seed_seconds=statistics.fmean(r["seed_seconds"] for r in group),
                             polish_seconds=statistics.fmean(r["polish_seconds"] for r in group)))
        probsat = [r for r in runs if r["family"] == family and r["arm"] == "probsat"]
        if probsat:
            solved = [r["wall_seconds"] for r in probsat if r["status"] == "SATISFIABLE"]
            flips = [r["flips"] for r in probsat if r["status"] == "SATISFIABLE" and r["flips"]]
            rows.append(dict(family=family, arm="probsat", runs=len(probsat), solved=len(solved),
                             mean_seconds=statistics.fmean(solved) if solved else None, median_seconds=statistics.median(solved) if solved else None,
                             mean_flips=statistics.fmean(flips) if flips else None))
    return rows


def write_table(provenance, rows, path):
    first = provenance[0] if provenance else {}
    arguments = first.get("arguments", {})
    lines = ["# Seed comparison in C++: per-restart success of one polish from five seeds, probSAT beside it", "",
             f"- First record {first.get('timestamp')}; commit {first.get('commit')}; binary sha256 {first.get('binary_sha256')}; "
             f"backend {arguments.get('backend')}; GPU at start: {first.get('gpu')}.",
             f"- {arguments.get('slots')} slots per run, polish = {arguments.get('polish_flips_per_variable')} n SKC flips (noise 0.5), "
             f"the ascent = the library's projected gradient with its defaults for 50, 200 or 500 iterations rounded by sign; "
             f"instances: the first {arguments.get('instances')} of each family in name order; seeds {arguments.get('seeds')}.",
             "- p = mean over runs of the fraction of slots satisfied after the polish; cost = median over runs of "
             "(seed seconds + polish seconds) / slots, from the solver's own clocks; expected time = cost / p. "
             "probSAT: wall seconds of one run to a solution (its default flip and try limits), mean and median over "
             "instances and seeds, which is a draw of its expected time to a solution (process start and parse included); "
             "its mean flips per solution sit in the cost column, against polish flips / p for the walk.", "",
             "| family | seed | runs | p | runs with p > 0 | runs with p above uniform's | cost / restart (ms) | expected time (ms) | seed s | polish s |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["arm"] == "probsat":
            mean = f"{r['mean_seconds'] * 1000:.2f}" if r["mean_seconds"] is not None else "-"
            median = f"{r['median_seconds'] * 1000:.2f}" if r["median_seconds"] is not None else "-"
            flips = f"{r['mean_flips'] / 1e3:.1f} k flips" if r["mean_flips"] else "-"
            lines.append(f"| {r['family']} | probSAT, one core | {r['runs']} | solved {r['solved']}/{r['runs']} | - | - | mean {flips} | mean {mean}, median {median} | - | - |")
            continue
        expected = f"{r['expected']:.3f}" if r["expected"] is not None else "inf"
        lines.append(f"| {r['family']} | {r['arm']} | {r['runs']} | {r['p']:.4f} | {r['with_success']}/{r['runs']} | {r['above_uniform']}/{r['runs']} "
                     f"| {r['cost']:.4f} | {expected} | {r['seed_seconds']:.3f} | {r['polish_seconds']:.3f} |")
    lines += ["", "Every run is in seed_comparison.jsonl with its command, seed, commit, binary hash and timestamp."]
    path.write_text("\n".join(lines) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", type=Path, default=BENCHMARK / "seed_comparison.jsonl")
    parser.add_argument("--output", type=Path, default=BENCHMARK / "seed_comparison.md")
    arguments = parser.parse_args()
    records = load_records(arguments.input)
    write_table([r for r in records if r.get("kind") == "provenance"], summarise([r for r in records if r.get("kind") == "run"]), arguments.output)
