#!/usr/bin/env python3
"""What every walk benchmark shares: one solver or probSAT process run and turned into a
record (the command, the c json line, wall time), the frozen copy of the binary a run is
made with, the provenance stamp (commit, binary hash, GPU), and the JSONL records.
Standard library only."""
import hashlib
import json
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = ROOT / "benchmark"
INSTANCES = BENCHMARK / "instances"
RAW = BENCHMARK / "raw"
PROBSAT_BINARY = BENCHMARK / "third_party" / "probSAT" / "probSAT"
EXTERNAL_MARGIN = 20   # seconds added to a solver's own cap before the process is killed


def git_head():
    return subprocess.run(["git", "rev-parse", "--short=10", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def frozen_binary(build="build-cuda"):
    """A copy of build/multilinear-sat named by the commit and its mtime, so a rebuild during
    a run cannot change what the records were made with."""
    source = ROOT / build / "multilinear-sat"
    stamp = datetime.fromtimestamp(source.stat().st_mtime).strftime("%Y%m%d-%H%M%S")
    target = RAW / "frozen" / f"multilinear-sat-{git_head()}-{stamp}"
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return target


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def gpu_state():
    query = ["nvidia-smi", "--query-gpu=name,memory.used,utilization.gpu", "--format=csv,noheader"]
    try:
        return subprocess.run(query, capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "nvidia-smi unavailable"


def provenance(binary, arguments):
    return dict(kind="provenance", timestamp=datetime.now().isoformat(timespec="seconds"), commit=git_head(),
                binary=str(binary), binary_sha256=sha256_of(binary), gpu=gpu_state(),
                probsat_sha256=sha256_of(PROBSAT_BINARY) if PROBSAT_BINARY.exists() else None,
                arguments={key: str(value) for key, value in vars(arguments).items()})


def run_command(command, cap_seconds, environment=None):
    start = time.perf_counter()
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=cap_seconds + EXTERNAL_MARGIN, env=environment)
        return completed.returncode, completed.stdout, completed.stderr, time.perf_counter() - start, False
    except subprocess.TimeoutExpired as expired:
        return None, expired.stdout or "", expired.stderr or "", time.perf_counter() - start, True


def run_solver(binary, path, flags, cap_seconds, environment=None):
    """The c json line of one run as a dict, with the command and the wall time beside it."""
    command = [str(binary), str(path), "--no-model", "--time-limit", str(cap_seconds)] + [str(flag) for flag in flags]
    returncode, stdout, stderr, elapsed, hung = run_command(command, cap_seconds, environment)
    json_line = next((line[len("c json "):] for line in stdout.splitlines() if line.startswith("c json ")), None)
    return dict(command=" ".join(command), returncode=returncode, wall_seconds=round(elapsed, 4), hung=hung,
                json=json.loads(json_line) if json_line else None, stderr=stderr,
                status="SATISFIABLE" if returncode == 10 else "UNKNOWN")


def run_probsat(path, seed, cap_seconds, max_flips=None):
    """probSAT's own statistics: flips, flips per second, its CPU time and whether it solved."""
    command = [str(PROBSAT_BINARY)]
    if max_flips is not None:
        command += ["--maxflips", str(max_flips), "--runs", "1"]
    command += [str(path), str(seed)]
    returncode, stdout, stderr, elapsed, hung = run_command(["timeout", str(cap_seconds)] + command, cap_seconds)
    statistics = {}
    for line in stdout.splitlines():
        for key in ("numFlips", "flips/sec", "CPU Time"):
            if line.startswith("c " + key):
                statistics[key] = float(line.split(":")[1])
    return dict(command=" ".join(command), returncode=returncode, wall_seconds=round(elapsed, 4), hung=hung,
                status="SATISFIABLE" if returncode == 10 and "s SATISFIABLE" in stdout else "UNKNOWN",
                flips=statistics.get("numFlips"), flips_per_second=statistics.get("flips/sec"), cpu_seconds=statistics.get("CPU Time"))


def satlib_instances(family, count):
    """The first `count` files of a SATLIB family in name order, the order the Python record used."""
    return sorted((INSTANCES / family).glob("*.cnf"))[:count]


def load_records(path):
    if not Path(path).exists():
        return []
    with open(path) as handle:
        return [json.loads(line) for line in handle if line.strip()]


def append_record(path, record):
    with open(path, "a") as handle:
        handle.write(json.dumps(record) + "\n")
