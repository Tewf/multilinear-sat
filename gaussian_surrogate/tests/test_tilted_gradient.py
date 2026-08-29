"""The tilted gradient against enumeration of {-1, 1}^n: the closed form is beta Cov(x, S), the raw
draw estimate has that expectation, the exactly weighted sampled gradient is the derivative of
log E[exp(beta S)] by finite differences, and beta -> 0 recovers d mu / d theta."""
import numpy as np
import pytest
import torch

from brute_force_reference import (exact_covariance_with_count, exact_moments, exact_tilted_log_partition,
                                   exact_tilted_weights)
from dimacs import Formula, formula_from_clauses
from random_instances import random_3sat
from sampling import draw_assignments
from tilted_gradient import closed_form_gradient, merged_gradient, raw_draw_estimate, sampled_tilted_gradient

NUM_VARIABLES, NUM_CLAUSES, BETA = 7, 20, 0.3


def problem(seed):
    clauses = random_3sat(NUM_VARIABLES, NUM_CLAUSES, seed)
    formula = formula_from_clauses(NUM_VARIABLES, clauses)
    formula = Formula(NUM_VARIABLES, formula.clauses, formula.variable_index, formula.sign.double())
    theta = np.random.default_rng(seed).uniform(-1.0, 1.0, size=NUM_VARIABLES)
    return clauses, formula, torch.tensor(theta, dtype=torch.float64).reshape(1, -1)


@pytest.mark.parametrize("seed", [0, 1])
def test_closed_form_is_beta_times_the_covariance_with_the_count(seed):
    clauses, formula, theta = problem(seed)
    expected = BETA * exact_covariance_with_count(NUM_VARIABLES, clauses, np.tanh(theta[0].numpy()))
    gradient, mu = closed_form_gradient(theta, formula, BETA)
    assert gradient[0].numpy() == pytest.approx(expected, abs=1e-9)
    assert mu.item() == pytest.approx(exact_moments(NUM_VARIABLES, clauses, np.tanh(theta[0].numpy()))[0], abs=1e-9)


def test_raw_draw_estimate_has_the_closed_form_expectation():
    clauses, formula, theta = problem(2)
    p = torch.tanh(theta)
    num_draws = 200000
    raw = draw_assignments(p.expand(num_draws, -1), torch.Generator().manual_seed(2)).double()
    counts = (raw[:, formula.variable_index] * formula.sign > 0).any(dim=-1).sum(dim=-1)
    for centre in (torch.zeros(1, dtype=torch.float64), torch.tensor([float(counts.double().mean())])):
        terms = (raw - p) * (BETA * (counts.double() - centre)).unsqueeze(1)
        estimate = raw_draw_estimate(raw.unsqueeze(0), counts.unsqueeze(0), p, BETA, centre)[0]
        assert torch.allclose(estimate, terms.mean(dim=0))
        standard_error = terms.std(dim=0) / num_draws ** 0.5
        assert torch.all((estimate - closed_form_gradient(theta, formula, BETA)[0][0]).abs() < 4 * standard_error + 1e-4)


@pytest.mark.parametrize("seed", [0, 3])
def test_exactly_weighted_sampled_gradient_is_the_derivative_of_the_log_partition(seed):
    clauses, formula, theta = problem(seed)
    points, weights = exact_tilted_weights(NUM_VARIABLES, clauses, theta[0].numpy(), BETA)
    sampled = sampled_tilted_gradient(torch.tensor(points).unsqueeze(0), torch.tensor(weights).unsqueeze(0),
                                      torch.tanh(theta))[0].numpy()
    step, finite_differences = 1e-5, np.zeros(NUM_VARIABLES)
    for i in range(NUM_VARIABLES):
        shift = np.eye(NUM_VARIABLES)[i] * step
        finite_differences[i] = (exact_tilted_log_partition(NUM_VARIABLES, clauses, theta[0].numpy() + shift, BETA)
                                 - exact_tilted_log_partition(NUM_VARIABLES, clauses, theta[0].numpy() - shift, BETA)) / (2 * step)
    assert sampled == pytest.approx(finite_differences, abs=1e-6)


def test_small_beta_recovers_the_mean_field_gradient():
    clauses, formula, theta = problem(4)
    small_beta = 1e-4
    points, weights = exact_tilted_weights(NUM_VARIABLES, clauses, theta[0].numpy(), small_beta)
    tilted_mean_minus_p = weights @ points - np.tanh(theta[0].numpy())
    mean_field = closed_form_gradient(theta, formula, 1.0)[0][0].numpy()
    assert tilted_mean_minus_p / small_beta == pytest.approx(mean_field, rel=1e-2, abs=1e-4)


def test_merged_gradient_algebra():
    sampled, raw_estimate, closed = torch.tensor([[1.0, 2.0]]), torch.tensor([[0.5, 0.5]]), torch.tensor([[0.25, 1.0]])
    assert torch.equal(merged_gradient(sampled, raw_estimate, closed, 0.0), sampled)
    assert torch.equal(merged_gradient(sampled, closed, closed, 1.0), sampled)
    assert torch.allclose(merged_gradient(sampled, raw_estimate, closed, 1.0), torch.tensor([[0.75, 2.5]]))
