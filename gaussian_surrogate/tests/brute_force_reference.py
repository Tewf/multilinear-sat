"""Exact mean and variance of the satisfied-clause count by enumerating {-1, 1}^n (n <= 10)."""
import itertools

import numpy as np


def satisfied_count(assignment, clauses):
    return sum(1 for clause in clauses
               if any(assignment[abs(literal) - 1] == (1 if literal > 0 else -1) for literal in clause))


def exact_moments(num_variables, clauses, p):
    """(mean, variance) of the number of satisfied clauses when each x_i is +1 with
    probability (1 + p_i) / 2, independently."""
    assert num_variables <= 10, "enumeration is meant for tiny formulas"
    mean = second_moment = 0.0
    for assignment in itertools.product((1, -1), repeat=num_variables):
        weight = np.prod([(1 + x * p_i) / 2 for x, p_i in zip(assignment, p)])
        count = satisfied_count(assignment, clauses)
        mean += weight * count
        second_moment += weight * count * count
    return mean, second_moment - mean * mean
