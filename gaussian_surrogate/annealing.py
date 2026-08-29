"""Annealed importance sampling (Neal 2001) toward the tilted measure q_theta(x) exp(beta S(x)):
a ladder beta_k = beta k / K from the raw draws (exact at beta_0 = 0), one Metropolis proposal per
rung, a uniformly chosen variable accepted with min(1, exp(beta_k dS + theta_i dx_i)), which is
symmetric and leaves q_theta e^{beta_k S} invariant, and log weights
sum_k (beta_k - beta_{k-1}) S(x_{k-1}). Self-normalised, the weighted mean of the samples is a
consistent estimator of E_tilted[x]. A chain that passes through a satisfying assignment keeps
moving (freezing it there would bias the sampler toward solutions, measured at 0.4 RMS on n = 12);
the assignment is recorded on the side so the run can end on it."""
import torch


def anneal(kernel, state, theta_slots, beta_slots, num_rungs, generator, active):
    """Runs the ladder in place on the active slots; returns (log weights [B], found [B], the
    satisfying assignment [B, n] of every slot that found one on the way)."""
    num_slots, num_variables = state.assignment.shape
    log_weight = torch.zeros(num_slots, device=state.assignment.device)
    found, saved = torch.zeros(num_slots, dtype=torch.bool, device=log_weight.device), state.assignment.clone()
    for rung in range(1, num_rungs + 1):
        satisfied = (kernel.num_clauses - state.num_violated()).to(log_weight.dtype)
        hit = (satisfied == kernel.num_clauses) & active & ~found
        saved = torch.where(hit.unsqueeze(1), state.assignment, saved)
        found |= hit
        log_weight += beta_slots / num_rungs * satisfied
        variable = torch.randint(0, num_variables, (num_slots,), generator=generator, device=state.assignment.device)
        make, breaks = kernel.flip_effects(state, variable.unsqueeze(1))
        delta_satisfied = (make - breaks).squeeze(1).to(log_weight.dtype)
        current = state.assignment.gather(1, variable.unsqueeze(1)).squeeze(1)
        theta_of_variable = theta_slots.gather(1, variable.unsqueeze(1)).squeeze(1)
        log_acceptance = beta_slots * rung / num_rungs * delta_satisfied - 2.0 * theta_of_variable * current
        uniform = torch.rand(num_slots, generator=generator, device=state.assignment.device)
        kernel.apply_flips(state, variable, active & (uniform.log() < log_acceptance))
    return log_weight, found, saved
