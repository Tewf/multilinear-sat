#!/usr/bin/env python3
"""Reads arms_results.jsonl, prices every arm per family (per-restart success p, cost per
restart, expected time to a solution, flips per solution) over the instances decided
satisfiable, finds the Pareto front on (expected time, p) per family and the arms no other
arm dominates overall, and writes front.md (survivors with their numbers) and rejected.md
(each dominated arm, by which arm, on which families, with the numbers; nothing deleted)."""
import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import arms                          # noqa: E402
from walk_runs import load_records   # noqa: E402

HERE = Path(__file__).resolve().parent
INF = float("inf")


def verdicts(records):
    """SAT if any certificate exists (CaDiCaL's record, probSAT, or a walk); UNSAT on CaDiCaL's word; else undecided."""
    verdict = {}
    if arms.BENCHMARK_RESULTS.exists():
        for r in json.loads(arms.BENCHMARK_RESULTS.read_text()):
            if r.get("solver") == "cadical" and r.get("status") in ("SAT", "UNSAT"):
                verdict[r["instance"]] = r["status"]
    for r in records:
        if r["status"] == "SATISFIABLE":
            verdict[r["instance"]] = "SAT"
    return verdict


def cells(records, verdict):
    """{(arm, family): cell} over the decided-satisfiable instances of the family."""
    out = {}
    for family in arms.FAMILIES:
        names = {p.name for p in arms.instances(family)}
        satisfiable = {name for name in names if verdict.get(name) == "SAT"}
        for arm in list(arms.ARMS) + ["probsat"]:
            group = [r for r in records if r["arm"] == arm and r["family"] == family and r["instance"] in satisfiable]
            if not group:
                continue
            cell = dict(arm=arm, family=family, runs=len(group), instances=len({r["instance"] for r in group}),
                        satisfiable=len(satisfiable), undecided=len(names) - len(satisfiable) - sum(verdict.get(n) == "UNSAT" for n in names),
                        unsatisfiable=sum(verdict.get(n) == "UNSAT" for n in names),
                        celsius=[c for r in group for c in (r.get("package_celsius") or []) if c is not None])
            if arm == "probsat":
                solved = [r for r in group if r["status"] == "SATISFIABLE"]
                cell.update(solved=len(solved), successes=len(solved), expected_ms=statistics.fmean(r["wall_seconds"] for r in solved) * 1000 if solved else INF,
                            median_ms=statistics.median(r["wall_seconds"] for r in solved) * 1000 if solved else INF,
                            flips_per_solution=statistics.fmean(r["flips"] for r in solved if r["flips"]) if solved else INF, p=None, cost_ms=None)
            else:
                successes = sum(r["polish_successes"] or 0 for r in group)
                slot_runs = sum(r["heuristic_slots"] * (r["runs_completed"] or 0) for r in group)
                seconds = sum((r["seed_seconds"] or 0) + (r["polish_seconds"] or 0) for r in group)
                flips = sum(r["flips"] or 0 for r in group)
                cell.update(successes=successes, p=successes / slot_runs if slot_runs else 0.0, cost_ms=seconds * 1000 / slot_runs if slot_runs else INF,
                            expected_ms=seconds * 1000 / successes if successes else INF, flips_per_solution=flips / successes if successes else INF,
                            solved=sum(r["status"] == "SATISFIABLE" for r in group), capped=sum(bool(r.get("capped")) for r in group),
                            first_solution_ms=statistics.median(r["first_solution_seconds"] for r in group if r["first_solution_seconds"] is not None) * 1000
                            if any(r["first_solution_seconds"] is not None for r in group) else INF)
            out[(arm, family)] = cell
    return out


def threshold(ka, kb, band=arms.THERMAL_BAND):
    """The ratio two cells must exceed to be distinguished: the thermal band, or two standard errors of
    the log ratio under Poisson success counts, whichever is larger; infinite when a count is zero."""
    if not ka or not kb:
        return INF
    return max(1 + band, math.exp(2 * math.sqrt(1 / ka + 1 / kb)))


def better(a, b, ka=None, kb=None, band=arms.THERMAL_BAND):
    """1 if a is better than b beyond the threshold, -1 if worse, 0 if not distinguished (smaller is
    better; inf ties inf; a finite value beats inf whatever the counts)."""
    if a == b:
        return 0
    if a == INF or b == INF:
        return -1 if a == INF else 1
    limit = threshold(ka, kb, band)
    if b / a > limit:
        return 1
    if a / b > limit:
        return -1
    return 0


def better_larger(a, b, ka=None, kb=None, band=arms.THERMAL_BAND):
    """The same rule where larger is better (p); zero against a positive value loses whatever the counts."""
    if a == b:
        return 0
    if a == 0 or b == 0:
        return -1 if a == 0 else 1
    limit = threshold(ka, kb, band)
    if a / b > limit:
        return 1
    if b / a > limit:
        return -1
    return 0


def compare(table, a, b, f):
    """(expected-time verdict, p verdict) of a against b on family f, counts included."""
    x, y = table[(a, f)], table[(b, f)]
    return (better(x["expected_ms"], y["expected_ms"], x["successes"], y["successes"]),
            better_larger(x["p"], y["p"], x["successes"], y["successes"]))


def dominates(table, a, b):
    """a dominates b: a was measured on every family b was, is at least as good on expected time on each,
    and strictly better on one; or not distinguished on expected time anywhere and better on p on one.
    Returns the families that carry the evidence, or None."""
    families = [f for f in arms.FAMILIES if (b, f) in table]
    if not families or any((a, f) not in table for f in families):
        return None
    verdicts = {f: compare(table, a, b, f) for f in families}
    if any(e < 0 for e, _ in verdicts.values()):
        return None
    if any(e > 0 for e, _ in verdicts.values()):
        return [f for f, (e, _) in verdicts.items() if e > 0]
    on_p = [f for f, (_, q) in verdicts.items() if q > 0]
    return on_p or None


def fronts(table):
    names = [a for a in arms.ARMS if any((a, f) in table for f in arms.FAMILIES)]
    rejected = {}
    for b in names:
        for a in names:
            if a != b and (evidence := dominates(table, a, b)):
                rejected.setdefault(b, []).append((a, evidence))
    survivors = [a for a in names if a not in rejected]
    per_family = {}
    for f in arms.FAMILIES:
        here = [a for a in names if (a, f) in table]
        per_family[f] = [a for a in here if not any(compare(table, o, a, f)[0] > 0
                                                    or (compare(table, o, a, f)[0] == 0 and compare(table, o, a, f)[1] > 0) for o in here if o != a)]
    return survivors, rejected, per_family


def fmt(x, digits=3):
    return "inf" if x == INF else (f"{x:.{digits}f}" if isinstance(x, float) else str(x))


def cell_row(c):
    if c["arm"] == "probsat":
        return (f"| {c['family']} | probSAT, one core | {c['solved']}/{c['runs']} solved | - | - | mean {fmt(c['expected_ms'], 2)}, median {fmt(c['median_ms'], 2)} "
                f"| {fmt(c['flips_per_solution'], 0)} | - |")
    band = f"{min(c['celsius']):.0f} to {max(c['celsius']):.0f}" if c["celsius"] else "-"
    return (f"| {c['family']} | {c['arm']} | {c['runs']} on {c['instances']} instances | {c['successes']} | {c['p']:.4g} | {fmt(c['cost_ms'], 4)} | {fmt(c['expected_ms'])} "
            f"| {fmt(c['flips_per_solution'], 0)} | {fmt(c['first_solution_ms'], 1)} | {band} |")


HEADER = ("| family | arm | runs | satisfied slot-runs | p | cost / restart (ms) | expected time (ms) | flips per solution | median first solution (ms) | package C |\n"
          "|---|---|---|---|---|---|---|---|---|---|")
PROBSAT_HEADER = "| family | arm | runs | | | wall ms per solution | flips per solution | |\n|---|---|---|---|---|---|---|---|"


def provenance_lines(records):
    stamps = [r for r in records if r.get("kind") == "provenance"]
    if not stamps:
        return ["- no provenance block yet"]
    commits = sorted({s["commit"] for s in stamps})
    binaries = sorted({f"{Path(s['binary']).name} (sha256 {s['binary_sha256']})" for s in stamps})
    return [f"- {len(stamps)} stages from {stamps[0]['timestamp']} to {stamps[-1]['timestamp']}; frozen binary {', '.join(binaries)}, "
            f"named by the commit it was built from; HEAD at the stages: {', '.join(commits)}; GPU at the first stage: {stamps[0]['gpu']}.",
            f"- Every run is in arms_results.jsonl with its command, seed, timeline, package temperature before and after, and the gate readings of its stage."]


def write_front(records, table, survivors, per_family, verdict):
    lines = ["# The front: the arms no other arm dominates, with their numbers", "", *provenance_lines(records),
             f"- Rule: [protocol.md](protocol.md); two cells are distinguished only when their ratio exceeds the {arms.THERMAL_BAND:.0%} thermal band "
             "and two standard errors of the log ratio under Poisson success counts, exp(2 sqrt(1/k_a + 1/k_b)); an arm dominates only arms it was "
             "measured beside on every one of their families.", "",
             "## Overall", ""]
    for a in survivors:
        measured = [f for f in arms.FAMILIES if (a, f) in table]
        lines.append(f"- **{a}** ({', '.join(f'{k}={v}' for k, v in arms.configuration(a).items())}), measured on {', '.join(measured)}")
    lines += ["", "## Per family: every arm on the family's front, then probSAT beside it", ""]
    for f in arms.FAMILIES:
        if not any((a, f) in table for a in arms.ARMS):
            names = {p.name for p in arms.instances(f)}
            if any(r["family"] == f for r in records if r.get("kind") == "run"):
                lines += [f"### {f}: no instance decided satisfiable of {len(names)} "
                          f"({sum(verdict.get(n) == 'UNSAT' for n in names)} unsatisfiable, the rest undecided: probSAT capped, CaDiCaL without a verdict, no walk certificate); no cell", ""]
            continue
        counts = next(c for (a, ff), c in table.items() if ff == f)
        lines += [f"### {f}: {counts['satisfiable']} satisfiable, {counts['unsatisfiable']} unsatisfiable, {counts['undecided']} undecided of "
                  f"{counts['satisfiable'] + counts['unsatisfiable'] + counts['undecided']} instances (cells over the satisfiable ones)", "", HEADER]
        lines += [cell_row(table[(a, f)]) for a in per_family[f]]
        if ("probsat", f) in table:
            lines += ["", PROBSAT_HEADER, cell_row(table[("probsat", f)])]
        lines.append("")
    (HERE / "front.md").write_text("\n".join(lines) + "\n")


def tilted_on_the_records():
    """The tilted seed against a uniform start on the same (instance, seed) runs of the sampling-walk record."""
    if not arms.SEED_COMPARISON.exists():
        return None
    runs = [r for r in load_records(arms.SEED_COMPARISON) if r.get("kind") == "run"]
    tilted = [r for r in runs if r["arm"] == "tilted500" and r.get("expected_time_ms")]
    pairs = []
    for t in tilted:
        u = next((r for r in runs if r["arm"] == "uniform" and r["instance"] == t["instance"] and r["seed"] == t["seed"]), None)
        if u and u.get("expected_time_ms"):
            pairs.append((t["expected_time_ms"], u["expected_time_ms"]))
    if not pairs:
        return None
    return len(pairs), statistics.fmean(t for t, _ in pairs), statistics.fmean(u for _, u in pairs)


def write_rejected(records, table, rejected):
    lines = ["# The rejected arms, each with the arm that dominates it and the numbers", "", *provenance_lines(records),
             "- An arm is dominated when another arm, measured on every family it was measured on, is at least as good on expected time on "
             f"each and strictly better on one, or not distinguished on expected time anywhere and better on p on one; distinguished means beyond the "
             f"{arms.THERMAL_BAND:.0%} thermal band and beyond two standard errors of the log ratio under Poisson success counts (the satisfied slot-runs column). "
             "Nothing is deleted: every rejected arm keeps its cells here beside its dominator's.", ""]
    for b, by in rejected.items():
        lines.append(f"## {b} ({', '.join(f'{k}={v}' for k, v in arms.configuration(b).items())})")
        for a, evidence in by:
            lines.append(f"- dominated by **{a}** on {', '.join(evidence)}")
        lines += ["", HEADER]
        for f in arms.FAMILIES:
            if (b, f) in table:
                lines.append(cell_row(table[(b, f)]))
                for a, _ in by:
                    if (a, f) in table:
                        lines.append(cell_row(table[(a, f)]))
        lines.append("")
    n5000 = [f for f in arms.N5000 if ("base", f) in table]
    if n5000:
        lines += ["## n = 5000: the one-factor arms, not run, the base arm's zero standing for all of them",
                  f"- {', '.join(arms.ONE_FACTOR_ARMS_NOT_RUN_AT_N5000)}: cut on the base stage's own numbers (protocol.md). The base arm "
                  "found nothing at n = 5000 in the family's budget of 200n flips per slot, so a one-factor change of it would carry "
                  "the same zero and price nothing; the long-walk arm is the n = 5000 test.", "", HEADER]
        for f in n5000:
            lines.append(cell_row(table[("base", f)]))
        lines += ["", PROBSAT_HEADER] + [cell_row(table[("probsat", f)]) for f in n5000 if ("probsat", f) in table] + [""]
    t = tilted_on_the_records()
    if t:
        n, tilted_ms, uniform_ms = t
        lines += ["## tilted seed (rejected on the sampling-walk records, not run here)",
                  f"- On the {n} uf250-1065 runs the tilted arm completed in benchmark/seed_comparison.jsonl, the mean over runs of each run's "
                  f"expected time is {tilted_ms:.1f} ms against {uniform_ms:.2f} ms for a uniform start on the same (instance, seed) runs, "
                  f"{tilted_ms / uniform_ms:.0f}x (the record's table, pooling the runs, says 94x); "
                  "the brief admits it only within 2x of uniform somewhere, so it is not an arm.", ""]
    (HERE / "rejected.md").write_text("\n".join(lines) + "\n")


def main():
    records = [r for r in load_records(arms.RECORDS)]
    runs = [r for r in records if r.get("kind") == "run"]
    verdict = verdicts(runs)
    table = cells(runs, verdict)
    survivors, rejected, per_family = fronts(table)
    write_front(records, table, survivors, per_family, verdict)
    write_rejected(records, table, rejected)
    print(f"{len(runs)} runs, {len(table)} cells; front: {', '.join(survivors)}; rejected: {', '.join(rejected) or 'none'}")


if __name__ == "__main__":
    main()
