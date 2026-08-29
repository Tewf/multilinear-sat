"""The tilted sampling-gradient loop (../method/sampling-gradient-loop.md): B slots in G groups
sharing one theta each. Per step: raw draws from q_theta, a move of each sample, importance
weights, the merged gradient, a step on theta, the beta schedule, Luby restarts per group, a
certificate check of every sample, and the trajectory log. The move is one of two (walk_mode):
`metropolis`, the annealed-importance-sampling ladder of annealing.py, whose weights make the
sampled tilted mean consistent; or `walk`, the SKC walk of the flip kernel with self-normalised
exp(beta S) weights, which are BIASED and labelled so wherever they are logged. A rigorous
fraction of the groups draws uniform starts and walks Schöning's rule for 3n flips instead; their
failures and the heuristic ones feed the two UNSAT posteriors.

On the Luby schedule: on hard random 3-SAT a well-tuned SLS has a memoryless run-length
distribution where no schedule helps (Hoos and Stützle 1999); the seeded walk's distribution is
unknown until measured, which the trajectory log records."""
import csv
import math
import time

import numpy as np
import torch

from annealing import anneal
from failure_record import FailureRecord
from flip_kernel import FlipKernel
from group_optimizers import build_optimizer
from luby import LubyRestarts
from sampling import draw_assignments, effective_sample_size, normalised_weights
from solver import SolveResult, certify_solution
from tilted_gradient import closed_form_gradient, merged_gradient, raw_draw_estimate, sampled_tilted_gradient

TRAJECTORY_COLUMNS = ["step", "restarts", "seconds", "beta", "ess", "mu", "saturated", "min_unsat",
                      "rigorous_failures", "heuristic_failures", "posterior_rigorous", "posterior_beta",
                      "weights_biased"]
SCHOENING_FLIPS_PER_VARIABLE = 3   # the walk length of Schöning's algorithm, part of its bound
WEIGHT_LABELS = {"metropolis": "annealed importance sampling, consistent",
                 "walk": "biased: self-normalised exp(beta S) after the SKC walk"}


class TiltedLoop:
    def __init__(self, formula, configuration, seed):
        self.formula, self.configuration = formula, configuration
        self.device = formula.variable_index.device
        self.generator = torch.Generator(device=self.device).manual_seed(seed)
        self.kernel = FlipKernel(formula)
        self.num_groups, self.slots_per_group = configuration.tilted_num_groups, configuration.tilted_slots_per_group
        num_rigorous = round(configuration.rigorous_fraction * self.num_groups)
        self.rigorous_group = torch.arange(self.num_groups, device=self.device) >= self.num_groups - num_rigorous
        self.rigorous_slot = self.rigorous_group.repeat_interleave(self.slots_per_group)
        self.walk_flips = round(configuration.tilted_walk_flips_per_variable * formula.num_variables)
        schoening_flips = SCHOENING_FLIPS_PER_VARIABLE * formula.num_variables
        self.rigorous_budget = torch.where(self.rigorous_slot, schoening_flips, 0)
        self.budget = torch.where(self.rigorous_slot, schoening_flips, self.walk_flips)
        self.theta = self.initial_theta(self.num_groups)
        self.beta = torch.full((self.num_groups,), configuration.beta_initial, device=self.device)
        self.optimizer = build_optimizer(configuration.tilted_optimizer, self.theta, configuration.tilted_learning_rate,
                                         configuration.tilted_learning_rate_half_life)
        self.restarts = LubyRestarts(self.num_groups, configuration.luby_unit_steps)
        self.failures = FailureRecord(formula.num_variables, configuration)

    def initial_theta(self, count):
        shape = (count, self.formula.num_variables)
        return (torch.rand(shape, generator=self.generator, device=self.device) * 2 - 1) * self.configuration.init_scale

    def draw_and_walk(self, p):
        """(raw draws, their satisfied counts, the moved state, log weights [B]): one sample per
        slot. Rigorous groups draw uniformly (p = 0) and walk Schöning's rule for 3n flips; the
        others anneal or walk according to walk_mode."""
        slots = self.slots_per_group
        raw = draw_assignments(p.repeat_interleave(slots, dim=0), self.generator)
        state = self.kernel.initialise(raw)
        raw_count = self.formula.num_clauses - state.num_violated()
        beta_slots, noise = self.beta.repeat_interleave(slots), self.configuration.walksat_noise
        if self.configuration.walk_mode == "metropolis":
            self.kernel.walk(state, int(self.rigorous_budget.max()), self.rigorous_slot, noise, self.generator,
                             self.rigorous_budget)
            log_weights, found, saved = anneal(self.kernel, state, self.theta.repeat_interleave(slots, dim=0),
                                               beta_slots, self.walk_flips, self.generator, ~self.rigorous_slot)
            if found.any():     # a solution seen on the way ends the run: put it back in its slot
                state = self.kernel.initialise(torch.where(found.unsqueeze(1), saved, state.assignment))
        else:
            self.kernel.walk(state, int(self.budget.max()), self.rigorous_slot, noise, self.generator, self.budget)
            log_weights = beta_slots * (self.formula.num_clauses - state.num_violated())
        return raw, raw_count, state, log_weights

    def update_theta(self, p, raw, raw_count, state, weights):
        """The merged gradient step on theta of the heuristic groups; returns mu(p) per group."""
        shape = (self.num_groups, self.slots_per_group, self.formula.num_variables)
        closed, mu = closed_form_gradient(self.theta, self.formula, self.beta)
        sampled = sampled_tilted_gradient(state.assignment.view(shape), weights, p)
        raw_estimate = raw_draw_estimate(raw.view(shape), raw_count.view(shape[:2]), p, self.beta, mu)
        gradient = merged_gradient(sampled, raw_estimate, closed, self.configuration.control_variate_coefficient)
        self.optimizer.step(gradient * (~self.rigorous_group).unsqueeze(1))
        return mu

    def schedule_and_restart(self, ess):
        """Raise beta where the ESS stays above the floor, hold elsewhere; reinitialise the groups
        whose Luby budget is spent."""
        configuration = self.configuration
        raised = (self.beta * configuration.beta_growth_factor).clamp(max=configuration.beta_max)
        self.beta = torch.where(ess >= configuration.ess_floor_fraction * self.slots_per_group, raised, self.beta)
        restarted = self.restarts.advance()
        if restarted:
            self.theta[restarted] = self.initial_theta(len(restarted))
            self.beta[restarted] = configuration.beta_initial
            self.optimizer.reset(restarted)

    def step(self):
        """One round over every slot: (min unsat after the walk, a satisfying assignment or None,
        the numbers of the log row: beta, ESS, mu, saturated means averaged over groups, then the
        failure counts and the two posteriors)."""
        p = torch.tanh(self.theta) * (~self.rigorous_group).unsqueeze(1)
        raw, raw_count, state, log_weights = self.draw_and_walk(p)
        violated = state.num_violated()
        weights = normalised_weights(log_weights, self.num_groups)
        ess = effective_sample_size(weights)
        mu = self.update_theta(p, raw, raw_count, state, weights)
        self.schedule_and_restart(ess)
        self.failures.count(violated, self.rigorous_slot)
        best = int(violated.argmin())
        min_unsat = int(violated[best])
        solution = [int(value) for value in state.assignment[best].tolist()] if min_unsat == 0 else None
        saturated = (p.abs() > self.configuration.saturation_threshold).sum(dim=1).float().mean().item()
        return min_unsat, solution, (self.beta.mean().item(), ess.mean().item(), mu.mean().item(), saturated)


def solve_tilted(formula, configuration, seed, trajectory_path=None):
    """The same contract as solver.solve: a SolveResult, the assignment certified in plain Python."""
    loop = TiltedLoop(formula, configuration, seed)
    weights_biased = int(configuration.walk_mode == "walk")
    trajectory, unsat_events, solution, num_steps = [], [], None, 0
    start = time.perf_counter()
    while solution is None and time.perf_counter() - start < configuration.time_limit_seconds:
        min_unsat, solution, numbers = loop.step()
        num_steps += 1
        unsat_events.append(min_unsat)
        if trajectory_path is not None:
            trajectory.append((num_steps, loop.restarts.num_restarts, round(time.perf_counter() - start, 4), *numbers,
                               min_unsat, loop.failures.rigorous_failures, loop.failures.heuristic_failures,
                               *loop.failures.posteriors(), weights_biased))
    certify_solution(formula, solution)
    if trajectory_path is not None:
        with open(trajectory_path, "w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(TRAJECTORY_COLUMNS)
            writer.writerows(trajectory)
    posterior_rigorous, posterior_beta = loop.failures.posteriors()
    return SolveResult(solution is not None, solution, time.perf_counter() - start, loop.restarts.num_restarts,
                       num_steps, min(unsat_events) if unsat_events else -1,
                       float(np.mean(unsat_events)) if unsat_events else math.nan, len(unsat_events),
                       loop.failures.rigorous_failures, loop.failures.heuristic_failures,
                       posterior_rigorous, posterior_beta, WEIGHT_LABELS[configuration.walk_mode])
