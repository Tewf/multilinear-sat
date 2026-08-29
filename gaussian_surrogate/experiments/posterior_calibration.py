"""Calibration of the UNSAT posteriors on uf250-1065 (satisfiable) against uuf250-1065
(unsatisfiable, the same family): the tilted loop with half its groups rigorous under a cap, the
two posteriors logged over time, and per uuf instance the time the Beta-mixture posterior takes
to reach 0.99 against kissat's refutation time (fastest of three). The loop runs in walk mode
with the polish's flip budget so that one heuristic restart is the seed comparison's tilted_walk
protocol, on which the Beta(a, b) prior is fitted by moments. Phases: kissat (CPU), loop (GPU),
all. One JSONL; the table is posterior_table.py."""
import argparse
import csv
import json
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import torch

PACKAGE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PACKAGE))
from configuration import Configuration                  # noqa: E402
from dimacs import read_dimacs                           # noqa: E402
from posterior import fit_beta_by_moments                # noqa: E402
from tilted_loop import solve_tilted                     # noqa: E402

INSTANCES_DIRECTORY = PACKAGE.parent / "benchmark" / "instances"
HERE = Path(__file__).resolve().parent
FAMILIES = {"uf250-1065": True, "uuf250-1065": False}     # family: satisfiable
POSTERIOR_TARGET = 0.99


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--phase", choices=["kissat", "loop", "all"], default="all")
    parser.add_argument("--device", default=Configuration.device)
    parser.add_argument("--instances", type=int, default=20)
    parser.add_argument("--cap", type=float, default=60.0, help="seconds per instance for the loop")
    parser.add_argument("--slots-per-group", type=int, default=32)
    parser.add_argument("--groups", type=int, default=16)
    parser.add_argument("--flips-per-variable", type=float, default=10.0, help="the polish budget of the seed comparison")
    parser.add_argument("--rigorous-fraction", type=float, default=0.5)
    parser.add_argument("--prior-satisfiable", type=float, default=0.5)
    parser.add_argument("--beta-prior", type=float, nargs=2, metavar=("A", "B"),
                        help="skip the fit and use Beta(A, B)")
    parser.add_argument("--seed-comparison", type=Path, default=HERE / "seed_comparison.jsonl")
    parser.add_argument("--kissat-runs", type=int, default=3)
    parser.add_argument("--output", type=Path, default=HERE / "posterior_calibration.jsonl")
    return parser.parse_args()


def instance_paths(count):
    return [(family, satisfiable, path) for family, satisfiable in FAMILIES.items()
            for path in sorted((INSTANCES_DIRECTORY / family).glob("*.cnf"))[:count]]


def fitted_beta_prior(arguments):
    """(a, b, how): from the seed comparison's tilted_walk arm on uf250-1065, else the flag, else (1, 1)."""
    if arguments.beta_prior:
        return (*arguments.beta_prior, "given on the command line")
    if arguments.seed_comparison.exists():
        with open(arguments.seed_comparison) as handle:
            records = [json.loads(line) for line in handle if line.strip()]
        fractions = [r["success_fraction"] for r in records
                     if r.get("kind") == "run" and r["family"] == "uf250-1065" and r["seed_method"] == "tilted_walk"]
        if len(fractions) >= 3:
            try:
                a, b = fit_beta_by_moments(fractions)
                return a, b, f"moments of {len(fractions)} tilted_walk fractions on uf250-1065 (mean {statistics.fmean(fractions):.4f})"
            except ValueError as reason:
                return 1.0, 1.0, f"uniform: the fit failed ({reason})"
    return 1.0, 1.0, "uniform: no seed comparison record to fit on"


def kissat_times(path, runs):
    """Wall seconds of `runs` kissat runs and its verdict (exit 10 SAT, 20 UNSAT). kissat rejects
    SATLIB's layout (a parse error on line 1), so the formula is re-emitted as plain DIMACS."""
    formula = read_dimacs(path)
    with tempfile.NamedTemporaryFile("w", suffix=".cnf", delete=False) as clean:
        clean.write(f"p cnf {formula.num_variables} {formula.num_clauses}\n")
        clean.writelines(" ".join(map(str, clause)) + " 0\n" for clause in formula.clauses.tolist())
    times, codes = [], []
    for _ in range(runs):
        start = time.perf_counter()
        completed = subprocess.run(["kissat", "-q", clean.name], capture_output=True, text=True)
        times.append(round(time.perf_counter() - start, 4))
        codes.append(completed.returncode)
    Path(clean.name).unlink()
    return times, codes


def run_loop(path, arguments, prior):
    configuration = Configuration(device=arguments.device, time_limit_seconds=arguments.cap, walk_mode="walk",
                                  tilted_num_groups=arguments.groups, tilted_slots_per_group=arguments.slots_per_group,
                                  tilted_walk_flips_per_variable=arguments.flips_per_variable,
                                  rigorous_fraction=arguments.rigorous_fraction, prior_satisfiable=arguments.prior_satisfiable,
                                  beta_prior_a=prior[0], beta_prior_b=prior[1])
    formula = read_dimacs(path).to(arguments.device)
    with tempfile.NamedTemporaryFile(suffix=".csv") as trajectory:
        result = solve_tilted(formula, configuration, seed=0, trajectory_path=trajectory.name)
        with open(trajectory.name) as handle:
            rows = list(csv.DictReader(handle))
    timeline = [(float(r["seconds"]), float(r["posterior_beta"]), float(r["posterior_rigorous"])) for r in rows]
    reached = [seconds for seconds, beta_posterior, _ in timeline if beta_posterior >= POSTERIOR_TARGET]
    return result, timeline, reached[0] if reached else None


def main():
    arguments = parse_arguments()
    a, b, how = fitted_beta_prior(arguments)
    with open(arguments.output, "a") as output:
        output.write(json.dumps(dict(kind="provenance", timestamp=datetime.now().isoformat(timespec="seconds"),
                                     commit=subprocess.run(["git", "rev-parse", "--short=10", "HEAD"], cwd=PACKAGE,
                                                           capture_output=True, text=True).stdout.strip(),
                                     phase=arguments.phase, device=arguments.device, torch=torch.__version__,
                                     gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
                                     beta_prior=[a, b], beta_prior_how=how,
                                     arguments={k: str(v) for k, v in vars(arguments).items()})) + "\n")
        for family, satisfiable, path in instance_paths(arguments.instances):
            if arguments.phase in ("kissat", "all") and not satisfiable:
                times, codes = kissat_times(path, arguments.kissat_runs)
                output.write(json.dumps(dict(kind="kissat", family=family, instance=path.name, seconds=times,
                                             fastest=min(times), exit_codes=codes)) + "\n")
                print(f"kissat {path.name} {times} exit {codes}", flush=True)
            if arguments.phase in ("loop", "all"):
                result, timeline, time_to_target = run_loop(path, arguments, (a, b))
                output.write(json.dumps(dict(
                    kind="run", family=family, instance=path.name, satisfiable=satisfiable,
                    status="SATISFIABLE" if result.solved else "UNKNOWN", seconds=round(result.time_seconds, 3),
                    steps=result.num_steps, heuristic_failures=result.heuristic_failures,
                    rigorous_failures=result.rigorous_failures, posterior_beta=result.posterior_beta,
                    posterior_rigorous=result.posterior_rigorous, seconds_to_target=time_to_target,
                    timeline=timeline[:: max(1, len(timeline) // 200)])) + "\n")
                print(f"{family} {path.name} {'SAT' if result.solved else 'unknown':7s} {result.time_seconds:6.1f}s "
                      f"steps={result.num_steps} k={result.heuristic_failures} posterior_beta={result.posterior_beta:.4f} "
                      f"to {POSTERIOR_TARGET}: {time_to_target}", flush=True)
            output.flush()


if __name__ == "__main__":
    main()
