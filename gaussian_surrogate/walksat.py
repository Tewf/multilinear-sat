"""A short WalkSAT/SKC polish of one +-1 assignment, in numpy, with incremental true-literal counts."""
import numpy as np


def build_occurrence_lists(variable_index, sign, num_variables):
    """For each variable: the clauses it occurs in and the sign of its literal there."""
    clause_of = np.repeat(np.arange(variable_index.shape[0]), 3)
    order = np.argsort(variable_index.ravel(), kind="stable")
    boundaries = np.cumsum(np.bincount(variable_index.ravel(), minlength=num_variables))[:-1]
    return np.split(clause_of[order], boundaries), np.split(sign.ravel()[order], boundaries)


def walksat_polish(assignment, variable_index, sign, occurrence_clauses, occurrence_signs,
                   max_flips, noise, rng):
    """Flip until every clause is satisfied or the budget is spent; returns (assignment, num_unsat)."""
    x = assignment.copy()
    true_count = (x[variable_index] * sign > 0).sum(axis=1)

    def break_count(variable):
        clauses, signs = occurrence_clauses[variable], occurrence_signs[variable]
        return int(((true_count[clauses] == 1) & (x[variable] * signs > 0)).sum())

    for _ in range(max_flips):
        unsatisfied = np.flatnonzero(true_count == 0)
        if unsatisfied.size == 0:
            break
        candidates = variable_index[unsatisfied[rng.integers(unsatisfied.size)]]
        break_counts = np.array([break_count(variable) for variable in candidates])
        if break_counts.min() > 0 and rng.random() < noise:
            variable = candidates[rng.integers(candidates.size)]
        else:
            variable = candidates[break_counts.argmin()]
        clauses, signs = occurrence_clauses[variable], occurrence_signs[variable]
        was_true = x[variable] * signs > 0
        x[variable] = -x[variable]
        true_count[clauses] += np.where(was_true, -1, 1)
    return x, int((true_count == 0).sum())
