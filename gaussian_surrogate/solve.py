"""Command line: python solve.py file.cnf --obj {F,mu,fourier,tilted} [--seed N] [--time-limit S]
[--log-trajectory out.csv] [--device cpu|cuda], plus one flag per field of Configuration.
SAT-competition style output and exit code."""
import argparse
import json
import sys
from dataclasses import fields

from adjacency import build_clause_adjacency
from configuration import Configuration
from dimacs import read_dimacs
from methods import METHODS, SAMPLING_METHODS, build_method
from solver import solve

EXPLICIT_FLAGS = ("time_limit_seconds", "device")


def parse_arguments():
    parser = argparse.ArgumentParser(description="3-SAT by gradient ascent on a relaxed objective, or by the "
                                                 "tilted sampling-gradient loop",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("cnf_path")
    parser.add_argument("--obj", choices=list(METHODS) + list(SAMPLING_METHODS), default="F",
                        help="F: Gaussian surrogate on p = tanh(theta); mu: expected satisfied clauses on "
                             "tanh(theta); fourier: the same energy on the box [-1,1]^n, clipped after each step; "
                             "tilted: the sampling-gradient loop on the tilted objective log E[exp(beta S)]")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--time-limit", dest="time_limit_seconds", type=float,
                        default=Configuration.time_limit_seconds, metavar="SECONDS")
    parser.add_argument("--log-trajectory", metavar="CSV", help="write the per-step log (slot 0 for the gradient "
                        "methods, group means for tilted)")
    parser.add_argument("--device", choices=["cpu", "cuda"], default=Configuration.device)
    for field in fields(Configuration):
        if field.name not in EXPLICIT_FLAGS:
            parser.add_argument("--" + field.name.replace("_", "-"), dest=field.name,
                                type=type(field.default), default=field.default)
    return parser.parse_args()


def run(arguments, configuration, formula):
    if arguments.obj in SAMPLING_METHODS:
        return SAMPLING_METHODS[arguments.obj](formula, configuration, arguments.seed, arguments.log_trajectory)
    adjacency = build_clause_adjacency(formula).to(configuration.device)
    objective, relaxation = build_method(arguments.obj, formula, adjacency, configuration.variance_floor)
    return solve(formula, objective, relaxation, configuration, arguments.seed, arguments.log_trajectory)


def main():
    arguments = parse_arguments()
    configuration = Configuration(**{field.name: getattr(arguments, field.name) for field in fields(Configuration)})
    formula = read_dimacs(arguments.cnf_path).to(configuration.device)
    print(f"c gaussian-surrogate: {formula.num_variables} variables, {formula.num_clauses} clauses, "
          f"objective {arguments.obj}, device {configuration.device}, seed {arguments.seed}")
    result = run(arguments, configuration, formula)
    statistics = {
        "status": "SATISFIABLE" if result.solved else "UNKNOWN", "time_seconds": round(result.time_seconds, 4),
        "restarts": result.num_restarts, "steps": result.num_steps,
        "min_unsat_at_rounding": result.min_unsat_at_rounding,
        "mean_unsat_at_rounding": round(result.mean_unsat_at_rounding, 3),
        "rounding_events": result.num_rounding_events}
    if result.posterior_rigorous is not None:
        statistics.update(rigorous_failures=result.rigorous_failures, heuristic_failures=result.heuristic_failures,
                          posterior_rigorous=result.posterior_rigorous, posterior_beta=result.posterior_beta)
    print("c json " + json.dumps(statistics))
    if result.solved:
        print("s SATISFIABLE")
        print("v " + " ".join(str((index + 1) * value) for index, value in enumerate(result.assignment)) + " 0")
        return 10
    print("s UNKNOWN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
