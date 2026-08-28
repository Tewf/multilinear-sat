"""mu and var against brute-force enumeration on tiny formulas, in float64."""
import numpy as np
import pytest
import torch

from adjacency import ClauseAdjacency, build_clause_adjacency
from brute_force_reference import exact_moments
from dimacs import Formula, formula_from_clauses
from instances import random_3sat
from moments import expected_satisfied, pair_unsat_probability, unsat_probability, variance


def float64_formula_and_adjacency(num_variables, clauses):
    formula = formula_from_clauses(num_variables, clauses)
    formula = Formula(num_variables, formula.clauses, formula.variable_index, formula.sign.double())
    adjacency = build_clause_adjacency(formula)
    return formula, ClauseAdjacency(adjacency.pair_index, adjacency.slot_variable,
                                    adjacency.slot_sign.double(), adjacency.pair_scale.double())


def vectorised_moments(num_variables, clauses, p):
    formula, adjacency = float64_formula_and_adjacency(num_variables, clauses)
    p = torch.as_tensor(np.asarray(p), dtype=torch.float64).reshape(1, -1)
    unsat = unsat_probability(p, formula)
    mu = expected_satisfied(unsat, len(clauses))
    var = variance(unsat, pair_unsat_probability(p, adjacency), adjacency)
    return mu.item(), var.item()


def assert_matches_brute_force(num_variables, clauses, p):
    mu, var = vectorised_moments(num_variables, clauses, p)
    mu_exact, var_exact = exact_moments(num_variables, clauses, p)
    assert mu == pytest.approx(mu_exact, abs=1e-9)
    assert var == pytest.approx(var_exact, abs=1e-9)


def random_points(num_variables, count, seed):
    return np.random.default_rng(seed).uniform(-0.9, 0.9, size=(count, num_variables))


@pytest.mark.parametrize("seed, num_variables, num_clauses", [(0, 8, 20), (1, 9, 30), (2, 10, 40)])
def test_random_3sat(seed, num_variables, num_clauses):
    clauses = random_3sat(num_variables, num_clauses, seed)
    for p in random_points(num_variables, 3, seed):
        assert_matches_brute_force(num_variables, clauses, p)


HAND_MADE = [
    ("same_sign_shared_pair", 5, [[1, 2, 3], [1, 4, 5]]),
    ("opposite_sign_shared_pair", 5, [[1, 2, 3], [-1, 4, 5]]),
    ("two_shared_variables_same_signs", 4, [[1, 2, 3], [1, 2, 4]]),
    ("two_shared_variables_mixed_signs", 4, [[1, 2, 3], [1, -2, 4]]),
    ("identical_clauses", 3, [[1, 2, 3], [1, 2, 3]]),
    ("mixed_formula", 6, [[1, 2, 3], [1, 4, 5], [-2, 4, 6], [-3, -5, 6], [1, -2, 6]]),
]


@pytest.mark.parametrize("name, num_variables, clauses", HAND_MADE, ids=[case[0] for case in HAND_MADE])
def test_hand_made(name, num_variables, clauses):
    for p in random_points(num_variables, 4, len(name)):
        assert_matches_brute_force(num_variables, clauses, p)


def test_pair_scale_encodes_the_shared_variable_rule():
    scales = {name: build_clause_adjacency(formula_from_clauses(n, c)).pair_scale.tolist()
              for name, n, c in HAND_MADE[:5]}
    assert scales["same_sign_shared_pair"] == pytest.approx([2 / 64])
    assert scales["opposite_sign_shared_pair"] == [0.0]
    assert scales["two_shared_variables_same_signs"] == pytest.approx([4 / 64])
    assert scales["two_shared_variables_mixed_signs"] == [0.0]
    assert scales["identical_clauses"] == pytest.approx([8 / 64])


def test_disjoint_clauses_have_no_pairs_and_binomial_variance():
    num_variables, clauses = 9, [[1, 2, 3], [-4, 5, -6], [7, -8, 9]]
    p = random_points(num_variables, 1, 7)[0]
    formula, adjacency = float64_formula_and_adjacency(num_variables, clauses)
    assert adjacency.num_pairs == 0
    unsat = [np.prod([1 - np.sign(literal) * p[abs(literal) - 1] for literal in clause]) / 8 for clause in clauses]
    _, var = vectorised_moments(num_variables, clauses, p)
    assert var == pytest.approx(sum(u * (1 - u) for u in unsat), abs=1e-12)
    assert_matches_brute_force(num_variables, clauses, p)


@pytest.mark.parametrize("p", [np.full(6, -1.0), np.zeros(6), np.full(6, 1.0), np.array([1, -1, 0, 1, 0, -1.0])],
                         ids=["all_minus_one", "all_zero", "all_plus_one", "mixed_boundary"])
def test_boundary_points(p):
    _, num_variables, clauses = HAND_MADE[-1]
    assert_matches_brute_force(num_variables, clauses, p)
