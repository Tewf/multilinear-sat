"""The markdown table of a basin-of-attraction run: one row per (point, method)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from methods import METHODS  # noqa: E402

ROUNDING_INTERVAL = 25   # must match basin_of_attraction.py; printed in the table header
SEED = 0


def write_table(records, path, arguments):
    lines = ["# Basin of attraction: fraction of restarts that reach a satisfying assignment", "",
             f"No WalkSAT polish. {arguments.batch_size} restarts per instance, {arguments.steps} Adam steps, "
             f"rounding every {ROUNDING_INTERVAL} steps; a restart counts if any of its rounded points satisfies "
             f"the formula. Fractions are means over instances; device {arguments.device}, seed {SEED}.", "",
             "| point | method | instances | fraction of restarts | instances with a success | mean #unsat at the end |",
             "|---|---|---|---|---|---|"]
    keys = sorted({(r["point"], r["method"]) for r in records}, key=lambda k: (k[0], list(METHODS).index(k[1])))
    for point, method in keys:
        rows = [r for r in records if r["point"] == point and r["method"] == method]
        fraction = sum(r["fraction"] for r in rows) / len(rows)
        successes = sum(1 for r in rows if r["fraction"] > 0)
        mean_unsat = sum(r["mean_final_unsat"] for r in rows) / len(rows)
        lines.append(f"| {point} | {method} | {len(rows)} | {fraction:.4f} | {successes}/{len(rows)} | {mean_unsat:.1f} |")
    path.write_text("\n".join(lines) + "\n")
