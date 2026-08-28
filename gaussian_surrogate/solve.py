"""Command line: python solve.py file.cnf --obj {F,mu,fourier} [--seed N] [--time-limit S]
[--log-trajectory out.csv] [--device cpu|cuda]. SAT-competition style output and exit code."""
import argparse
import json
import sys

from adjacency import build_clause_adjacency
from configuration import Configuration
from dimacs import read_dimacs
from methods import METHODS, build_method
from solver import solve


def parse_arguments():
    parser = argparse.ArgumentParser(description="3-SAT by gradient ascent on a relaxed objective")
    parser.add_argument("cnf_path")
    parser.add_argument("--obj", choices=list(METHODS), default="F",
                        help="F: Gaussian surrogate on p = tanh(theta); mu: expected satisfied clauses on "
                             "tanh(theta); fourier: the same energy on the box [-1,1]^n, clipped after each step")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--time-limit", type=float, default=Configuration.time_limit_seconds, metavar="SECONDS")
    parser.add_argument("--log-trajectory", metavar="CSV", help="write mu, var, F per step for slot 0")
    parser.add_argument("--device", choices=["cpu", "cuda"], default=Configuration.device)
    return parser.parse_args()


def main():
    arguments = parse_arguments()
    configuration = Configuration(time_limit_seconds=arguments.time_limit, device=arguments.device)
    formula = read_dimacs(arguments.cnf_path).to(configuration.device)
    adjacency = build_clause_adjacency(formula).to(configuration.device)
    print(f"c gaussian-surrogate: {formula.num_variables} variables, {formula.num_clauses} clauses, "
          f"{adjacency.num_pairs} clause pairs sharing a variable, objective {arguments.obj}, "
          f"device {configuration.device}, seed {arguments.seed}")
    objective, relaxation = build_method(arguments.obj, formula, adjacency, configuration.variance_floor)
    result = solve(formula, objective, relaxation, configuration, arguments.seed, arguments.log_trajectory)
    print("c json " + json.dumps({
        "status": "SATISFIABLE" if result.solved else "UNKNOWN", "time_seconds": round(result.time_seconds, 4),
        "restarts": result.num_restarts, "steps": result.num_steps,
        "min_unsat_at_rounding": result.min_unsat_at_rounding,
        "mean_unsat_at_rounding": round(result.mean_unsat_at_rounding, 3),
        "rounding_events": result.num_rounding_events}))
    if result.solved:
        print("s SATISFIABLE")
        print("v " + " ".join(str((index + 1) * value) for index, value in enumerate(result.assignment)) + " 0")
        return 10
    print("s UNKNOWN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
