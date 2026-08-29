#!/usr/bin/env python3
"""Runs every arm of the stage plan not yet in arms_results.jsonl: one record per (arm,
family, instance, seed), probSAT beside every family of the base stage, resumable. CUDA runs
start only on a free card (two nvidia-smi readings a minute apart at 0 % and no process
holding it) and a package under the temperature limit; a provenance block opens every
family stage. Run from anywhere; paths in the records are repository-relative."""
import argparse
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import arms                                                                                   # noqa: E402
from walk_runs import (RAW, append_record, frozen_binary, load_records, provenance, run_probsat,  # noqa: E402
                       run_solver, sha256_of)

RUN_LINE = re.compile(r"c run (\d+) elapsed ([\d.]+) best (\d+) restarts \d+ heuristic_failures (\d+) rigorous_failures (\d+) "
                      r"posterior_beta [\d.e+-]+ posterior_rigorous [\d.e+-]+ scale (\d+) polish_successes (\d+) flips (\d+) "
                      r"seed_seconds ([\d.]+) polish_seconds ([\d.]+)")


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--stages", nargs="*", default=[name for name, _, _ in arms.STAGES if name in ("base", "seeds", "rule_and_batch", "schedule_and_polish", "rigorous")],
                        choices=[name for name, _, _ in arms.STAGES])
    parser.add_argument("--families", nargs="*", default=None, help="restrict every stage to these families")
    parser.add_argument("--build", default="build-cuda")
    parser.add_argument("--dry-run", action="store_true", help="list the runs still to do and exit")
    parser.add_argument("--no-gate", action="store_true", help="skip the GPU and temperature gates (a smoke test, never a record)")
    return parser.parse_args()


def package_celsius():
    try:
        output = subprocess.run(["sensors"], capture_output=True, text=True, timeout=10).stdout
        match = re.search(r"Package id 0:\s+\+([\d.]+)", output)
        return float(match.group(1)) if match else None
    except (OSError, subprocess.SubprocessError):
        return None


def gpu_reading():
    query = ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used", "--format=csv,noheader,nounits"]
    utilisation, memory = subprocess.run(query, capture_output=True, text=True, timeout=10).stdout.strip().split(",")
    processes = subprocess.run(["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader"],
                               capture_output=True, text=True, timeout=10).stdout.strip()
    return int(utilisation), int(memory), processes


def wait_for_free_card(log):
    """Two readings a minute apart at 0 % utilisation and under the held-memory line, and the
    package under the limit; the state of the second reading is what the stage records."""
    while True:
        first = gpu_reading()
        time.sleep(60)
        second = gpu_reading()
        celsius = package_celsius()
        free = all(u == 0 and m < arms.GPU_MEMORY_HELD_MIB for u, m, _ in (first, second))
        cool = celsius is not None and celsius < arms.PACKAGE_CELSIUS_LIMIT
        log(f"gate: gpu {first[0]}%/{first[1]} MiB then {second[0]}%/{second[1]} MiB, package {celsius} C: {'go' if free and cool else 'wait'}")
        if free and cool:
            return dict(gpu_utilisation=[first[0], second[0]], gpu_memory_mib=[first[1], second[1]], gpu_processes=second[2], package_celsius=celsius)


def wait_for_cool_package(log):
    for _ in range(60):
        celsius = package_celsius()
        if celsius is None or celsius < arms.PACKAGE_CELSIUS_LIMIT:
            return celsius
        log(f"package at {celsius} C, waiting")
        time.sleep(10)
    return package_celsius()


def variable_count(path):
    with open(path) as handle:
        for line in handle:
            if line.startswith("p "):
                return int(line.split()[2])
    raise ValueError(f"no header in {path}")


def timeline(stderr):
    return [dict(run=int(m[1]), elapsed=float(m[2]), best=int(m[3]), heuristic_failures=int(m[4]), rigorous_failures=int(m[5]),
                 scale=int(m[6]), polish_successes=int(m[7]), flips=int(m[8]), seed_seconds=float(m[9]), polish_seconds=float(m[10]))
            for m in RUN_LINE.finditer(stderr)]


def solver_record(binary, arm, family, path, seed, gate):
    n = variable_count(path)
    runs, schedule, polish_flips = arms.run_count_and_polish(arm, family, n)
    celsius_before = package_celsius()
    result = run_solver(binary, path, arms.flags(arm, family, n, seed), arms.SOLVER_CAP_SECONDS)
    stats = result["json"] or {}
    lines = timeline(result["stderr"])
    first = next((line["elapsed"] for line in lines if line["polish_successes"] > 0), None)
    if first is None and result["status"] == "SATISFIABLE":
        first = stats.get("elapsed_seconds")
    c = arms.configuration(arm)
    heuristic_slots = c["batch"] - round(c["rigorous"] * c["batch"])
    return dict(kind="run", arm=arm, family=family, instance=path.name, seed=seed, variable_count=n, configuration=c,
                run_limit=runs, schedule=schedule, polish_flips_per_run=polish_flips, heuristic_slots=heuristic_slots,
                runs_completed=stats.get("runs"), polish_successes=stats.get("polish_successes"),
                heuristic_failures=stats.get("heuristic_failures"), rigorous_failures=stats.get("rigorous_failures"),
                flips=stats.get("flips"), seed_seconds=stats.get("seed_seconds"), polish_seconds=stats.get("polish_seconds"),
                elapsed_seconds=stats.get("elapsed_seconds"), wall_seconds=result["wall_seconds"], status=result["status"],
                capped=result["hung"] or (stats.get("elapsed_seconds") or 0) >= arms.SOLVER_CAP_SECONDS,
                first_solution_seconds=first, timeline=lines, package_celsius=[celsius_before, package_celsius()],
                gate=gate, command=result["command"], timestamp=datetime.now().isoformat(timespec="seconds"))


def probsat_record(family, path, seed):
    result = run_probsat(path, seed, arms.FAMILIES[family]["probsat_cap"])
    return dict(kind="run", arm="probsat", family=family, instance=path.name, seed=seed, status=result["status"],
                wall_seconds=result["wall_seconds"], cpu_seconds=result["cpu_seconds"], flips=result["flips"], capped=result["hung"],
                cap_seconds=arms.FAMILIES[family]["probsat_cap"], package_celsius=[package_celsius()], command=result["command"],
                timestamp=datetime.now().isoformat(timespec="seconds"))


def main():
    arguments = parse_arguments()
    log = lambda message: print(f"{datetime.now().strftime('%H:%M:%S')} {message}", flush=True)
    done = {(r["arm"], r["family"], r["instance"], r["seed"]) for r in load_records(arms.RECORDS) if r.get("kind") == "run"}
    todo = []
    for stage, stage_arms, families in arms.STAGES:
        if stage not in arguments.stages:
            continue
        for family in families:
            if arguments.families and family not in arguments.families:
                continue
            for arm in stage_arms + (["probsat"] if stage == "base" else []):
                for path in arms.instances(family):
                    for seed in arms.FAMILIES[family]["seeds"]:
                        if (arm, family, path.name, seed) not in done:
                            todo.append((stage, family, arm, path, seed))
    log(f"{len(todo)} runs to do, {len(done)} recorded")
    if arguments.dry_run:
        for stage, family, arm, path, seed in todo:
            print(f"{stage:20s} {family:12s} {arm:24s} {path.name} seed={seed}")
        return
    binary = frozen_binary(arguments.build)
    log(f"binary {binary.name} sha256 {sha256_of(binary)}")
    current_stage = None
    gate = None
    for stage, family, arm, path, seed in todo:
        if (stage, family) != current_stage:
            current_stage = (stage, family)
            gate = None if arguments.no_gate else wait_for_free_card(log)
            append_record(arms.RECORDS, {**provenance(binary, arguments), "stage": stage, "family": family, "gate": gate})
        if arm == "probsat":
            record = probsat_record(family, path, seed)
            log(f"{family} {path.name} seed={seed} probsat {record['status']} {record['wall_seconds']:.3f}s")
        else:
            if not arguments.no_gate:
                wait_for_cool_package(log)
            record = solver_record(binary, arm, family, path, seed, gate)
            successes, slot_runs = record["polish_successes"] or 0, record["heuristic_slots"] * (record["runs_completed"] or 0)
            log(f"{family} {path.name} seed={seed} {arm:24s} p={successes / slot_runs if slot_runs else float('nan'):.4f} "
                f"first={record['first_solution_seconds']} elapsed={record['elapsed_seconds']}s package={record['package_celsius']}")
        append_record(arms.RECORDS, record)
    log("ARMS DONE")


if __name__ == "__main__":
    main()
