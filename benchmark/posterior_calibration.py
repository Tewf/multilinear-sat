#!/usr/bin/env python3
"""Calibration of the UNSAT posteriors on uf250-1065 (satisfiable) against uuf250-1065
(unsatisfiable, the same family): the walk from uniform starts, 10n SKC flips at 4096 slots
with half the batch rigorous, under a cap, the posteriors read after every run from the
solver's verbose lines; per uuf instance the time the Beta-mixture posterior takes to reach
0.99 against kissat's refutation time (fastest of three). The Beta(a, b) prior is fitted by
moments on the seed comparison's uniform arm on uf250 (the same polish), else Beta(1, 1).
Phases: kissat (CPU), loop (GPU), all. One JSONL; the table is posterior_table.py."""
import argparse
import re
import statistics
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path

from walk_runs import BENCHMARK, append_record, frozen_binary, load_records, provenance, run_solver, satlib_instances

FAMILIES = {"uf250-1065": True, "uuf250-1065": False}   # family: satisfiable
POSTERIOR_TARGET = 0.99
RUN_LINE = re.compile(r"c run (\d+) elapsed ([\d.]+) best (\d+) restarts \d+ heuristic_failures (\d+) rigorous_failures (\d+) "
                      r"posterior_beta ([\d.e+-]+) posterior_rigorous ([\d.e+-]+)")


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--phase", choices=["kissat", "loop", "all"], default="all")
    parser.add_argument("--build", default="build-cuda")
    parser.add_argument("--backend", default="cuda")
    parser.add_argument("--instances", type=int, default=20)
    parser.add_argument("--cap", type=float, default=20.0, help="seconds per instance for the loop")
    parser.add_argument("--slots", type=int, default=4096)
    parser.add_argument("--polish-flips-per-variable", type=int, default=10)
    parser.add_argument("--rigorous-fraction", type=float, default=0.5)
    parser.add_argument("--prior-satisfiable", type=float, default=0.5)
    parser.add_argument("--beta-prior", type=float, nargs=2, metavar=("A", "B"), help="skip the fit and use Beta(A, B)")
    parser.add_argument("--seed-comparison", type=Path, default=BENCHMARK / "seed_comparison.jsonl")
    parser.add_argument("--kissat-runs", type=int, default=3)
    parser.add_argument("--output", type=Path, default=BENCHMARK / "posterior_calibration.jsonl")
    return parser.parse_args()


def fit_beta_by_moments(fractions):
    """(a, b) of the Beta law with the sample mean and variance of the fractions in (0, 1)."""
    mean = statistics.fmean(fractions)
    variance = statistics.variance(fractions)
    if not 0.0 < mean < 1.0 or variance <= 0.0 or variance >= mean * (1.0 - mean):
        raise ValueError("no Beta fit by moments: need 0 < mean < 1 and variance < mean (1 - mean)")
    common = mean * (1.0 - mean) / variance - 1.0
    return mean * common, (1.0 - mean) * common


def fitted_beta_prior(arguments):
    if arguments.beta_prior:
        return (*arguments.beta_prior, "given on the command line")
    fractions = [r["success_fraction"] for r in load_records(arguments.seed_comparison)
                 if r.get("kind") == "run" and r["family"] == "uf250-1065" and r["arm"] == "uniform" and r["success_fraction"] is not None]
    if len(fractions) >= 3:
        try:
            a, b = fit_beta_by_moments(fractions)
            return a, b, f"moments of {len(fractions)} uniform-arm fractions on uf250-1065 (mean {statistics.fmean(fractions):.4f})"
        except ValueError as reason:
            return 1.0, 1.0, f"uniform: the fit failed ({reason})"
    return 1.0, 1.0, "uniform: no seed comparison record to fit on"


def clean_dimacs(path):
    """SATLIB's layout (a '%' trailer and padded header) makes kissat stop at line 1, so the
    formula is re-emitted as plain DIMACS into a temporary file."""
    clauses, current, header = [], [], None
    for line in open(path):
        if line.startswith("%"):
            break
        if line.startswith("c"):
            continue
        if line.startswith("p"):
            header = line.split()
            continue
        for token in line.split():
            if token == "0":
                if current:
                    clauses.append(current)
                current = []
            else:
                current.append(token)
    clean = tempfile.NamedTemporaryFile("w", suffix=".cnf", delete=False)
    clean.write(f"p cnf {header[2]} {len(clauses)}\n")
    clean.writelines(" ".join(clause) + " 0\n" for clause in clauses)
    clean.close()
    return Path(clean.name)


def kissat_times(path, runs):
    clean = clean_dimacs(path)
    times, codes = [], []
    for _ in range(runs):
        start = time.perf_counter()
        completed = subprocess.run(["kissat", "-q", str(clean)], capture_output=True, text=True)
        times.append(round(time.perf_counter() - start, 4))
        codes.append(completed.returncode)
    clean.unlink()
    return times, codes


def variable_count(path):
    for line in open(path):
        if line.startswith("p "):
            return int(line.split()[2])
    raise ValueError(f"no header in {path}")


def loop_record(binary, arguments, family, satisfiable, path, prior):
    flags = ["--backend", arguments.backend, "--batch-size", arguments.slots, "--seed-kind", "uniform", "--walk-rule", "skc",
             "--polish-flips", arguments.polish_flips_per_variable * variable_count(path), "--rigorous-fraction", arguments.rigorous_fraction,
             "--prior-satisfiable", arguments.prior_satisfiable, "--beta-prior-a", prior[0], "--beta-prior-b", prior[1], "--seed", 0, "--verbose"]
    result = run_solver(binary, path, flags, arguments.cap)
    timeline = [(float(m.group(2)), float(m.group(6)), float(m.group(7)), int(m.group(4))) for m in RUN_LINE.finditer(result["stderr"])]
    reached = [seconds for seconds, beta, _, _ in timeline if beta >= POSTERIOR_TARGET]
    stats = result["json"] or {}
    return dict(kind="run", family=family, instance=path.name, satisfiable=satisfiable, status=result["status"],
                seconds=stats.get("elapsed_seconds"), runs=stats.get("runs"), heuristic_failures=stats.get("heuristic_failures"),
                rigorous_failures=stats.get("rigorous_failures"), posterior_beta=stats.get("posterior_beta"),
                posterior_rigorous=stats.get("posterior_rigorous"), seconds_to_target=reached[0] if reached else None,
                timeline=timeline[:: max(1, len(timeline) // 200)], command=result["command"])


def main():
    arguments = parse_arguments()
    a, b, how = fitted_beta_prior(arguments)
    binary = frozen_binary(arguments.build) if arguments.phase != "kissat" else None
    stamp = provenance(binary, arguments) if binary else dict(kind="provenance", phase="kissat", timestamp=datetime.now().isoformat(timespec="seconds"))
    stamp.update(phase=arguments.phase, beta_prior=[a, b], beta_prior_how=how)
    append_record(arguments.output, stamp)
    done = {(r["kind"], r["instance"]) for r in load_records(arguments.output) if r.get("kind") in ("kissat", "run")}
    for family, satisfiable in FAMILIES.items():
        for path in satlib_instances(family, arguments.instances):
            if arguments.phase in ("kissat", "all") and not satisfiable and ("kissat", path.name) not in done:
                times, codes = kissat_times(path, arguments.kissat_runs)
                append_record(arguments.output, dict(kind="kissat", family=family, instance=path.name, seconds=times, fastest=min(times), exit_codes=codes))
                print(f"kissat {path.name} {times} exit {codes}", flush=True)
            if arguments.phase in ("loop", "all") and ("run", path.name) not in done:
                record = loop_record(binary, arguments, family, satisfiable, path, (a, b))
                append_record(arguments.output, record)
                print(f"{family} {path.name} {record['status']:11s} {record['seconds']}s runs={record['runs']} k={record['heuristic_failures']} "
                      f"posterior_beta={record['posterior_beta']} to {POSTERIOR_TARGET}: {record['seconds_to_target']}", flush=True)


if __name__ == "__main__":
    main()
