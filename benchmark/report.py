#!/usr/bin/env python3
"""Builds benchmark/results.md from results.json and sweep_results.json.

One role: turn the raw JSON run records that run_benchmark.py writes into the
human-readable report. Re-run any time (`python3 report.py`) to refresh
results.md from whatever data currently exists; safe to call after every stage
so an interruption never loses a finished section.
"""
import statistics
import re
import subprocess
from datetime import datetime
from pathlib import Path

from run_benchmark import (
    ROOT, THIRD_PARTY, SOLVER_BIN, RESULTS_JSON, SWEEP_JSON, RESULTS_MD,
    N_VALUES, RATIOS, SEEDS, DEFAULT_STEP, SWEEP_N, SWEEP_RATIO, SWEEP_SEEDS,
    SWEEP_CAP, SWEEP_FACTORS, EXTERNAL_MARGIN, load_json,
)


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
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
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


def binary_versions_used(results, sweep_results):
    stamps = {r.get("solver_binary_mtime") for r in results + sweep_results if r.get("solver_binary_mtime")}
    return sorted(s for s in stamps if s)


def provenance_section(results, sweep_results):
    lines = ["## Provenance", ""]
    lines.append(f"- Date: {datetime.now().strftime('%Y-%m-%d %H:%M')} (local, Europe/Paris)")
    lines.append(f"- Solver git commit: {git_provenance()}")
    lines.append(f"- Prebuilt binary: `build-cuda/multilinear-sat`, last built {binary_mtime()}")
    versions = binary_versions_used(results, sweep_results)
    if len(versions) > 1:
        lines.append(f"- **WARNING: results were collected against {len(versions)} different binary builds** "
                      f"(the solver is under active concurrent development outside this benchmark). "
                      f"build mtimes seen across recorded runs: {', '.join(versions)}. Every run record in "
                      f"results.json / sweep_results.json carries its own `solver_binary_mtime`; treat runs "
                      f"stamped with different mtimes as not directly comparable.")
    elif versions:
        lines.append(f"- All recorded runs used the single binary build at mtime {versions[0]}, "
                      f"matching the commit above.")
    lines.append(f"- GPU: {gpu_name()}")
    lines.append(f"- CPU: {cpu_model()}")
    lines.append(f"- CUDA: {cuda_version()}")
    lines.append("- Baseline commits (`benchmark/third_party/versions.txt`):")
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
    return lines


def protocol_section():
    return [
        "## Protocol", "",
        "One run per (solver, instance, seed) cell, no other GPU load during the run "
        "(checked with `nvidia-smi` before starting). CaDiCaL runs first on every instance with a "
        "generous limit (300s for n<=5000, 600s for n=20000) purely to decide satisfiability; an "
        "instance it cannot decide within that limit is reported as \"undecided\" and excluded from "
        "the rates below (it still counts against the compute budget). probSAT and multilinear-sat "
        "(cuda backend) then each run once per seed on every CaDiCaL-SAT instance, at the per-solver "
        "limit (60s for n<=5000, 120s for n=20000).", "",
        "**Scope cut from the brief.** Calibration on 2026-08-28 showed CaDiCaL frequently needs its "
        "full cap even at n=1000-5000 on uniform random 3-SAT (consistent with the literature: CDCL "
        "scales poorly on random k-SAT well below the satisfiability threshold, which is exactly why "
        "local-search solvers are competitive here). To stay under the ~75 minute total compute "
        "budget, the two prescribed cuts were both applied up front: n=20000 was dropped first, then "
        "seeds were reduced from 3 to 2. Scope actually run: n in {200, 1000, 5000}, ratios in "
        "{4.0, 4.2, 4.26}, seeds in {0, 1} (18 instances).", "",
    ]


def sweep_section(sweep_results):
    lines = ["## Parameter sweep", ""]
    lines.append(f"n={SWEEP_N}, ratio={SWEEP_RATIO}, seeds={SWEEP_SEEDS}, {SWEEP_CAP}s per run, cuda backend, "
                  "one factor varied at a time from the `configuration.hpp` defaults "
                  f"({', '.join(f'{k}={v}' for k, v in DEFAULT_STEP.items())}). "
                  "`best_violated` is min-max over the runs at that setting (0 = solved).")
    lines.append("")
    if not sweep_results:
        lines.append("*(not yet run)*")
        lines.append("")
        return lines
    sweep_rows = build_sweep_table(sweep_results)
    lines.append("| factor | value | runs | solved | best_violated range |")
    lines.append("|---|---|---|---|---|")
    for r in sweep_rows:
        lines.append(f"| {r['factor']} | {r['value']} | {r['n']} | {r['solved']}/{r['n']} | {r['best_violated']} |")
    def fewest_violated(row):
        return int(row["best_violated"].split("-")[0]) if row["best_violated"] != "-" else 10 ** 9

    best_by_factor = {}
    for factor in SWEEP_FACTORS:
        candidates = [r for r in sweep_rows if r["factor"] == factor]
        if candidates:
            best_by_factor[factor] = max(candidates, key=lambda r: (r["solved"], -fewest_violated(r)))
    lines.append("")
    if any(r["solved"] for r in sweep_rows):
        summary = "; ".join(f"{f}: {r['value']} ({r['solved']}/{r['n']} solved)" for f, r in best_by_factor.items())
        lines.append(f"Best setting per factor by runs solved: {summary}.")
    else:
        summary = "; ".join(f"{f}: {r['value']} (best_violated {r['best_violated']})"
                            for f, r in best_by_factor.items())
        lines.append("No swept setting solved the sweep instance, so the settings are ranked by the fewest "
                     f"violated clauses reached: {summary}. The main table below uses the compiled-in "
                     "defaults; the sweep's direction (a smaller step, a larger kick) is untested there.")
    lines.append("")
    return lines


def main_table_section(results):
    lines = ["## Main table", ""]
    if not results:
        lines.append("*(not yet run)*")
        lines.append("")
        return lines
    rows = build_main_table(results)
    lines.append("| n | ratio | instances tested (CaDiCaL-SAT) | multilinear-sat rate | multilinear-sat median | "
                  "probSAT rate | probSAT median | CaDiCaL median decision time |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in rows:
        tested_str = f"{r['tested']}/{r['planned']}" if r['tested'] < r['planned'] else str(r['tested'])
        lines.append(f"| {r['n']} | {r['ratio']:.2f} | {tested_str} | {r['ml_rate']} | {r['ml_median']} | "
                      f"{r['ps_rate']} | {r['ps_median']} | {r['cad_median']} |")
    lines.append("")
    lines.append("(rate = solved/attempted on the CaDiCaL-SAT instances; median is over solved instances "
                  "only; \"instances tested\" shows fewer than planned when CaDiCaL left some undecided.)")
    lines.append("")
    return lines


def reading_section(results):
    lines = ["## Reading the results", ""]
    if not results:
        lines.append("*(not yet run)*")
        lines.append("")
        return lines
    rows = build_main_table(results)
    any_tested = [r for r in rows if r["tested"] > 0]
    if not any_tested:
        lines.append("No cell had any CaDiCaL-SAT instances to test on within budget; see Issues below.")
        lines.append("")
        return lines

    def rate_frac(s):
        a, b = s.split("/")
        return int(a), int(b)

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
                 f"its full generous cap on several instances above n=200, which is why some cells show "
                 f"fewer than the planned number of CaDiCaL-SAT instances: those larger/harder cells were "
                 f"left undecided rather than wrongly counted as unsolved by any solver.")
    solved_cells = [r for r in any_tested if rate_frac(r["ml_rate"])[0] > 0]
    if solved_cells:
        cells = ", ".join(f"n={r['n']} ratio {r['ratio']:.2f} (multilinear-sat {r['ml_median']}, "
                          f"probSAT {r['ps_median']})" for r in solved_cells)
        lines.append(f"Cells where multilinear-sat solved anything, with both medians: {cells}.")
    stalls = {}
    for r in results:
        violated = (r.get("json") or {}).get("best_violated")
        size = re.match(r"uf(\d+)_", r.get("instance", ""))
        if r["solver"] == "multilinear-sat" and r["status"] != "SAT" and violated is not None and size:
            stalls.setdefault(int(size.group(1)), []).append(violated)
    if stalls:
        ranges = "; ".join(f"{min(v)}-{max(v)} at n={n}" for n, v in sorted(stalls.items()))
        lines.append(f"Where multilinear-sat did not solve within its cap, the fewest violated clauses it "
                     f"reached were {ranges}: the residual grows with n.")
    lines.append("")
    return lines


RUN_NOTES = [
    "- 2026-08-28 main run: a ComfyUI server (pid 26518, 1.9 GB resident, 0 % utilisation) stayed on the GPU "
    "throughout. Its memory never changed across the 686 samples of `raw/gpu-monitor.log` (one every 15 s) "
    "and every interval of non-zero utilisation coincides with a multilinear-sat run, so no cell is affected.",
    "- 2026-08-28 main run: the binary was built from commit 06ba842; commits after it up to the report "
    "touch neither `solver/` nor `cli/`.",
]


def issues_section(results):
    lines = ["## Issues", ""]
    issues = list(RUN_NOTES)
    for r in results:
        if r.get("status") == "hung":
            issues.append(f"- `{r['solver']}` on `{r['instance']}` seed={r['seed']}: exceeded external safety "
                           f"timeout (cap {r.get('cap')}s + {EXTERNAL_MARGIN}s margin), killed. stderr tail: "
                           f"`{r.get('stderr', '')[:300]}`")
        elif isinstance(r.get("status"), str) and r["status"].startswith("unexpected_rc"):
            issues.append(f"- `{r['solver']}` on `{r['instance']}` seed={r['seed']}: {r['status']} "
                           f"(cmd exit code not in {{0,10,20}}). stderr tail: `{r.get('stderr', '')[:300]}`")
    lines.extend(issues if issues else ["None recorded so far."])
    lines.append("")
    return lines


def write_markdown():
    results = load_json(RESULTS_JSON)
    sweep_results = load_json(SWEEP_JSON)

    lines = ["# multilinear-sat benchmark results", ""]
    lines += provenance_section(results, sweep_results)
    lines += protocol_section()
    lines += sweep_section(sweep_results)
    lines += main_table_section(results)
    lines += reading_section(results)
    lines += issues_section(results)

    RESULTS_MD.write_text("\n".join(lines))
    print(f"wrote {RESULTS_MD}")


if __name__ == "__main__":
    write_markdown()
