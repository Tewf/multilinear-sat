"""The markdown of a posterior calibration run: the reliability curve of the final Beta-mixture
posterior (bins against the fraction of instances actually unsatisfiable), the same at fixed
times, and per uuf instance the time to 0.99 against kissat's fastest refutation."""
import argparse
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
BINS = [(0.0, 0.5), (0.5, 0.9), (0.9, 0.99), (0.99, 0.999), (0.999, 1.0001)]
TIMES = (1.0, 5.0, 20.0)


def load(path):
    with open(path) as handle:
        records = [json.loads(line) for line in handle if line.strip()]
    kinds = {kind: [r for r in records if r.get("kind") == kind] for kind in ("provenance", "run", "kissat")}
    return kinds["provenance"], kinds["run"], {r["instance"]: r for r in kinds["kissat"]}


def posterior_at(run, seconds):
    """The Beta posterior the loop reported last before `seconds` (the prior before its first step)."""
    values = [beta_posterior for t, beta_posterior, _ in run["timeline"] if t <= seconds]
    return values[-1] if values else None


def reliability_lines(runs, at_seconds=None):
    """One line per bin: instances whose posterior (final, or at a time) falls in it, and how many are UNSAT."""
    lines = []
    for low, high in BINS:
        members = []
        for run in runs:
            value = run["posterior_beta"] if at_seconds is None else posterior_at(run, at_seconds)
            if value is not None and low <= value < high:
                members.append(run)
        if members:
            unsat = sum(not r["satisfiable"] for r in members)
            lines.append(f"| [{low}, {min(high, 1.0)}) | {len(members)} | {unsat}/{len(members)} = {unsat / len(members):.2f} |")
    return lines


def write_markdown(provenance, runs, kissat, path):
    loop = next((p for p in reversed(provenance) if p.get("phase") in ("loop", "all")), provenance[-1] if provenance else {})
    arguments = loop.get("arguments", {})
    solved_sat = [r for r in runs if r["satisfiable"] and r["status"] == "SATISFIABLE"]
    sat_runs, unsat_runs = [r for r in runs if r["satisfiable"]], [r for r in runs if not r["satisfiable"]]
    lines = ["# Posterior calibration: uf250-1065 against uuf250-1065", "",
             f"- Date {loop.get('timestamp')}; commit {loop.get('commit')}; device {loop.get('device')} ({loop.get('gpu')}); "
             f"cap {arguments.get('cap')} s; {arguments.get('groups')} groups of {arguments.get('slots_per_group')} slots, "
             f"rigorous fraction {arguments.get('rigorous_fraction')}, walk mode walk with {arguments.get('flips_per_variable')} n "
             f"flips per restart (the seed comparison's polish), prior P(SAT) = {arguments.get('prior_satisfiable')}.",
             f"- Beta prior of a satisfiable instance's per-restart success: Beta({loop.get('beta_prior', ['?', '?'])[0]:.4g}, "
             f"{loop.get('beta_prior', ['?', '?'])[1]:.4g}), {loop.get('beta_prior_how')}.",
             f"- Instances: {len(sat_runs)} satisfiable ({len(solved_sat)} solved under the cap) and {len(unsat_runs)} "
             "unsatisfiable. A satisfiable instance that is solved stops reporting; its last posterior is the one binned.",
             "- The rigorous posterior stays at the prior throughout: Schöning's bound is (3/4)^250 / 2253 per try.", "",
             "## Reliability of the final Beta-mixture posterior", "",
             "| posterior bin | instances | actually UNSAT |", "|---|---|---|"] + reliability_lines(runs)
    for seconds in TIMES:
        lines += ["", f"## The same at {seconds:g} s", "", "| posterior bin | instances | actually UNSAT |", "|---|---|---|"]
        lines += reliability_lines(runs, seconds)
    lines += ["", "## Time to a 0.99 posterior against kissat's refutation (uuf250-1065)", "",
              "| instance | seconds to 0.99 | steps at cap | heuristic failures | kissat fastest of "
              f"{len(next(iter(kissat.values()))['seconds']) if kissat else '?'} (s) |", "|---|---|---|---|---|"]
    ratios = []
    for run in unsat_runs:
        reference = kissat.get(run["instance"])
        to_target = run["seconds_to_target"]
        if reference and to_target is not None:
            ratios.append(to_target / reference["fastest"])
        lines.append(f"| {run['instance']} | {to_target if to_target is not None else 'never'} | {run['steps']} | "
                     f"{run['heuristic_failures']} | {reference['fastest'] if reference else '-'} |")
    if ratios:
        lines += ["", f"Median ratio (time to 0.99) / (kissat refutation): {statistics.median(ratios):.2f}; "
                  f"kissat median {statistics.median(k['fastest'] for k in kissat.values()):.3f} s, posterior median "
                  f"{statistics.median(r['seconds_to_target'] for r in unsat_runs if r['seconds_to_target'] is not None):.3f} s."]
    false_alarms = [r for r in sat_runs if r["status"] != "SATISFIABLE" and r["posterior_beta"] >= 0.99]
    lines += ["", f"Satisfiable instances unsolved under the cap whose posterior reached 0.99 (false alarms): "
              f"{len(false_alarms)} of {len(sat_runs)}.", "",
              "Every run is in posterior_calibration.jsonl with its timeline, seed 0, commit and timestamps."]
    path.write_text("\n".join(lines) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", type=Path, default=HERE / "posterior_calibration.jsonl")
    parser.add_argument("--output", type=Path, default=HERE / "posterior_calibration.md")
    arguments = parser.parse_args()
    write_markdown(*load(arguments.input), arguments.output)
