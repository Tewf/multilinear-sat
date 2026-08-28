"""Gradient ascent on a relaxed objective with random restarts; every few steps the point is
rounded, checked, and the best rounded slot gets a short WalkSAT polish."""
import csv
import math
import time
from dataclasses import dataclass

import numpy as np
import torch

from rounding import count_unsatisfied, count_unsatisfied_python, round_to_assignment
from walksat import BestSlotPolisher


@dataclass
class SolveResult:
    solved: bool
    assignment: list | None          # +-1 per variable, index 0 is variable 1
    time_seconds: float
    num_restarts: int
    num_steps: int
    min_unsat_at_rounding: int       # over every rounding event, before polishing
    mean_unsat_at_rounding: float    # batch minimum per event, averaged over events
    num_rounding_events: int


def solve(formula, objective, relaxation, configuration, seed, trajectory_path=None):
    """objective(p, with_diagnostics) returns an ObjectiveValue whose ascent_target [B] is
    maximised; relaxation maps the optimised parameters to p and keeps them feasible. The
    formula must already live on the device the configuration names."""
    device = formula.variable_index.device
    generator = torch.Generator(device=device).manual_seed(seed)
    polisher = BestSlotPolisher(formula, configuration, seed)
    shape = (configuration.batch_size, formula.num_variables)
    log_trajectory = trajectory_path is not None
    trajectory, unsat_events = [], []
    num_steps = num_restarts = 0
    solution = None
    start = time.perf_counter()

    def time_is_up():
        return time.perf_counter() - start >= configuration.time_limit_seconds

    while solution is None and not time_is_up():
        parameters = relaxation.initial_parameters(shape, generator, configuration.init_scale)
        optimizer = torch.optim.Adam([parameters], lr=configuration.learning_rate)
        num_restarts += 1
        for _ in range(configuration.steps_per_restart):
            p = relaxation.point(parameters)
            value = objective(p, with_diagnostics=log_trajectory)
            num_steps += 1
            min_unsat = math.nan
            if num_steps % configuration.rounding_interval == 0:
                with torch.no_grad():
                    assignment = round_to_assignment(p)
                    unsat = count_unsatisfied(assignment, formula)
                min_unsat = int(unsat.min())
                unsat_events.append(min_unsat)
                solution = polisher(assignment, unsat)
            if log_trajectory:
                trajectory.append((num_steps, num_restarts, value.mu[0].item(), value.var[0].item(),
                                   value.log_probability[0].item(), value.probability[0].item(), min_unsat))
            if solution is not None or time_is_up():
                break
            optimizer.zero_grad()
            (-value.ascent_target.sum()).backward()
            optimizer.step()
            relaxation.project(parameters)

    if solution is not None and count_unsatisfied_python(formula.clauses.cpu().tolist(), solution) != 0:
        raise RuntimeError("the solver reported an assignment that the independent check rejects")
    if log_trajectory:
        with open(trajectory_path, "w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["step", "restart", "mu", "var", "log_F", "F", "min_unsat_at_rounding"])
            writer.writerows(trajectory)
    return SolveResult(solution is not None, solution, time.perf_counter() - start, num_restarts, num_steps,
                       min(unsat_events) if unsat_events else -1,
                       float(np.mean(unsat_events)) if unsat_events else math.nan, len(unsat_events))
