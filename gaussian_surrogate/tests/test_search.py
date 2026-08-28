"""Rounding counts, the WalkSAT polish, and the whole solver on a planted instance, on the CPU."""
import numpy as np
import torch

from adjacency import build_clause_adjacency
from configuration import Configuration
from dimacs import formula_from_clauses
from instances import planted_3sat, random_3sat
from objective import gaussian_surrogate
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


def test_solver_finds_a_planted_solution():
    num_variables = 30
    clauses, _ = planted_3sat(num_variables, 120, 2)
    formula = formula_from_clauses(num_variables, clauses)
    adjacency = build_clause_adjacency(formula)
    configuration = Configuration(batch_size=16, time_limit_seconds=10.0, device="cpu")
    result = solve(formula, lambda p: gaussian_surrogate(p, formula, adjacency, configuration.variance_floor),
                   configuration, seed=0)
    assert result.solved
    assert count_unsatisfied_python(clauses, result.assignment) == 0
