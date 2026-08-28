"""The Gaussian surrogate of P(all clauses satisfied), returned in log form for the ascent."""
from dataclasses import dataclass

import torch

from moments import expected_satisfied, pair_unsat_probability, unsat_probability, variance


@dataclass
class ObjectiveValue:
    log_probability: torch.Tensor  # [B] what gradient ascent maximises
    mu: torch.Tensor               # [B] expected number of satisfied clauses
    var: torch.Tensor              # [B] its variance

    @property
    def probability(self):
        return self.log_probability.exp()


def gaussian_surrogate(p, formula, adjacency, variance_floor):
    """log F(p) with F = Phi((mu - m + 1/2) / sqrt(max(var, floor))): the probability that a
    Gaussian with the exact mean and variance of the satisfied-clause count reaches m."""
    unsat = unsat_probability(p, formula)
    mu = expected_satisfied(unsat, formula.num_clauses)
    var = variance(unsat, pair_unsat_probability(p, adjacency), adjacency)
    z = (mu - formula.num_clauses + 0.5) / var.clamp(min=variance_floor).sqrt()
    return ObjectiveValue(torch.special.log_ndtr(z), mu, var)
