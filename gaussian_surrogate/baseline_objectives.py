"""The baseline objective: the expected number of satisfied clauses, which is FourierSAT's
multilinear energy up to an affine map. Which relaxation it runs on is decided in methods.py."""
import torch

from moments import expected_satisfied, unsat_probability
from objective import ObjectiveValue, surrogate_moments


def expected_satisfied_objective(p, formula, adjacency, variance_floor, with_diagnostics=False):
    """mu(p) = m - sum_j U_j. The Gaussian surrogate is evaluated without gradient, and only when
    a trajectory is being logged, so a baseline step costs what its own objective costs."""
    mu = expected_satisfied(unsat_probability(p, formula), formula.num_clauses)
    if not with_diagnostics:
        undefined = torch.full_like(mu, float("nan"))
        return ObjectiveValue(mu, undefined, mu, undefined)
    with torch.no_grad():
        log_probability, _, var = surrogate_moments(p, formula, adjacency, variance_floor)
    return ObjectiveValue(mu, log_probability, mu, var)
