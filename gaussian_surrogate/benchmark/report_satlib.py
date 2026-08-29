"""Turn satlib_results.jsonl into results.md: provenance, the scope run, one table, what it shows."""
import argparse
import json
import statistics
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
METHOD_ORDER = ("F", "mu", "fourier")


def load_records(path):
    with open(path) as handle:
        records = [json.loads(line) for line in handle if line.strip()]
    provenance = [r for r in records if r.get("kind") == "provenance"]
    return provenance, [r for r in records if r.get("kind") == "run"]


def git_head():
    try:
        return subprocess.run(["git", "rev-parse", "--short=10", "HEAD"], cwd=HERE, capture_output=True,
                              text=True, timeout=10).stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def summarise(runs):
    """One row per (family, method): counts, rate, median time over solved, the two #unsat means."""
    groups = defaultdict(list)
    for r in runs:
        groups[(r["family"], r["method"])].append(r)
    rows = []
    for (family, method), group in groups.items():
        solved = [r for r in group if r["status"] == "SATISFIABLE"]
        per_instance_min = defaultdict(list)
        for r in group:
            per_instance_min[r["instance"]].append(r["min_unsat_at_rounding"])
        rows.append({
            "family": family, "method": method, "runs": len(group), "solved": len(solved),
            "median_time": statistics.median(r["time_seconds"] for r in solved) if solved else None,
            "mean_min_unsat": statistics.fmean(min(v) for v in per_instance_min.values()),
            "mean_mean_unsat": statistics.fmean(r["mean_unsat_at_rounding"] for r in group),
            "hit_cap": len(group) - len(solved), "instances": len(per_instance_min),
            "seeds": sorted({r["seed"] for r in group}), "cap": group[0]["cap"]})
    families = list(dict.fromkeys(r["family"] for r in runs))
    return sorted(rows, key=lambda r: (families.index(r["family"]), METHOD_ORDER.index(r["method"])))


def table_lines(rows):
    lines = ["| family | method | runs | solve rate | median time (solved) | mean per-instance min #unsat "
             "at rounding | mean of mean #unsat over events | runs at cap |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        median = f"{r['median_time']:.2f} s" if r["median_time"] is not None else "-"
        lines.append(f"| {r['family']} | {r['method']} | {r['runs']} | {r['solved']}/{r['runs']} "
                     f"({100 * r['solved'] / r['runs']:.0f} %) | {median} | {r['mean_min_unsat']:.2f} | "
                     f"{r['mean_mean_unsat']:.2f} | {r['hit_cap']} |")
    return lines


def reading_lines(rows):
    """What the table shows, family by family, without saying why."""
    lines = []
    for family in dict.fromkeys(r["family"] for r in rows):
        family_rows = [r for r in rows if r["family"] == family]
        best_rate = max(r["solved"] / r["runs"] for r in family_rows)
        lowest_unsat = min(r["mean_min_unsat"] for r in family_rows)
        highest = ", ".join(r["method"] for r in family_rows if r["solved"] / r["runs"] == best_rate)
        lowest = ", ".join(r["method"] for r in family_rows if r["mean_min_unsat"] == lowest_unsat)
        rates = ", ".join(f"{r['method']} {r['solved']}/{r['runs']}" for r in family_rows)
        unsat = ", ".join(f"{r['method']} {r['mean_min_unsat']:.2f}" for r in family_rows)
        lines.append(f"- **{family}** (cap {family_rows[0]['cap']:g} s): solve rates {rates}; highest: {highest}. "
                     f"Mean per-instance min #unsat at rounding {unsat}; lowest: {lowest}.")
    return lines


RUN_NOTES = [
    "- This record (run 2, 2026-08-28 23:37 to 2026-08-29 01:02) supersedes run 1 (commit 28dc078), which "
    "computed the clause products with torch's prod; its CUDA backward is slow on rows holding an exact zero, "
    "which the box relaxation produces, so run 1's fourier column had a 24x per-step handicap. The moments "
    "are identical; only speed changed.",
    "- An image-generation server (ComfyUI, pid 50779, 4.8 GB resident) was on the GPU from the start of run "
    "2 to its end. It was idle when the run started (0 % utilisation) and was seen computing at least once "
    "during the uf250 phase (95 % total utilisation at 00:14 against about 66 % for this benchmark alone); "
    "no sampler ran, so its share is unknown. Under a 30 s cap that costs steps, rounding events and polishes "
    "to every method in the same way; treat the uf250 solve rates and medians as a lower bound and the "
    "per-instance minimum #unsat as the more robust column.",
]


def write_markdown(provenance, runs, output):
    rows = summarise(runs)
    first = provenance[0] if provenance else {}
    scope = "; ".join(f"{family}: {next(r['instances'] for r in rows if r['family'] == family)} instances, "
                      f"seeds {next(r['seeds'] for r in rows if r['family'] == family)}, cap {cap:g} s"
                      for family, cap in first.get("caps", {}).items() if any(r["family"] == family for r in rows))
    lines = ["# SATLIB benchmark: F against mu and fourier", "", "## Provenance", "",
             f"- Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}; branch commit {git_head()}",
             f"- Device: {first.get('device')} ({first.get('gpu')}), torch {first.get('torch')}",
             f"- Other GPU processes at start (nvidia-smi): {first.get('gpu_processes_at_start') or 'none'}",
             f"- Runs started {first.get('timestamp')}; one warm-up solve per process, untimed, before any record",
             "- Instances: SATLIB uniform random 3-SAT, satisfiable by construction (uf50-218, uf100-430, "
             "uf250-1065), the first N files by sorted name; fixed seeds; identical scaffolding for every method",
             "", "## Scope actually run", "", scope, "",
             "Budget rule: with the caps fixed, the scope was reduced in the order N = 100 with seeds {0, 1}; "
             "seeds {0}; N = 50 for uf250 only; N = 50 for all, until a calibration on 5 instances per family "
             "estimated the run under 2.5 hours.", "", "## Table", ""]
    lines += table_lines(rows)
    lines += ["", "median time is over solved runs only; the per-instance minimum is over seeds and rounding "
              "events before the WalkSAT polish; a run is at cap when it did not solve within its time limit.",
              "", "## What the table shows", ""]
    lines += reading_lines(rows)
    lines += ["", "## Caveats", ""] + RUN_NOTES
    output.write_text("\n".join(lines) + "\n")
    print(f"wrote {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="results.md from the SATLIB JSONL")
    parser.add_argument("--input", type=Path, default=HERE / "satlib_results.jsonl")
    parser.add_argument("--output", type=Path, default=HERE / "results.md")
    arguments = parser.parse_args()
    write_markdown(*load_records(arguments.input), arguments.output)
