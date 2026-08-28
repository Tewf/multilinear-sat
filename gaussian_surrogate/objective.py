"""The Gaussian surrogate of P(all clauses satisfied), in log form, and the value record that
every objective hands to the solver."""
from dataclasses import dataclass

import torch

from moments import expected_satisfied, pair_unsat_probability, unsat_probability, variance


@dataclass
class ObjectiveValue:
    ascent_target: torch.Tensor    # [B] what gradient ascent maximises
    log_probability: torch.Tensor  # [B] log F, the Gaussian surrogate, logged for every objective
    mu: torch.Tensor               # [B] expected number of satisfied clauses
    var: torch.Tensor              # [B] its variance

    @property
    def probability(self):
        return self.log_probability.exp()


def surrogate_moments(p, formula, adjacency, variance_floor):
    """(log F, mu, var) with F = Phi((mu - m + 1/2) / sqrt(max(var, floor))): the probability that a
    Gaussian with the exact mean and variance of the satisfied-clause count reaches m."""
    unsat = unsat_probability(p, formula)
    mu = expected_satisfied(unsat, formula.num_clauses)
    var = variance(unsat, pair_unsat_probability(p, adjacency), adjacency)
    z = (mu - formula.num_clauses + 0.5) / var.clamp(min=variance_floor).sqrt()
    return torch.special.log_ndtr(z), mu, var


def gaussian_surrogate(p, formula, adjacency, variance_floor, with_diagnostics=True):
    """Objective F: the ascent target is log F itself, so the diagnostics come for free."""
    log_probability, mu, var = surrogate_moments(p, formula, adjacency, variance_floor)
    return ObjectiveValue(log_probability, log_probability, mu, var)
