"""The markdown table of a seed comparison run: one row per (family, seed method) with the
per-restart success probability, the median cost of a restart and their ratio, plus the loop's
own diagnostics for the tilted seeds and the throughput note against probSAT."""
import argparse
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
METHOD_ORDER = ["uniform", "all_false", "mu", "tilted", "tilted_walk"]
PROBSAT_FLIPS_PER_SECOND = 6.26e6   # one CPU core, uuf250-01, 20 M flips, seeds 1 and 2 (6.27, 6.25), 2026-08-29


def load(path):
    with open(path) as handle:
        records = [json.loads(line) for line in handle if line.strip()]
    return [r for r in records if r.get("kind") == "provenance"], [r for r in records if r.get("kind") == "run"]


def summarise(runs):
    rows = []
    for family in dict.fromkeys(r["family"] for r in runs):
        for method in METHOD_ORDER:
            group = [r for r in runs if r["family"] == family and r["seed_method"] == method]
            if not group:
                continue
            p = statistics.fmean(r["success_fraction"] for r in group)
            cost = statistics.median(r["cost_per_restart_ms"] for r in group)
            row = dict(family=family, method=method, runs=len(group), p=p, cost=cost,
                       expected=cost / p if p > 0 else None,
                       instances_with_success=sum(r["success_fraction"] > 0 for r in group),
                       seed_seconds=statistics.fmean(r["seed_seconds"] for r in group),
                       polish_seconds=statistics.fmean(r["polish_seconds"] for r in group),
                       chain_flips=statistics.median(r["kernel_flips_per_second_per_chain"] for r in group))
            if "final_ess" in group[0]:
                row.update(ess=statistics.fmean(r["final_ess"] for r in group),
                           saturated=statistics.fmean(r["saturated_fraction"] for r in group),
                           solved_during_seed=sum(r["steps_with_a_solution"] > 0 for r in group),
                           weights=group[0]["weights"])
            rows.append(row)
    return rows


def write_table(provenance, rows, runs, path):
    first = provenance[0] if provenance else {}
    arguments = first.get("arguments", {})
    lines = ["# Seed comparison: per-restart success of one polish from four seeds", "",
             f"- Date {first.get('timestamp')}; commit {first.get('commit')}; device {first.get('device')} "
             f"({first.get('gpu')}), torch {first.get('torch')}; other GPU processes at start: "
             f"{first.get('gpu_processes_at_start') or 'none'}",
             f"- {arguments.get('slots')} slots per run, T = {arguments.get('steps')} seeding steps (mu: Adam on the "
             f"mu objective; tilted: the loop, G = slots / {arguments.get('slots_per_group')} groups), polish = "
             f"{arguments.get('polish_flips_per_variable')} n SKC flips of the flip kernel, noise 0.5; instances: the "
             f"first {arguments.get('instances')} of each family; seeds {arguments.get('seeds')}.",
             "- p = mean over runs of the fraction of slots satisfied after the polish; cost = median over runs of "
             "(seed seconds + polish seconds) / slots; expected time = cost / p. The tilted seed draws the slots "
             "from its final q_theta; its ESS and saturated fraction are the loop's last step.",
             "- Replication of Putikhin and Kascheev, EWDTS 2017 (DOI 10.1109/EWDTS.2017.8110119): they seeded "
             "probSAT from a continuous extension; their abstract gives no per-restart number and no code was found. "
             "Where their protocol is recoverable it differs from this one in the local search (probSAT against the "
             "SKC kernel) and in the seed (a nonlinear optimisation of a continuous extension against mu ascent and "
             "the tilted loop). Nearest public code of the loop's family, not run here: "
             "omargup/Policy-Gradient-MaxSAT-Solver (REINFORCE with a baseline, reads DIMACS, no licence) and "
             "VicentePerezSoloviev/EDAspy (PBIL and UMDA, MIT).", "",
             "| family | seed | runs | p | instances with p > 0 | cost / restart (ms) | expected time (ms) | "
             "seed s | polish s | ESS | saturated | seeding steps with a solution | weights |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        expected = f"{r['expected']:.1f}" if r["expected"] is not None else "inf"
        extra = (f"{r['ess']:.1f} | {r['saturated']:.3f} | {r['solved_during_seed']}/{r['runs']} | {r['weights']}"
                 if "ess" in r else "- | - | - | -")
        lines.append(f"| {r['family']} | {r['method']} | {r['runs']} | {r['p']:.4f} | {r['instances_with_success']}/{r['runs']} "
                     f"| {r['cost']:.3f} | {expected} | {r['seed_seconds']:.2f} | {r['polish_seconds']:.2f} | {extra} |")
    chain = statistics.median(r["kernel_flips_per_second_per_chain"] for r in runs)
    slots = int(arguments.get("slots", 0) or 0)
    lines += ["", f"Throughput: the kernel's polish runs at a median {chain:,.0f} flips per second per chain "
              f"({chain * slots / 1e6:.1f} M per second over the {slots} chains) on the {first.get('device')} against "
              f"{PROBSAT_FLIPS_PER_SECOND / 1e6:.2f} M flips per second for probSAT on one CPU core (measured on "
              "uuf250-01, 20 M flips, seeds 1 and 2). One chain of the kernel is "
              f"{PROBSAT_FLIPS_PER_SECOND / chain:.0f}x slower than probSAT; the batch is what the GPU buys.",
              "", "Every run is in seed_comparison.jsonl with its seed, instance, commit and timestamps."]
    path.write_text("\n".join(lines) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", type=Path, default=HERE / "seed_comparison.jsonl")
    parser.add_argument("--output", type=Path, default=HERE / "seed_comparison.md")
    arguments = parser.parse_args()
    provenance, runs = load(arguments.input)
    write_table(provenance, summarise(runs), runs, arguments.output)
