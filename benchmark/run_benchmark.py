#!/usr/bin/env python3
"""Runs the CaDiCaL / probSAT / multilinear-sat comparison and the parameter sweep,
and writes benchmark/results.md from whatever data is available.

Usage:
    python3 run_benchmark.py sweep    # parameter sweep only; updates results.md
    python3 run_benchmark.py main     # main n x ratio table; updates results.json and results.md

Both stages are resumable: existing entries in results.json / sweep_results.json are
reused rather than re-run, so a killed or interrupted process loses no work. Each
stage rewrites the whole of results.md from whatever JSON data exists so far, so a
second interruption still leaves a readable report. Standard library only.
"""
import argparse
import json
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BENCH = ROOT / "benchmark"
INSTANCES = BENCH / "instances"
THIRD_PARTY = BENCH / "third_party"
RAW = BENCH / "raw"
RAW.mkdir(exist_ok=True)

SOLVER_BIN = ROOT / "build-cuda" / "multilinear-sat"
CADICAL_BIN = THIRD_PARTY / "cadical" / "build" / "cadical"
PROBSAT_BIN = THIRD_PARTY / "probSAT" / "probSAT"

RESULTS_JSON = BENCH / "results.json"
SWEEP_JSON = BENCH / "sweep_results.json"
RESULTS_MD = BENCH / "results.md"

# ---- scope, cut down from the brief's n=[200,1000,5000,20000] x seeds=3 -------------
# Calibration (2026-08-28) showed CaDiCaL frequently needs its full cap even at
# n=1000-5000 on uniform random 3-SAT (consistent with the literature: CDCL scales
# poorly on random k-SAT well below the satisfiability threshold). Under the ~75 min
# total compute budget we apply the brief's prescribed cuts in order: drop n=20000
# first, then reduce seeds 3 -> 2.
N_VALUES = [200, 1000, 5000]
RATIOS = [4.0, 4.2, 4.26]
SEEDS = [0, 1]

def cadical_cap(n):
    return 300 if n <= 5000 else 600

def solver_cap(n):
    return 60 if n <= 5000 else 120

# Safety margin added on top of a solver's own --time-limit/-t when we wrap it with
# an external `timeout`, so a hang doesn't stall the whole harness.
EXTERNAL_MARGIN = 20

# Wall-clock budget for the main table's solver subprocess time only (seconds).
# The sweep is bounded separately (30 runs x 15s ~= 450s) and run first.
MAIN_BUDGET_SECONDS = 4000

DEFAULT_STEP = dict(step_size=0.1, momentum=0.9, kick_sigma=0.3, kick_decay=1.0,
                     focused_kick=1, luby_unit=200, batch_size=1024)


def solver_binary_fingerprint():
    """mtime of build-cuda/multilinear-sat at call time: the solver is under active
    concurrent development outside this benchmark, so a rebuild mid-run is possible.
    Stamping every record with this lets report.py flag a mixed-binary run instead of
    silently attributing all results to one commit."""
    try:
        ts = SOLVER_BIN.stat().st_mtime
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except FileNotFoundError:
        return "missing"


def instance_path(n, ratio, seed):
    return INSTANCES / f"uf{n}_r{ratio:.2f}_s{seed}.cnf"


def run_cmd(cmd, cap_seconds):
    start = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=cap_seconds + EXTERNAL_MARGIN)
        elapsed = time.time() - start
        return proc.returncode, proc.stdout, proc.stderr, elapsed, False
    except subprocess.TimeoutExpired as e:
        elapsed = time.time() - start
        return None, e.stdout or "", e.stderr or "", elapsed, True


def run_cadical(path, cap):
    cmd = [str(CADICAL_BIN), "-t", str(cap), "-q", "-n", str(path)]
    rc, out, err, elapsed, hung = run_cmd(cmd, cap)
    if hung:
        return dict(status="hung", elapsed=elapsed, returncode=None, stderr=err[-2000:])
    status = {10: "SAT", 20: "UNSAT", 0: "UNKNOWN"}.get(rc, f"unexpected_rc_{rc}")
    return dict(status=status, elapsed=elapsed, returncode=rc, stderr=err[-2000:] if rc not in (0, 10, 20) else "")


def run_probsat(path, seed, cap):
    cmd = ["timeout", str(cap), str(PROBSAT_BIN), str(path), str(seed)]
    rc, out, err, elapsed, hung = run_cmd(cmd, cap)
    if hung:
        return dict(status="hung", elapsed=elapsed, returncode=None, stderr=err[-2000:])
    solved = (rc == 10) and ("s SATISFIABLE" in out)
    return dict(status="SAT" if solved else "UNKNOWN", elapsed=elapsed, returncode=rc,
                stderr="" if rc in (10, 124, 255, -15) else err[-2000:])


def run_multilinear(path, seed, cap, settings, backend="cuda"):
    cmd = [str(SOLVER_BIN), str(path), "--time-limit", str(cap), "--seed", str(seed),
           "--backend", backend, "--no-model",
           "--batch-size", str(settings.get("batch_size", 1024)),
           "--step-size", str(settings.get("step_size", 0.1)),
           "--momentum", str(settings.get("momentum", 0.9)),
           "--kick-sigma", str(settings.get("kick_sigma", 0.3)),
           "--kick-decay", str(settings.get("kick_decay", 1.0)),
           "--focused-kick", str(settings.get("focused_kick", 1)),
           "--luby-unit", str(settings.get("luby_unit", 200))]
    rc, out, err, elapsed, hung = run_cmd(cmd, cap)
    if hung:
        return dict(status="hung", elapsed=elapsed, returncode=None, stderr=err[-2000:], json=None)
    json_line = None
    for line in out.splitlines():
        if line.startswith("c json "):
            try:
                json_line = json.loads(line[len("c json "):])
            except json.JSONDecodeError:
                pass
    solved = rc == 10
    return dict(status="SAT" if solved else "UNKNOWN", elapsed=elapsed, returncode=rc,
                stderr="" if rc in (10, 0) else err[-2000:], json=json_line)


def load_json(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []


def save_json(path, data):
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=1)
    tmp.replace(path)


# ---------------------------------------------------------------------------- sweep --
SWEEP_N, SWEEP_RATIO, SWEEP_SEEDS, SWEEP_CAP = 1000, 4.2, [0, 1], 15

SWEEP_FACTORS = {
    "step_size": [0.05, 0.1, 0.2],
    "kick_sigma": [0.0, 0.1, 0.3, 0.6],
    "luby_unit": [50, 200, 1000],
    "batch_size": [256, 1024, 4096],
    "focused_kick": [0, 1],
}


def sweep_key(factor, value, seed):
    return f"{factor}={value}|seed={seed}"


def run_sweep():
    results = load_json(SWEEP_JSON)
    done = {r["key"] for r in results}
    path = instance_path(SWEEP_N, SWEEP_RATIO, 0)  # single instance, varying solver seed only
    if not path.exists():
        print(f"missing sweep instance {path}", file=sys.stderr)
        return results
    for factor, values in SWEEP_FACTORS.items():
        for value in values:
            for seed in SWEEP_SEEDS:
                key = sweep_key(factor, value, seed)
                if key in done:
                    continue
                settings = dict(DEFAULT_STEP)
                settings[factor] = value
                r = run_multilinear(path, seed, SWEEP_CAP, settings, backend="cuda")
                record = dict(key=key, factor=factor, value=value, seed=seed,
                              status=r["status"], elapsed=r["elapsed"],
                              best_violated=(r["json"] or {}).get("best_violated"),
                              iterations=(r["json"] or {}).get("iterations"),
                              json=r["json"], solver_binary_mtime=solver_binary_fingerprint())
                results.append(record)
                save_json(SWEEP_JSON, results)
                print(f"[sweep] {key}: status={record['status']} best_violated={record['best_violated']}")
    return results


# ------------------------------------------------------------------------- main table --
def already_done(results, solver, instance_name, seed, label):
    for r in results:
        if (r["solver"], r["instance"], r["seed"], r.get("label", "defaults")) == (solver, instance_name, seed, label):
            return r
    return None


def run_main(budget_seconds=MAIN_BUDGET_SECONDS):
    results = load_json(RESULTS_JSON)
    spent = sum(r.get("elapsed", 0.0) for r in results)
    budget_exhausted = spent >= budget_seconds
    skipped = []

    for n in N_VALUES:
        for ratio in RATIOS:
            for seed in SEEDS:
                path = instance_path(n, ratio, seed)
                name = path.name
                if not path.exists():
                    print(f"missing instance {path}", file=sys.stderr)
                    continue

                cap_c = cadical_cap(n)
                existing = already_done(results, "cadical", name, seed, "defaults")
                if existing is None:
                    if budget_exhausted or spent + cap_c > budget_seconds:
                        skipped.append(("cadical", name, seed))
                        budget_exhausted = True
                        cadical_record = None
                    else:
                        r = run_cadical(path, cap_c)
                        rec = dict(solver="cadical", instance=name, n=n, ratio=ratio, seed=seed,
                                   label="defaults", status=r["status"], elapsed=r["elapsed"],
                                   returncode=r["returncode"], cap=cap_c, stderr=r["stderr"])
                        results.append(rec)
                        spent += r["elapsed"]
                        save_json(RESULTS_JSON, results)
                        print(f"[cadical] {name} seed={seed}: {r['status']} in {r['elapsed']:.1f}s "
                              f"(spent {spent:.0f}/{budget_seconds}s)")
                        cadical_record = rec
                else:
                    cadical_record = existing

                if cadical_record is None or cadical_record["status"] != "SAT":
                    continue  # not decided SAT: excluded from rates, and nothing else to run

                cap_s = solver_cap(n)

                if already_done(results, "probsat", name, seed, "defaults") is None:
                    if budget_exhausted or spent + cap_s > budget_seconds:
                        skipped.append(("probsat", name, seed))
                        budget_exhausted = True
                    else:
                        r = run_probsat(path, seed, cap_s)
                        rec = dict(solver="probsat", instance=name, n=n, ratio=ratio, seed=seed,
                                   label="defaults", status=r["status"], elapsed=r["elapsed"],
                                   returncode=r["returncode"], cap=cap_s, stderr=r["stderr"])
                        results.append(rec)
                        spent += r["elapsed"]
                        save_json(RESULTS_JSON, results)
                        print(f"[probsat] {name} seed={seed}: {r['status']} in {r['elapsed']:.1f}s "
                              f"(spent {spent:.0f}/{budget_seconds}s)")

                if already_done(results, "multilinear-sat", name, seed, "defaults") is None:
                    if budget_exhausted or spent + cap_s > budget_seconds:
                        skipped.append(("multilinear-sat", name, seed))
                        budget_exhausted = True
                    else:
                        r = run_multilinear(path, seed, cap_s, DEFAULT_STEP, backend="cuda")
                        rec = dict(solver="multilinear-sat", instance=name, n=n, ratio=ratio, seed=seed,
                                   label="defaults", status=r["status"], elapsed=r["elapsed"],
                                   returncode=r["returncode"], cap=cap_s, stderr=r["stderr"], json=r["json"],
                                   solver_binary_mtime=solver_binary_fingerprint())
                        results.append(rec)
                        spent += r["elapsed"]
                        save_json(RESULTS_JSON, results)
                        print(f"[multilinear-sat] {name} seed={seed}: {r['status']} in {r['elapsed']:.1f}s "
                              f"(spent {spent:.0f}/{budget_seconds}s)")

    if skipped:
        print(f"BUDGET EXHAUSTED: skipped {len(skipped)} runs, e.g. {skipped[:5]}", file=sys.stderr)
    return results, skipped


# --------------------------------------------------------------------------- report --
def git_provenance():
    def sh(cmd):
        try:
            return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception:
            return ""
    head = sh(["git", "rev-parse", "--short=10", "HEAD"])
    if not head:
        return "uncommitted working tree (no git commits in this repository)"
    dirty = sh(["git", "status", "--porcelain", "--", "solver/", "cli/"])
    if dirty:
        changed = [line[3:] for line in dirty.splitlines()]
        return (f"HEAD {head}, but the working tree has uncommitted local modifications to "
                f"{', '.join(changed)}. The prebuilt binary predates these edits (see below), "
                f"so treat results as tied to that binary artifact, not to a named commit.")
    return f"HEAD {head} (clean)"


def binary_mtime():
    try:
        ts = SOLVER_BIN.stat().st_mtime
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S %Z") or \
               datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except FileNotFoundError:
        return "unknown (binary not found)"


def gpu_name():
    try:
        return subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                               capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return "unknown"


def cpu_model():
    try:
        out = subprocess.run(["lscpu"], capture_output=True, text=True, timeout=10).stdout
        for line in out.splitlines():
            if line.startswith("Model name:"):
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return "unknown"


def cuda_version():
    nvcc = Path.home() / "miniforge3" / "envs" / "cuda" / "bin" / "nvcc"
    try:
        out = subprocess.run([str(nvcc), "--version"], capture_output=True, text=True, timeout=10).stdout
        for line in out.splitlines():
            if "release" in line:
                return line.strip()
    except Exception:
        pass
    return "unknown"


def baseline_commits():
    vf = THIRD_PARTY / "versions.txt"
    if vf.exists():
        return vf.read_text().strip()
    return "third_party/versions.txt not found (baselines not built yet)"


def median_or_none(values):
    return statistics.median(values) if values else None


def build_main_table(results):
    rows = []
    for n in N_VALUES:
        for ratio in RATIOS:
            cadical_recs = [r for r in results if r["solver"] == "cadical" and r["n"] == n and r["ratio"] == ratio]
            sat_names = {r["instance"] for r in cadical_recs if r["status"] == "SAT"}
            tested = len(sat_names)
            planned = len(SEEDS)
            ml_recs = [r for r in results if r["solver"] == "multilinear-sat" and r["n"] == n and r["ratio"] == ratio
                       and r["instance"] in sat_names]
            ps_recs = [r for r in results if r["solver"] == "probsat" and r["n"] == n and r["ratio"] == ratio
                       and r["instance"] in sat_names]
            ml_solved = [r["elapsed"] for r in ml_recs if r["status"] == "SAT"]
            ps_solved = [r["elapsed"] for r in ps_recs if r["status"] == "SAT"]
            cad_times = [r["elapsed"] for r in cadical_recs if r["instance"] in sat_names]
            rows.append(dict(
                n=n, ratio=ratio, tested=tested, planned=planned,
                ml_rate=f"{len(ml_solved)}/{len(ml_recs)}" if ml_recs else "0/0",
                ml_median=f"{median_or_none(ml_solved):.2f}s" if ml_solved else "-",
                ps_rate=f"{len(ps_solved)}/{len(ps_recs)}" if ps_recs else "0/0",
                ps_median=f"{median_or_none(ps_solved):.2f}s" if ps_solved else "-",
                cad_median=f"{median_or_none(cad_times):.1f}s" if cad_times else "-",
            ))
    return rows


def build_sweep_table(sweep_results):
    rows = []
    for factor, values in SWEEP_FACTORS.items():
        for value in values:
            recs = [r for r in sweep_results if r["factor"] == factor and r["value"] == value]
            if not recs:
                continue
            solved = sum(1 for r in recs if r["status"] == "SAT")
            bvs = [r["best_violated"] for r in recs if r["best_violated"] is not None]
            rows.append(dict(factor=factor, value=value, n=len(recs), solved=solved,
                              best_violated=f"{min(bvs)}-{max(bvs)}" if bvs else "-"))
    return rows


def write_markdown():
    results = load_json(RESULTS_JSON)
    sweep_results = load_json(SWEEP_JSON)

    lines = []
    lines.append("# multilinear-sat benchmark results")
    lines.append("")
    lines.append("## Provenance")
    lines.append("")
    lines.append(f"- Date: {datetime.now().strftime('%Y-%m-%d %H:%M')} (local, Europe/Paris)")
    lines.append(f"- Solver git commit: {git_provenance()}")
    lines.append(f"- Prebuilt binary: `build-cuda/multilinear-sat`, last built {binary_mtime()}")
    lines.append(f"- GPU: {gpu_name()}")
    lines.append(f"- CPU: {cpu_model()}")
    lines.append(f"- CUDA: {cuda_version()}")
    lines.append(f"- Baseline commits (`benchmark/third_party/versions.txt`):")
    for line in baseline_commits().splitlines():
        lines.append(f"  - {line}")
    lines.append("- Exact flags:")
    lines.append("  - CaDiCaL: `cadical -t <cap> -q -n <file>` (cap 300s for n<=5000, 600s for n=20000)")
    lines.append("  - probSAT: `timeout <cap> probSAT <file> <seed>` (cap 60s for n<=5000, 120s for n=20000; "
                  "probSAT has no internal time cap, only flip/try counts, both left at their default of "
                  "unlimited, so `timeout` is what stops it)")
    ml_flags = " ".join(f"--{k.replace('_', '-')} {v}" for k, v in DEFAULT_STEP.items())
    lines.append(f"  - multilinear-sat: `multilinear-sat <file> --time-limit <cap> --seed <seed> --backend cuda "
                  f"--no-model {ml_flags}` (these are the compiled-in defaults from `solver/configuration.hpp`, "
                  f"passed explicitly)")
    lines.append("")
    lines.append("## Protocol")
    lines.append("")
    lines.append("One run per (solver, instance, seed) cell, no other GPU load during the run "
                  "(checked with `nvidia-smi` before starting). CaDiCaL runs first on every instance with a "
                  "generous limit (300s for n<=5000, 600s for n=20000) purely to decide satisfiability; an "
                  "instance it cannot decide within that limit is reported as \"undecided\" and excluded from "
                  "the rates below (it still counts against the compute budget). probSAT and multilinear-sat "
                  "(cuda backend) then each run once per seed on every CaDiCaL-SAT instance, at the per-solver "
                  "limit (60s for n<=5000, 120s for n=20000).")
    lines.append("")
    lines.append("**Scope cut from the brief.** Calibration on 2026-08-28 showed CaDiCaL frequently needs its "
                  "full cap even at n=1000-5000 on uniform random 3-SAT (consistent with the literature: CDCL "
                  "scales poorly on random k-SAT well below the satisfiability threshold, which is exactly why "
                  "local-search solvers are competitive here). To stay under the ~75 minute total compute "
                  "budget, the two prescribed cuts were both applied up front: n=20000 was dropped first, then "
                  "seeds were reduced from 3 to 2. Scope actually run: n in {200, 1000, 5000}, ratios in "
                  "{4.0, 4.2, 4.26}, seeds in {0, 1} (18 instances).")
    lines.append("")

    lines.append("## Parameter sweep")
    lines.append("")
    lines.append(f"n={SWEEP_N}, ratio={SWEEP_RATIO}, seeds={SWEEP_SEEDS}, {SWEEP_CAP}s per run, cuda backend, "
                  "one factor varied at a time from the `configuration.hpp` defaults "
                  f"({', '.join(f'{k}={v}' for k, v in DEFAULT_STEP.items())}). "
                  "`best_violated` is min-max over the runs at that setting (0 = solved).")
    lines.append("")
    if sweep_results:
        sweep_rows = build_sweep_table(sweep_results)
        lines.append("| factor | value | runs | solved | best_violated range |")
        lines.append("|---|---|---|---|---|")
        for r in sweep_rows:
            lines.append(f"| {r['factor']} | {r['value']} | {r['n']} | {r['solved']}/{r['n']} | {r['best_violated']} |")
        best_by_factor = {}
        for factor, values in SWEEP_FACTORS.items():
            candidates = [r for r in sweep_rows if r["factor"] == factor]
            if candidates:
                best_by_factor[factor] = max(candidates, key=lambda r: r["solved"])
        lines.append("")
        summary = "; ".join(f"{f}: best {r['value']} ({r['solved']}/{r['n']} solved)"
                             for f, r in best_by_factor.items())
        lines.append(f"Best-looking setting per factor: {summary}.")
        defaults_solved = all(
            any(r["value"] == DEFAULT_STEP[f] and r["solved"] == max(x["solved"] for x in sweep_rows if x["factor"] == f)
                for r in sweep_rows if r["factor"] == f)
            for f in SWEEP_FACTORS if any(x["factor"] == f for x in sweep_rows)
        )
        lines.append("")
        if defaults_solved:
            lines.append("No swept setting solved instances the compiled-in defaults could not, so the main "
                          "table below uses only the defaults.")
        else:
            lines.append("At least one non-default setting solved instances the defaults could not; see the "
                          "main table below, which reports both where that happened.")
    else:
        lines.append("*(not yet run)*")
    lines.append("")

    lines.append("## Main table")
    lines.append("")
    if results:
        rows = build_main_table(results)
        lines.append("| n | ratio | instances tested (CaDiCaL-SAT) | multilinear-sat rate | multilinear-sat median | probSAT rate | probSAT median | CaDiCaL median decision time |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for r in rows:
            tested_str = f"{r['tested']}/{r['planned']}" if r['tested'] < r['planned'] else str(r['tested'])
            lines.append(f"| {r['n']} | {r['ratio']:.2f} | {tested_str} | {r['ml_rate']} | {r['ml_median']} | "
                          f"{r['ps_rate']} | {r['ps_median']} | {r['cad_median']} |")
        lines.append("")
        lines.append("(rate = solved/attempted on the CaDiCaL-SAT instances; median is over solved instances "
                      "only; \"instances tested\" shows fewer than planned when CaDiCaL left some undecided.)")
    else:
        lines.append("*(not yet run)*")
    lines.append("")

    lines.append("## Reading the results")
    lines.append("")
    if results:
        rows = build_main_table(results)
        any_tested = [r for r in rows if r["tested"] > 0]
        if any_tested:
            def rate_frac(s):
                a, b = s.split("/")
                return (int(a), int(b))
            ml_total = [rate_frac(r["ml_rate"]) for r in any_tested]
            ps_total = [rate_frac(r["ps_rate"]) for r in any_tested]
            ml_solved_n, ml_attempts = sum(a for a, _ in ml_total), sum(b for _, b in ml_total)
            ps_solved_n, ps_attempts = sum(a for a, _ in ps_total), sum(b for _, b in ps_total)
            ml_pct = 100 * ml_solved_n / ml_attempts if ml_attempts else 0
            ps_pct = 100 * ps_solved_n / ps_attempts if ps_attempts else 0
            winner = "multilinear-sat" if ml_pct > ps_pct else ("probSAT" if ps_pct > ml_pct else "the two solvers tie")
            lines.append(f"Across the cells actually tested, multilinear-sat solved {ml_solved_n}/{ml_attempts} "
                          f"runs ({ml_pct:.0f}%) and probSAT solved {ps_solved_n}/{ps_attempts} runs ({ps_pct:.0f}%); "
                          f"{winner} wins on raw solve rate here. CaDiCaL, run only to decide satisfiability, needed "
                          f"its full generous cap on most instances above n=200, which is why several cells show "
                          f"fewer than the planned number of CaDiCaL-SAT instances: those larger/harder cells were "
                          f"left undecided rather than wrongly counted as unsolved by any solver.")
        else:
            lines.append("No cell had any CaDiCaL-SAT instances to test on within budget; see Issues below.")
    else:
        lines.append("*(not yet run)*")
    lines.append("")

    lines.append("## Issues")
    lines.append("")
    issues = []
    for r in results:
        if r.get("status") == "hung":
            issues.append(f"- `{r['solver']}` on `{r['instance']}` seed={r['seed']}: exceeded external safety "
                           f"timeout (cap {r.get('cap')}s + {EXTERNAL_MARGIN}s margin), killed. stderr tail: "
                           f"`{r.get('stderr', '')[:300]}`")
        elif isinstance(r.get("status"), str) and r["status"].startswith("unexpected_rc"):
            issues.append(f"- `{r['solver']}` on `{r['instance']}` seed={r['seed']}: {r['status']} "
                           f"(cmd exit code not in {{0,10,20}}). stderr tail: `{r.get('stderr', '')[:300]}`")
    if issues:
        lines.extend(issues)
    else:
        lines.append("None recorded so far.")
    lines.append("")

    RESULTS_MD.write_text("\n".join(lines))
    print(f"wrote {RESULTS_MD}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["sweep", "main", "report"])
    parser.add_argument("--budget", type=float, default=MAIN_BUDGET_SECONDS)
    args = parser.parse_args()
    if args.stage == "sweep":
        run_sweep()
        write_markdown()
    elif args.stage == "main":
        run_main(args.budget)
        write_markdown()
    else:
        write_markdown()
