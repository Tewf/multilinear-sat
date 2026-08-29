"""Exact quantities of the satisfied-clause count by enumerating {-1, 1}^n (n <= 16): its mean
and variance under independent means p, and the tilted measure q_theta(x) exp(beta S(x)) / Z."""
import itertools

import numpy as np


def satisfied_count(assignment, clauses):
    return sum(1 for clause in clauses
               if any(assignment[abs(literal) - 1] == (1 if literal > 0 else -1) for literal in clause))


def enumerate_cube(num_variables, clauses, p):
    """(X [2^n, n], q [2^n], S [2^n]): every assignment, its product-measure probability under
    means p, and its satisfied-clause count."""
    assert num_variables <= 16, "enumeration is meant for tiny formulas"
    points = np.array(list(itertools.product((1, -1), repeat=num_variables)), dtype=np.float64)
    probability = np.prod((1 + points * np.asarray(p, dtype=np.float64)) / 2, axis=1)
    literals = np.asarray(clauses)
    literal_true = points[:, np.abs(literals) - 1] * np.sign(literals) > 0            # [2^n, m, 3]
    return points, probability, literal_true.any(axis=-1).sum(axis=-1).astype(np.float64)


def exact_moments(num_variables, clauses, p):
    """(mean, variance) of the number of satisfied clauses when each x_i is +1 with
    probability (1 + p_i) / 2, independently."""
    _, probability, counts = enumerate_cube(num_variables, clauses, p)
    mean = float(probability @ counts)
    return mean, float(probability @ (counts * counts)) - mean * mean


def exact_covariance_with_count(num_variables, clauses, p):
    """Cov_p(x_i, S) for every i, which is d mu / d theta_i at p = tanh(theta)."""
    points, probability, counts = enumerate_cube(num_variables, clauses, p)
    return (probability * counts) @ (points - np.asarray(p, dtype=np.float64))


def exact_tilted_log_partition(num_variables, clauses, theta, beta):
    """log E_theta[exp(beta S)] with p = tanh(theta)."""
    _, probability, counts = enumerate_cube(num_variables, clauses, np.tanh(theta))
    return float(np.log(probability @ np.exp(beta * counts)))


def exact_tilted_weights(num_variables, clauses, theta, beta):
    """q_theta(x) exp(beta S(x)) / Z over the whole cube, and the cube itself."""
    points, probability, counts = enumerate_cube(num_variables, clauses, np.tanh(theta))
    weights = probability * np.exp(beta * counts)
    return points, weights / weights.sum()
