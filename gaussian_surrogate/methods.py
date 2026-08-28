"""The three methods by name: which objective is maximised, on which relaxation."""
from functools import partial

from baseline_objectives import expected_satisfied_objective
from objective import gaussian_surrogate
from relaxation import BoxRelaxation, TanhRelaxation

METHODS = {
    "F": (gaussian_surrogate, TanhRelaxation),               # Gaussian surrogate, p = tanh(theta)
    "mu": (expected_satisfied_objective, TanhRelaxation),    # expected satisfied clauses, p = tanh(theta)
    "fourier": (expected_satisfied_objective, BoxRelaxation),  # the same energy, x on the box, clipped
}


def build_method(name, formula, adjacency, variance_floor):
    """(objective(p, with_diagnostics) -> ObjectiveValue, relaxation instance) for a method name."""
    objective, relaxation = METHODS[name]
    return partial(objective, formula=formula, adjacency=adjacency, variance_floor=variance_floor), relaxation()
