"""Rounding counts, the WalkSAT polish, the relaxations, and every method on a planted instance."""
import csv
import math

import numpy as np
import pytest
import torch

from adjacency import build_clause_adjacency
from configuration import Configuration
from dimacs import formula_from_clauses
from random_instances import planted_3sat, random_3sat
from methods import METHODS, build_method
from relaxation import BoxRelaxation
from rounding import count_unsatisfied, count_unsatisfied_python
from solver import solve
from walksat import build_occurrence_lists, walksat_polish


def test_vectorised_count_matches_the_python_count():
    clauses = random_3sat(12, 50, 0)
    formula = formula_from_clauses(12, clauses)
    generator = torch.Generator().manual_seed(0)
    assignment = torch.where(torch.rand(16, 12, generator=generator) < 0.5, -1.0, 1.0)
    expected = [count_unsatisfied_python(clauses, row) for row in assignment.tolist()]
    assert count_unsatisfied(assignment, formula).tolist() == expected


def test_walksat_polish_repairs_a_corrupted_planted_assignment():
    num_variables = 30
    clauses, planted = planted_3sat(num_variables, 120, 1)
    formula = formula_from_clauses(num_variables, clauses)
    variable_index, sign = formula.variable_index.numpy(), formula.sign.numpy()
    occurrence_clauses, occurrence_signs = build_occurrence_lists(variable_index, sign, num_variables)
    rng = np.random.default_rng(1)
    corrupted = planted.astype(np.float32)
    corrupted[rng.choice(num_variables, size=4, replace=False)] *= -1
    assert count_unsatisfied_python(clauses, corrupted.tolist()) > 0
    polished, remaining = walksat_polish(corrupted, variable_index, sign, occurrence_clauses,
                                         occurrence_signs, max_flips=60, noise=0.5, rng=rng)
    assert remaining == 0
    assert count_unsatisfied_python(clauses, polished.tolist()) == 0


def test_box_relaxation_starts_and_stays_inside_the_box():
    relaxation = BoxRelaxation()
    parameters = relaxation.initial_parameters((4, 7), torch.Generator().manual_seed(0), scale=3.0)
    assert parameters.abs().max() <= 1.0
    with torch.no_grad():
        parameters += 5.0
    relaxation.project(parameters)
    assert torch.all(parameters == 1.0)


def planted_problem(seed):
    clauses, _ = planted_3sat(30, 120, seed)
    formula = formula_from_clauses(30, clauses)
    return clauses, formula, build_clause_adjacency(formula)


@pytest.mark.parametrize("method", list(METHODS))
def test_every_method_finds_a_planted_solution(method):
    clauses, formula, adjacency = planted_problem(2)
    configuration = Configuration(batch_size=16, time_limit_seconds=10.0, device="cpu")
    objective, relaxation = build_method(method, formula, adjacency, configuration.variance_floor)
    result = solve(formula, objective, relaxation, configuration, seed=0)
    assert result.solved
    assert count_unsatisfied_python(clauses, result.assignment) == 0


@pytest.mark.parametrize("method", list(METHODS))
def test_every_method_logs_a_finite_trajectory(method, tmp_path):
    _, formula, adjacency = planted_problem(3)
    configuration = Configuration(batch_size=4, steps_per_restart=30, time_limit_seconds=5.0, device="cpu")
    objective, relaxation = build_method(method, formula, adjacency, configuration.variance_floor)
    path = tmp_path / "trajectory.csv"
    solve(formula, objective, relaxation, configuration, seed=0, trajectory_path=str(path))
    with open(path) as handle:
        rows = list(csv.DictReader(handle))
    assert rows and list(rows[0]) == ["step", "restart", "mu", "var", "log_F", "F", "min_unsat_at_rounding"]
    assert all(math.isfinite(float(row[column])) for row in rows for column in ("mu", "var", "log_F", "F"))
