"""Bernoulli draws from product means, and the self-normalised tilted weights of every group
of samples with their effective sample size. Slots are consecutive: slot b is in group b // S."""
import torch


def draw_assignments(p, generator):
    """x in {-1, 1}^{B x n} with P(x_i = +1) = (1 + p_i) / 2 independently, one row per row of p."""
    uniform = torch.rand(p.shape, generator=generator, device=p.device)
    return torch.where(uniform < (1.0 + p) / 2.0, 1.0, -1.0)


def tilted_weights(satisfied_count, beta, num_groups):
    """w_b proportional to exp(beta S(x_b)), normalised within each group of S consecutive slots;
    beta is one value per group (or one scalar). Shape [G, S]."""
    scores = satisfied_count.view(num_groups, -1).to(torch.float32)
    beta = torch.as_tensor(beta, dtype=torch.float32, device=scores.device).reshape(-1, 1)
    return torch.softmax(scores * beta, dim=1)


def effective_sample_size(weights):
    """(sum w)^2 / sum w^2 per group: S when the weights are flat, 1 when one sample carries all."""
    return weights.sum(dim=1).square() / weights.square().sum(dim=1)
