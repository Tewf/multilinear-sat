"""Random 3-SAT instances for the tests: uniform, and with a planted satisfying assignment."""
import numpy as np


def random_3sat(num_variables, num_clauses, seed):
    rng = np.random.default_rng(seed)
    clauses = []
    while len(clauses) < num_clauses:
        variables = rng.choice(num_variables, size=3, replace=False) + 1
        signs = rng.choice([-1, 1], size=3)
        clauses.append([int(variable * sign) for variable, sign in zip(variables, signs)])
    return clauses


def planted_3sat(num_variables, num_clauses, seed):
    """Clauses drawn uniformly among those satisfied by a random planted assignment (+-1 array)."""
    rng = np.random.default_rng(seed)
    planted = rng.choice([-1, 1], size=num_variables)
    clauses = []
    while len(clauses) < num_clauses:
        variables = rng.choice(num_variables, size=3, replace=False)
        signs = rng.choice([-1, 1], size=3)
        if any(planted[variable] == sign for variable, sign in zip(variables, signs)):
            clauses.append([int((variable + 1) * sign) for variable, sign in zip(variables, signs)])
    return clauses, planted
