"""Basin of attraction of the gradient dynamics: the fraction of random restarts whose rounded
point satisfies the formula at some rounding event, with no WalkSAT polish, per objective.
Two axes: the clause ratio at fixed n (uniform random 3-SAT kept when CaDiCaL says satisfiable)
and n at the threshold ratio (SATLIB uf50 / uf100 / uf250). Writes a JSONL and a markdown table."""
import argparse
import json
import sys
import time
from pathlib import Path

import torch

PACKAGE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PACKAGE))
from adjacency import build_clause_adjacency            # noqa: E402
from configuration import Configuration                  # noqa: E402
from dimacs import formula_from_clauses, read_dimacs    # noqa: E402
from methods import METHODS, build_method               # noqa: E402
from random_instances import random_3sat                # noqa: E402
from rounding import count_unsatisfied, round_to_assignment  # noqa: E402
from basin_table import write_table  # noqa: E402

RATIOS = [3.0, 3.5, 4.0, 4.2, 4.26]     # ratio axis, at NUM_VARIABLES_RATIO_AXIS variables
NUM_VARIABLES_RATIO_AXIS = 100
SATLIB_FAMILIES = ["uf50-218", "uf100-430", "uf250-1065"]   # n axis, all at ratio 4.26
SATLIB_ROOT = PACKAGE.parent / "benchmark" / "instances"
INSTANCES_PER_POINT = 20
BATCH_SIZE = 512
STEPS = 500
ROUNDING_INTERVAL = 25   # also stated in basin_table.py
SEED = 0


def satisfiable_random_instances(num_variables, ratio, count, seed):
    """The first `count` uniform random 3-SAT instances (by seed) that CaDiCaL finds satisfiable."""
    from pysat.solvers import Solver
    instances, candidate = [], seed
    while len(instances) < count:
        clauses = random_3sat(num_variables, round(ratio * num_variables), candidate)
        with Solver(name="cadical153", bootstrap_with=clauses) as solver:
            if solver.solve():
                instances.append((f"n{num_variables}_r{ratio}_s{candidate}", formula_from_clauses(num_variables, clauses)))
        candidate += 1
    return instances


def satlib_instances(family, count):
    paths = sorted((SATLIB_ROOT / family).glob("*.cnf"))[:count]
    return [(path.stem, read_dimacs(path)) for path in paths]


def basin_fraction(formula, method_name, configuration, steps, seed):
    """(fraction of slots ever satisfied at a rounding event, mean and min unsat at the last one)."""
    device = formula.variable_index.device
    adjacency = build_clause_adjacency(formula).to(device)
    objective, relaxation = build_method(method_name, formula, adjacency, configuration.variance_floor)
    generator = torch.Generator(device=device).manual_seed(seed)
    parameters = relaxation.initial_parameters((configuration.batch_size, formula.num_variables),
                                               generator, configuration.init_scale)
    optimizer = torch.optim.Adam([parameters], lr=configuration.learning_rate)
    ever_satisfied = torch.zeros(configuration.batch_size, dtype=torch.bool, device=device)
    for step in range(1, steps + 1):
        p = relaxation.point(parameters)
        value = objective(p, with_diagnostics=False)
        if step % configuration.rounding_interval == 0:
            with torch.no_grad():
                unsat = count_unsatisfied(round_to_assignment(p), formula)
            ever_satisfied |= unsat == 0
        optimizer.zero_grad()
        (-value.ascent_target.sum()).backward()
        optimizer.step()
        relaxation.project(parameters)
    return ever_satisfied.float().mean().item(), unsat.float().mean().item(), int(unsat.min())


def points(arguments):
    for ratio in arguments.ratios:
        yield f"n={NUM_VARIABLES_RATIO_AXIS} ratio={ratio}", satisfiable_random_instances(
            NUM_VARIABLES_RATIO_AXIS, ratio, arguments.instances, SEED)
    for family in arguments.families:
        yield f"{family} (ratio 4.26)", satlib_instances(family, arguments.instances)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--device", default=Configuration.device)
    parser.add_argument("--instances", type=int, default=INSTANCES_PER_POINT)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--steps", type=int, default=STEPS)
    parser.add_argument("--ratios", type=float, nargs="*", default=RATIOS)
    parser.add_argument("--families", nargs="*", default=SATLIB_FAMILIES)
    parser.add_argument("--methods", nargs="*", default=list(METHODS))
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent)
    arguments = parser.parse_args()
    configuration = Configuration(batch_size=arguments.batch_size, rounding_interval=ROUNDING_INTERVAL,
                                  device=arguments.device)
    records, jsonl = [], arguments.out_dir / "basin_of_attraction.jsonl"
    with open(jsonl, "w") as handle:
        for point, instances in points(arguments):
            for name, formula in instances:
                formula = formula.to(arguments.device)
                for method in arguments.methods:
                    started = time.perf_counter()
                    fraction, mean_unsat, min_unsat = basin_fraction(formula, method, configuration, arguments.steps, SEED)
                    record = dict(point=point, instance=name, method=method, fraction=fraction,
                                  mean_final_unsat=mean_unsat, min_final_unsat=min_unsat,
                                  seconds=round(time.perf_counter() - started, 3))
                    records.append(record)
                    handle.write(json.dumps(record) + "\n")
                    print(f"{point:26s} {name:22s} {method:8s} fraction={fraction:.4f} "
                          f"mean_unsat={mean_unsat:.1f} min={min_unsat} {record['seconds']}s", flush=True)
    write_table(records, arguments.out_dir / "basin_of_attraction.md", arguments)


if __name__ == "__main__":
    main()
