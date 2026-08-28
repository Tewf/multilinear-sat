"""Gradient ascent on the relaxed objective with random restarts; every few steps the point
is rounded, checked, and the best rounded slot gets a short WalkSAT polish."""
import csv
import math
import time
from dataclasses import dataclass

import numpy as np
import torch

from rounding import count_unsatisfied, count_unsatisfied_python, round_to_assignment
from walksat import build_occurrence_lists, walksat_polish


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


class _Polisher:
    """Holds what WalkSAT needs about the formula, and polishes the best rounded slots."""

    def __init__(self, formula, configuration, seed):
        self.variable_index = formula.variable_index.cpu().numpy()
        self.sign = formula.sign.cpu().numpy()
        self.occurrence_clauses, self.occurrence_signs = build_occurrence_lists(
            self.variable_index, self.sign, formula.num_variables)
        self.max_flips = configuration.walksat_flips_per_variable * formula.num_variables
        self.noise = configuration.walksat_noise
        self.top_slots = configuration.polish_top_slots
        self.rng = np.random.default_rng(seed)

    def __call__(self, assignment, unsat):
        """The first satisfying assignment among the best slots, polished if needed, else None."""
        for slot in torch.argsort(unsat)[: self.top_slots].tolist():
            x, remaining = assignment[slot].cpu().numpy(), int(unsat[slot])
            if remaining > 0:
                x, remaining = walksat_polish(x, self.variable_index, self.sign, self.occurrence_clauses,
                                              self.occurrence_signs, self.max_flips, self.noise, self.rng)
            if remaining == 0:
                return [int(value) for value in x]
        return None


def solve(formula, objective, configuration, seed, trajectory_path=None):
    """objective(p) returns an ObjectiveValue whose log_probability [B] is maximised.
    formula must already live on the device the configuration names."""
    device = formula.variable_index.device
    generator = torch.Generator(device=device).manual_seed(seed)
    polisher = _Polisher(formula, configuration, seed)
    shape = (configuration.batch_size, formula.num_variables)
    trajectory, unsat_events = [], []
    num_steps = num_restarts = 0
    solution = None
    start = time.perf_counter()

    def time_is_up():
        return time.perf_counter() - start >= configuration.time_limit_seconds

    while solution is None and not time_is_up():
        theta = (torch.rand(shape, generator=generator, device=device) * 2 - 1) * configuration.init_scale
        theta.requires_grad_(True)
        optimizer = torch.optim.Adam([theta], lr=configuration.learning_rate)
        num_restarts += 1
        for _ in range(configuration.steps_per_restart):
            p = torch.tanh(theta)
            value = objective(p)
            optimizer.zero_grad()
            (-value.log_probability.sum()).backward()
            optimizer.step()
            num_steps += 1
            min_unsat = math.nan
            if num_steps % configuration.rounding_interval == 0:
                with torch.no_grad():
                    assignment = round_to_assignment(p)
                    unsat = count_unsatisfied(assignment, formula)
                min_unsat = int(unsat.min())
                unsat_events.append(min_unsat)
                solution = polisher(assignment, unsat)
            if trajectory_path is not None:
                trajectory.append((num_steps, num_restarts, value.mu[0].item(), value.var[0].item(),
                                   value.log_probability[0].item(), value.probability[0].item(), min_unsat))
            if solution is not None or time_is_up():
                break

    if solution is not None and count_unsatisfied_python(formula.clauses.cpu().tolist(), solution) != 0:
        raise RuntimeError("the solver reported an assignment that the independent check rejects")
    if trajectory_path is not None:
        with open(trajectory_path, "w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["step", "restart", "mu", "var", "log_F", "F", "min_unsat_at_rounding"])
            writer.writerows(trajectory)
    return SolveResult(solution is not None, solution, time.perf_counter() - start, num_restarts, num_steps,
                       min(unsat_events) if unsat_events else -1,
                       float(np.mean(unsat_events)) if unsat_events else math.nan, len(unsat_events))
