"""The rigorous bound against the exact hitting probability of Schöning's dominated chain, both
posteriors' formulas and monotonicity, the Beta marginal against quadrature, the moment fit."""
import math

import numpy as np
import pytest

from posterior import (beta_mixture_log_likelihood, beta_mixture_posterior, fit_beta_by_moments,
                       rigorous_posterior, schoening_polynomial_factor, schoening_success_bound)


def dominated_chain_success_probability(num_variables):
    """Uniform start, then 3n steps of a chain moving one closer to the solution with probability
    1/3 and one further with probability 2/3, never reflected (a lower bound on the real walk)."""
    steps = 3 * num_variables
    distribution = np.array([math.comb(num_variables, j) / 2 ** num_variables for j in range(num_variables + 1)]
                            + [0.0] * steps)
    absorbed = distribution[0]
    distribution[0] = 0.0
    for _ in range(steps):
        moved = np.zeros_like(distribution)
        moved[:-1] += distribution[1:] / 3          # one step closer
        moved[1:] += distribution[:-1] * 2 / 3      # one step further
        absorbed += moved[0]
        moved[0] = 0.0
        distribution = moved
    return absorbed


@pytest.mark.parametrize("num_variables", [1, 2, 3, 5, 8, 13, 20, 30])
def test_schoening_bound_is_below_the_dominated_chain(num_variables):
    exact = dominated_chain_success_probability(num_variables)
    assert 0 < schoening_success_bound(num_variables) <= exact
    assert schoening_polynomial_factor(num_variables) == 9 * num_variables + 3


def test_rigorous_posterior_formula_and_monotonicity():
    bound = (27 / 64) / 30                                        # n = 3: (3/4)^3 / (3 (3 * 3 + 1))
    expected = 0.5 / (0.5 + 0.5 * (1 - bound) ** 2)
    assert rigorous_posterior(3, 2, 0.5) == pytest.approx(expected, rel=1e-12)
    assert rigorous_posterior(3, 0, 0.3) == pytest.approx(0.7)
    values = [rigorous_posterior(10, failures, 0.5) for failures in (0, 1, 10, 100, 10000)]
    assert all(later > earlier for earlier, later in zip(values, values[1:]))
    assert rigorous_posterior(250, 10 ** 6, 0.5) == pytest.approx(0.5)   # the bound is 2.7e-35 per try


def test_beta_mixture_special_cases_and_monotonicity():
    for failures in (0, 1, 7, 100):
        assert math.exp(beta_mixture_log_likelihood(failures, 1.0, 1.0)) == pytest.approx(1 / (failures + 1))
    assert beta_mixture_posterior(0, 2.0, 5.0, 0.4) == pytest.approx(0.6)
    assert beta_mixture_posterior(3, 1.0, 1.0, 0.5) == pytest.approx(1 / (1 + 1 / 4))
    values = [beta_mixture_posterior(failures, 2.0, 30.0, 0.5) for failures in (0, 1, 5, 20, 100, 1000)]
    assert all(later > earlier for earlier, later in zip(values, values[1:]))
    assert values[-1] < 1.0


def test_beta_marginal_likelihood_matches_quadrature():
    a, b, failures = 2.5, 6.0, 9
    p = np.linspace(0.0, 1.0, 200001)
    density = p ** (a - 1) * (1 - p) ** (b - 1)
    expected = np.trapezoid(density * (1 - p) ** failures, p) / np.trapezoid(density, p)
    assert math.exp(beta_mixture_log_likelihood(failures, a, b)) == pytest.approx(expected, rel=1e-6)


def test_fit_beta_by_moments_recovers_synthetic_parameters():
    samples = np.random.default_rng(0).beta(2.0, 8.0, size=40000).tolist()
    a, b = fit_beta_by_moments(samples)
    assert a == pytest.approx(2.0, rel=0.05) and b == pytest.approx(8.0, rel=0.05)
    with pytest.raises(ValueError):
        fit_beta_by_moments([0.0, 0.0, 0.0])
