"""The ascent direction of the tilted objective log E_theta[exp(beta S)] in theta coordinates
(method/sampling-gradient-loop.md): the weighted mean of the annealed samples minus p, corrected
by a control variate whose expectation under the raw draws is the closed form beta d mu / d theta."""
import torch

from moments import expected_satisfied, unsat_probability


def closed_form_gradient(theta, formula, beta):
    """(beta * d mu / d theta, mu) at p = tanh(theta), by autograd through moments.py; [G, n], [G].
    Since d log q / d theta_i = x_i - p_i the gradient equals beta Cov_p(x, S), the beta -> 0 limit."""
    theta = theta.detach().requires_grad_(True)
    mu = expected_satisfied(unsat_probability(torch.tanh(theta), formula), formula.num_clauses)
    (gradient,) = torch.autograd.grad(mu.sum(), theta)
    return torch.as_tensor(beta, dtype=theta.dtype, device=theta.device).reshape(-1, 1) * gradient, mu.detach()


def sampled_tilted_gradient(annealed, weights, p):
    """g_hat = sum_b w_b (x_b - p) per group: annealed [G, S, n], normalised weights [G, S], p [G, n]."""
    return (weights.unsqueeze(-1) * (annealed - p.unsqueeze(1))).sum(dim=1)


def raw_draw_estimate(raw, satisfied_count, p, beta, centre):
    """h_hat = (1/S) sum_b (x0_b - p) beta (S(x0_b) - centre) per group, raw [G, S, n],
    satisfied_count [G, S], centre [G]: the score-function estimator of the first-order Taylor
    surrogate of exp(beta S) about p, whose expectation under the product measure is the closed
    form (MuProp's mean-field control variate: Gu, Levine, Sutskever, Mnih, ICLR 2016). The
    expectation is beta Cov(x, S) whatever the centre, because E[x0 - p] = 0; the centre mu(p)
    removes the variance proportional to mu^2 that the uncentred count would carry."""
    beta = torch.as_tensor(beta, dtype=raw.dtype, device=raw.device).reshape(-1, 1, 1)
    scores = beta * (satisfied_count.to(raw.dtype) - centre.reshape(-1, 1)).unsqueeze(-1)
    return ((raw - p.unsqueeze(1)) * scores).mean(dim=1)


def merged_gradient(sampled, raw_estimate, closed_form, control_variate_coefficient):
    """g = g_hat - lambda (h_hat - g_closed): the correction has mean zero and cancels the part of
    the sampling noise that the raw draws share with the annealed samples."""
    return sampled - control_variate_coefficient * (raw_estimate - closed_form)
