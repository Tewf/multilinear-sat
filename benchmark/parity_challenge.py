#!/usr/bin/env python3
"""Parity constraints natively: the walk on the ten MM-Challenge-1 XNFs and on the tensor-rank
toolkit's own matmul_3x3x3 at rank 23, from all-false starts (xnfSAT's default, which its
paper found better than random) and from the ascent, five seeds under a stated cap; and the
matmul_2x2x2 at 7 check, the toolkit's decide-rank-by-sat --solver route re-multiplying the
model. The challenge and toolkit paths are arguments and never recorded: the records name
instances only. Records to parity_challenge.jsonl, the table to parity_challenge.md."""
import argparse
import os
import subprocess
from datetime import datetime
from pathlib import Path

from walk_runs import BENCHMARK, append_record, frozen_binary, load_records, provenance, run_solver

ARMS = {"all_false": ["--seed-kind", "all-false"], "ascent200": ["--seed-kind", "ascent", "--seed-steps", 200]}


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--build", default="build-cuda")
    parser.add_argument("--backend", default="cuda")
    parser.add_argument("--challenges", type=Path, required=True, help="directory of the MM-23-*.xnf files")
    parser.add_argument("--toolkit", type=Path, required=True, help="the toolkit's decide-rank-by-sat binary")
    parser.add_argument("--fixtures", type=Path, required=True, help="the toolkit's fixtures directory (matmul_*.tensor)")
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2, 3, 4])
    parser.add_argument("--cap", type=float, default=30.0)
    parser.add_argument("--slots", type=int, default=1024)
    parser.add_argument("--polish-flips-per-variable", type=int, default=50)
    parser.add_argument("--arms", nargs="*", default=list(ARMS), choices=list(ARMS))
    parser.add_argument("--skip-verification", action="store_true")
    parser.add_argument("--verification-only", action="store_true")
    parser.add_argument("--adapter-flags", default="--backend cuda --seed-kind all-false --polish-flips 32200 --batch-size 4096 --time-limit 120",
                        help="MULTILINEAR_SAT_FLAGS for the as-xnfsat adapter in the verification")
    parser.add_argument("--output", type=Path, default=BENCHMARK / "parity_challenge.jsonl")
    return parser.parse_args()


def emit_xnf(arguments, tensor, rank, target):
    subprocess.run([str(arguments.toolkit), str(arguments.fixtures / tensor), "--target", str(rank), "--emit-xnf", str(target)],
                   check=True, capture_output=True, text=True)
    return target


def header(path):
    for line in open(path):
        if line.startswith("p "):
            return int(line.split()[2]), int(line.split()[3])
    raise ValueError(f"no header in {path}")


def walk_record(binary, arguments, name, path, arm, seed):
    variables, rows = header(path)
    flags = ["--backend", arguments.backend, "--batch-size", arguments.slots, "--walk-rule", "skc",
             "--polish-flips", arguments.polish_flips_per_variable * variables, "--seed", seed] + ARMS[arm]
    result = run_solver(binary, path, flags, arguments.cap)
    stats = result["json"] or {}
    return dict(kind="run", instance=name, variables=variables, rows=rows, arm=arm, seed=seed, status=result["status"],
                seconds=stats.get("elapsed_seconds"), wall_seconds=result["wall_seconds"], runs=stats.get("runs"), flips=stats.get("flips"),
                best_violated=stats.get("best_violated"), timestamp=datetime.now().isoformat(timespec="seconds"))


def verification_records(binary, arguments):
    """decide-rank-by-sat matmul_2x2x2 --target 7 --solver <path>, twice: with the binary itself,
    which the toolkit names multilinear-sat and hands its 3-cut CNF expansion under the 0.1
    defaults (the ascent alone, one CPU thread); and with the as-xnfsat adapter, which the
    toolkit names xnfsat and hands the XNF, the walk from all-false starts. Either way the
    toolkit reads the model back and re-multiplies it."""
    records = []
    for label, solver in (("3-cut CNF, the ascent alone (the toolkit's multilinear-sat line)", binary),
                          ("XNF through the as-xnfsat adapter, the walk from all false", BENCHMARK / "as-xnfsat" / "xnfsat")):
        command = [str(arguments.toolkit), str(arguments.fixtures / "matmul_2x2x2.tensor"), "--target", "7", "--solver", str(solver),
                   "--timeout", "130", "--seed", "0"]
        environment = dict(os.environ, MULTILINEAR_SAT_BINARY=str(binary), MULTILINEAR_SAT_FLAGS=arguments.adapter_flags)
        completed = subprocess.run(command, capture_output=True, text=True, timeout=400, env=environment)
        output = "\n".join(line for line in (completed.stdout + completed.stderr).splitlines() if "fixtures" not in line)[-2000:]
        records.append(dict(kind="verification", instance=f"matmul_2x2x2 at 7 through decide-rank-by-sat --solver: {label}",
                            adapter_flags=arguments.adapter_flags if "adapter" in label else "the toolkit's own line, 0.1 defaults, one thread",
                            exit_code=completed.returncode, output=output))
    return records


def write_table(records, path):
    runs = [r for r in records if r["kind"] == "run"]
    stamp = next((r for r in records if r["kind"] == "provenance"), {})
    arguments = stamp.get("arguments", {})
    lines = ["# Parity constraints natively: MM-Challenge-1 and matmul_3x3x3 at 23", "",
             f"- First record {stamp.get('timestamp')}; commit {stamp.get('commit')}; binary sha256 {stamp.get('binary_sha256')}; backend "
             f"{arguments.get('backend')}; {arguments.get('slots')} slots; {arguments.get('polish_flips_per_variable')} n SKC flips per run on the "
             f"Luby schedule; cap {arguments.get('cap')} s per (instance, arm, seed); seeds {arguments.get('seeds')}.",
             "- Today's numbers to beat (toolkit branch las-vegas-sat, one seed, 5 s cap): xnfsat 3 of 10 (4-4-4-4-1 in 0.03 s, "
             "2-2-2-2-A in 2.39 s, 2-2-2-2-D in 0.83 s), kissat none; on matmul_3x3x3 at 23 xnfsat 0 of 5 in 60 s.", "",
             "| instance | arm | solved / seeds | seconds of the solved | best violated of the rest |", "|---|---|---|---|---|"]
    for name in dict.fromkeys(r["instance"] for r in runs):
        for arm in ARMS:
            group = [r for r in runs if r["instance"] == name and r["arm"] == arm]
            if not group:
                continue
            solved = sorted(r["seconds"] for r in group if r["status"] == "SATISFIABLE" and r["seconds"] is not None)
            rest = [r["best_violated"] for r in group if r["status"] != "SATISFIABLE" and r["best_violated"] is not None]
            lines.append(f"| {name} | {arm} | {len(solved)}/{len(group)} | {', '.join(f'{s:.2f}' for s in solved) or '-'} | "
                         f"{min(rest)}-{max(rest) if rest else ''}".rstrip("-") + (" |" if rest else "- |"))
    for r in records:
        if r["kind"] == "verification":
            lines += ["", f"Verification, {r['instance']} ({r.get('adapter_flags', '')}): exit code {r['exit_code']}.", "", "```",
                      r["output"].strip(), "```"]
    lines += ["", "Every run is in parity_challenge.jsonl with its seed, commit and binary hash; the instance files are not committed."]
    path.write_text("\n".join(lines) + "\n")
    print(f"wrote {path}")


def main():
    arguments = parse_arguments()
    binary = frozen_binary(arguments.build)
    stamp = provenance(binary, arguments)
    stamp["arguments"] = {k: v for k, v in stamp["arguments"].items() if k not in ("challenges", "toolkit", "fixtures")}
    append_record(arguments.output, stamp)
    done = {(r["instance"], r["arm"], r["seed"]) for r in load_records(arguments.output) if r.get("kind") == "run"}
    scratch = BENCHMARK / "raw" / "xnf"
    scratch.mkdir(parents=True, exist_ok=True)
    instances = [] if arguments.verification_only else [(p.stem, p) for p in sorted(arguments.challenges.glob("MM-23-*.xnf"))]
    if not arguments.verification_only:
        instances.append(("matmul_3x3x3 at 23 (toolkit --emit-xnf)", emit_xnf(arguments, "matmul_3x3x3.tensor", 23, scratch / "matmul_3x3x3_23.xnf")))
    for name, path in instances:
        for arm in arguments.arms:
            for seed in arguments.seeds:
                if (name, arm, seed) in done:
                    continue
                record = walk_record(binary, arguments, name, path, arm, seed)
                append_record(arguments.output, record)
                print(f"{name} {arm} seed {seed}: {record['status']} {record['seconds']}s best {record['best_violated']}", flush=True)
    if not arguments.skip_verification:
        for record in verification_records(binary, arguments):
            append_record(arguments.output, record)
            print(record["instance"], "exit", record["exit_code"])
            print(record["output"])
    write_table(load_records(arguments.output), arguments.output.with_suffix(".md"))


if __name__ == "__main__":
    main()
