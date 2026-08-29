#!/usr/bin/env python3
"""The markdown of a posterior calibration run: the reliability curve of the final
Beta-mixture posterior (bins against the fraction of instances actually unsatisfiable), the
same at fixed times, and per uuf instance the time to 0.99 against kissat's fastest
refutation; false alarms are the satisfiable instances whose posterior passed 0.99 before
their solution."""
import argparse
import statistics
from pathlib import Path

from walk_runs import BENCHMARK, load_records

BINS = [(0.0, 0.5), (0.5, 0.9), (0.9, 0.99), (0.99, 0.999), (0.999, 1.0001)]
TIMES = (0.5, 2.0, 5.0)


def posterior_at(run, seconds):
    values = [beta for t, beta, _, _ in run["timeline"] if t <= seconds]
    return values[-1] if values else None


def reliability_lines(runs, at_seconds=None):
    lines = []
    for low, high in BINS:
        members = [r for r in runs if (value := (r["posterior_beta"] if at_seconds is None else posterior_at(r, at_seconds))) is not None
                   and low <= value < high]
        if members:
            unsat = sum(not r["satisfiable"] for r in members)
            lines.append(f"| [{low}, {min(high, 1.0)}) | {len(members)} | {unsat}/{len(members)} = {unsat / len(members):.2f} |")
    return lines


def write_markdown(records, path):
    provenance = [r for r in records if r.get("kind") == "provenance" and r.get("phase") in ("loop", "all")]
    runs = [r for r in records if r.get("kind") == "run"]
    kissat = {r["instance"]: r for r in records if r.get("kind") == "kissat"}
    loop = provenance[-1] if provenance else {}
    arguments = loop.get("arguments", {})
    sat_runs, unsat_runs = [r for r in runs if r["satisfiable"]], [r for r in runs if not r["satisfiable"]]
    solved = [r for r in sat_runs if r["status"] == "SATISFIABLE"]
    lines = ["# Posterior calibration in C++: uf250-1065 against uuf250-1065", "",
             f"- Loop phase {loop.get('timestamp')}; commit {loop.get('commit')}; binary sha256 {loop.get('binary_sha256')}; backend "
             f"{arguments.get('backend')}; cap {arguments.get('cap')} s; {arguments.get('slots')} slots, rigorous fraction "
             f"{arguments.get('rigorous_fraction')}, uniform starts, {arguments.get('polish_flips_per_variable')} n SKC flips per run, "
             f"prior P(SAT) = {arguments.get('prior_satisfiable')}.",
             f"- Beta prior of a satisfiable instance's per-restart success: Beta({loop.get('beta_prior', ['?', '?'])[0]:.4g}, "
             f"{loop.get('beta_prior', ['?', '?'])[1]:.4g}), {loop.get('beta_prior_how')}.",
             f"- Instances: {len(sat_runs)} satisfiable ({len(solved)} solved under the cap) and {len(unsat_runs)} unsatisfiable. "
             "A solved instance's posterior is the one after its last failed run.",
             "- The rigorous posterior stays at the prior throughout: Schoening's bound is (3/4)^250 / 2253 per try.", "",
             "## Reliability of the final Beta-mixture posterior", "", "| posterior bin | instances | actually UNSAT |", "|---|---|---|"]
    lines += reliability_lines(runs)
    for seconds in TIMES:
        lines += ["", f"## The same at {seconds:g} s", "", "| posterior bin | instances | actually UNSAT |", "|---|---|---|"] + reliability_lines(runs, seconds)
    lines += ["", "## Time to a 0.99 posterior against kissat's refutation (uuf250-1065)", "",
              "| instance | seconds to 0.99 | runs at cap | heuristic failures | kissat fastest (s) |", "|---|---|---|---|---|"]
    ratios = []
    for run in unsat_runs:
        reference = kissat.get(run["instance"])
        if reference and run["seconds_to_target"] is not None:
            ratios.append(run["seconds_to_target"] / reference["fastest"])
        lines.append(f"| {run['instance']} | {run['seconds_to_target'] if run['seconds_to_target'] is not None else 'never'} | {run['runs']} | "
                     f"{run['heuristic_failures']} | {reference['fastest'] if reference else '-'} |")
    if ratios:
        lines += ["", f"Median ratio (time to 0.99) / (kissat refutation): {statistics.median(ratios):.3f}; kissat median "
                  f"{statistics.median(k['fastest'] for k in kissat.values()):.3f} s, posterior median "
                  f"{statistics.median(r['seconds_to_target'] for r in unsat_runs if r['seconds_to_target'] is not None):.3f} s."]
    false_alarms = [r for r in sat_runs if r["seconds_to_target"] is not None]
    unsolved_alarms = [r for r in false_alarms if r["status"] != "SATISFIABLE"]
    lines += ["", f"Satisfiable instances whose posterior reached 0.99 before a solution (false alarms): {len(false_alarms)} of {len(sat_runs)}, "
              f"of which {len(unsolved_alarms)} were still unsolved at the cap.", "",
              "Every run is in posterior_calibration.jsonl with its timeline, seed 0, command, commit and binary hash."]
    path.write_text("\n".join(lines) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", type=Path, default=BENCHMARK / "posterior_calibration.jsonl")
    parser.add_argument("--output", type=Path, default=BENCHMARK / "posterior_calibration.md")
    arguments = parser.parse_args()
    write_markdown(load_records(arguments.input), arguments.output)
