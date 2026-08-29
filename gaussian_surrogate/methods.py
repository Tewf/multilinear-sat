"""The methods by name: the gradient methods (which objective is maximised, on which relaxation)
and the sampling loop, which brings its own scaffolding."""
from functools import partial

from baseline_objectives import expected_satisfied_objective
from objective import gaussian_surrogate
from relaxation import BoxRelaxation, TanhRelaxation
from tilted_loop import solve_tilted

METHODS = {
    "F": (gaussian_surrogate, TanhRelaxation),               # Gaussian surrogate, p = tanh(theta)
    "mu": (expected_satisfied_objective, TanhRelaxation),    # expected satisfied clauses, p = tanh(theta)
    "fourier": (expected_satisfied_objective, BoxRelaxation),  # the same energy, x on the box, clipped
}

SAMPLING_METHODS = {
    "tilted": solve_tilted,   # the tilted sampling-gradient loop: solve(formula, configuration, seed, trajectory)
}


def build_method(name, formula, adjacency, variance_floor):
    """(objective(p, with_diagnostics) -> ObjectiveValue, relaxation instance) for a method name."""
    objective, relaxation = METHODS[name]
    return partial(objective, formula=formula, adjacency=adjacency, variance_floor=variance_floor), relaxation()
