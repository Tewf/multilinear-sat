"""Run every method over SATLIB families in one process; one JSONL record per (family, method,
instance, seed), resumable, with one untimed warm-up solve before any timing."""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PACKAGE))
import torch  # noqa: E402

from adjacency import build_clause_adjacency  # noqa: E402
from configuration import Configuration  # noqa: E402
from dimacs import read_dimacs  # noqa: E402
from methods import METHODS, build_method  # noqa: E402
from solver import solve  # noqa: E402

INSTANCES_DIRECTORY = PACKAGE.parent / "benchmark" / "instances"
RESULTS_PATH = Path(__file__).resolve().parent / "satlib_results.jsonl"
TIME_CAP_SECONDS = {"uf50-218": 5.0, "uf100-430": 15.0, "uf250-1065": 30.0}  # never cut to fit a budget
NUM_INSTANCES = 100        # the first N files by sorted name
SEEDS = (0, 1)
WARM_UP_SECONDS = 2.0


def parse_arguments():
    parser = argparse.ArgumentParser(description="SATLIB benchmark of the three objectives")
    parser.add_argument("--device", default=Configuration.device)
    parser.add_argument("--families", nargs="+", default=list(TIME_CAP_SECONDS))
    parser.add_argument("--caps", nargs="+", type=float, help="seconds, aligned with --families")
    parser.add_argument("--methods", nargs="+", default=list(METHODS), choices=list(METHODS))
    parser.add_argument("--seeds", nargs="+", type=int, default=list(SEEDS))
    parser.add_argument("--limit-instances", type=int, default=NUM_INSTANCES)
    parser.add_argument("--output", type=Path, default=RESULTS_PATH)
    return parser.parse_args()


def gpu_processes():
    query = ["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader"]
    try:
        return subprocess.run(query, capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "nvidia-smi unavailable"


def existing_keys(path):
    if not path.exists():
        return set()
    with open(path) as handle:
        records = [json.loads(line) for line in handle if line.strip()]
    return {(r["family"], r["method"], r["instance"], r["seed"]) for r in records if r.get("kind") == "run"}


def load_instance(path, device):
    formula = read_dimacs(path).to(device)
    return formula, build_clause_adjacency(formula).to(device)


def run_once(formula, adjacency, method, seed, cap, device):
    configuration = Configuration(time_limit_seconds=cap, device=device)
    objective, relaxation = build_method(method, formula, adjacency, configuration.variance_floor)
    return solve(formula, objective, relaxation, configuration, seed)


def main():
    arguments = parse_arguments()
    caps = dict(zip(arguments.families, arguments.caps)) if arguments.caps else TIME_CAP_SECONDS
    instances = {family: sorted(INSTANCES_DIRECTORY.joinpath(family).glob("*.cnf"))[: arguments.limit_instances]
                 for family in arguments.families}
    runs = sum(len(files) for files in instances.values()) * len(arguments.seeds) * len(arguments.methods)
    worst_case = sum(len(files) * caps[family] for family, files in instances.items()) \
        * len(arguments.seeds) * len(arguments.methods)
    done = existing_keys(arguments.output)
    print(f"{runs} runs, {len(done)} already recorded, worst case {worst_case / 3600:.2f} h", flush=True)
    with open(arguments.output, "a") as output:
        output.write(json.dumps({"kind": "provenance", "timestamp": datetime.now().isoformat(timespec="seconds"),
                                 "device": arguments.device, "torch": torch.__version__,
                                 "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
                                 "gpu_processes_at_start": gpu_processes(), "caps": caps,
                                 "num_instances": arguments.limit_instances, "seeds": arguments.seeds}) + "\n")
        first_family = arguments.families[0]
        warm_formula, warm_adjacency = load_instance(instances[first_family][0], arguments.device)
        run_once(warm_formula, warm_adjacency, arguments.methods[0], 0, WARM_UP_SECONDS, arguments.device)
        for family, files in instances.items():
            for path in files:
                formula, adjacency = load_instance(path, arguments.device)
                for seed in arguments.seeds:
                    for method in arguments.methods:
                        if (family, method, path.name, seed) in done:
                            continue
                        result = run_once(formula, adjacency, method, seed, caps[family], arguments.device)
                        record = {"kind": "run", "family": family, "method": method, "instance": path.name,
                                  "seed": seed, "status": "SATISFIABLE" if result.solved else "UNKNOWN",
                                  "time_seconds": round(result.time_seconds, 4), "restarts": result.num_restarts,
                                  "steps": result.num_steps, "min_unsat_at_rounding": result.min_unsat_at_rounding,
                                  "mean_unsat_at_rounding": round(result.mean_unsat_at_rounding, 3),
                                  "rounding_events": result.num_rounding_events, "cap": caps[family],
                                  "timestamp": datetime.now().isoformat(timespec="seconds")}
                        output.write(json.dumps(record) + "\n")
                        output.flush()
                        print(f"{family} {path.name} seed={seed} {method:7s} {record['status']:11s} "
                              f"{record['time_seconds']:7.2f}s min_unsat={record['min_unsat_at_rounding']}", flush=True)


if __name__ == "__main__":
    main()
