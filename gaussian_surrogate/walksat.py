"""A short WalkSAT/SKC polish of one +-1 assignment, in numpy, with incremental true-literal counts,
and the helper that applies it to the best rounded slots of a batch."""
import numpy as np
import torch


def build_occurrence_lists(variable_index, sign, num_variables):
    """For each variable: the clauses it occurs in and the sign of its literal there."""
    clause_of = np.repeat(np.arange(variable_index.shape[0]), 3)
    order = np.argsort(variable_index.ravel(), kind="stable")
    boundaries = np.cumsum(np.bincount(variable_index.ravel(), minlength=num_variables))[:-1]
    return np.split(clause_of[order], boundaries), np.split(sign.ravel()[order], boundaries)


def flip_variable(x, true_count, variable, occurrence_clauses, occurrence_signs):
    """Flip one variable in place and update the true-literal counts of the clauses it occurs in."""
    clauses, signs = occurrence_clauses[variable], occurrence_signs[variable]
    was_true = x[variable] * signs > 0
    x[variable] = -x[variable]
    true_count[clauses] += np.where(was_true, -1, 1)


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
        flip_variable(x, true_count, variable, occurrence_clauses, occurrence_signs)
    return x, int((true_count == 0).sum())


class BestSlotPolisher:
    """Holds what WalkSAT needs about the formula, and polishes the best rounded slots."""

    def __init__(self, formula, configuration, seed):
        self.variable_index = formula.variable_index.cpu().numpy()
        self.sign = formula.sign.cpu().numpy()
        self.occurrence_clauses, self.occurrence_signs = build_occurrence_lists(
            self.variable_index, self.sign, formula.num_variables)
        self.max_flips = configuration.walksat_flips_per_variable * formula.num_variables
        self.noise = configuration.walksat_noise
        self.top_slots = configuration.polish_top_slots
        self.rng = np.random.default_rng(seed)

    def __call__(self, assignment, unsat):
        """The first satisfying assignment among the best slots, polished if needed, else None."""
        for slot in torch.argsort(unsat)[: self.top_slots].tolist():
            x, remaining = assignment[slot].cpu().numpy(), int(unsat[slot])
            if remaining > 0:
                x, remaining = walksat_polish(x, self.variable_index, self.sign, self.occurrence_clauses,
                                              self.occurrence_signs, self.max_flips, self.noise, self.rng)
            if remaining == 0:
                return [int(value) for value in x]
        return None
