"""A local-search walk vectorised over slots and sequential over flips. Each slot holds a +-1
assignment and the count of true literals per clause, kept current by scatter updates over
padded occurrence lists; one flip per active slot per iteration. The variable is chosen by the
WalkSAT/SKC rule of walksat.py or, per slot, uniformly in the clause (Schöning)."""
from dataclasses import dataclass

import numpy as np
import torch

from walksat import build_occurrence_lists

SYNC_INTERVAL = 16   # iterations between checks that some slot is still active (a device sync)


@dataclass
class WalkState:
    assignment: torch.Tensor   # [B, n] of +-1.0
    true_count: torch.Tensor   # [B, m] true literals per clause, int64

    @property
    def violated(self):
        return self.true_count == 0

    def num_violated(self):
        return self.violated.sum(dim=1)


def padded_occurrence_lists(formula):
    """[n, D] clause indices and literal signs per variable, padded with clause 0 and sign 0."""
    clauses, signs = build_occurrence_lists(formula.variable_index.cpu().numpy(), formula.sign.cpu().numpy(),
                                            formula.num_variables)
    width = max(len(row) for row in clauses)
    clause_table = np.zeros((formula.num_variables, width), dtype=np.int64)
    sign_table = np.zeros((formula.num_variables, width), dtype=np.float32)
    for variable, (row_clauses, row_signs) in enumerate(zip(clauses, signs)):
        clause_table[variable, : len(row_clauses)] = row_clauses
        sign_table[variable, : len(row_signs)] = row_signs
    device = formula.variable_index.device
    return torch.from_numpy(clause_table).to(device), torch.from_numpy(sign_table).to(device)


class FlipKernel:
    def __init__(self, formula):
        self.variable_index, self.sign = formula.variable_index, formula.sign
        self.num_clauses = formula.num_clauses
        self.occurrence_clause, self.occurrence_sign = padded_occurrence_lists(formula)

    def initialise(self, assignment):
        """A state from +-1 assignments [B, n], its counts computed from scratch."""
        true_count = (assignment[:, self.variable_index] * self.sign > 0).sum(dim=-1)
        return WalkState(assignment.clone(), true_count)

    def choose_violated_clause(self, state, generator):
        """(clause [B], active [B]): a violated clause chosen uniformly per slot; a slot with none
        is inactive and gets the last clause index, to be ignored."""
        violated = state.violated
        count = violated.sum(dim=1)
        target = (torch.rand(count.shape, generator=generator, device=count.device) * count).long()
        clause = (violated.cumsum(dim=1) <= target.unsqueeze(1)).sum(dim=1)
        return clause.clamp(max=self.num_clauses - 1), count > 0

    def flip_effects(self, state, variables):
        """(make, break) for variables [B, k]: the clauses each flip would satisfy (its literal false
        in a violated clause) and violate (its literal the only true one)."""
        clauses, signs = self.occurrence_clause[variables], self.occurrence_sign[variables]   # [B, k, D]
        num_slots, k, width = clauses.shape
        true_count = state.true_count.gather(1, clauses.view(num_slots, k * width)).view(num_slots, k, width)
        literal_true = state.assignment.gather(1, variables).unsqueeze(-1) * signs > 0
        make = ((true_count == 0) & ~literal_true & (signs != 0)).sum(dim=-1)
        return make, ((true_count == 1) & literal_true).sum(dim=-1)

    def break_counts(self, state, variables):
        return self.flip_effects(state, variables)[1]

    def choose_variable(self, state, clause, uniform_choice, noise, generator):
        """The variable to flip in each slot's chosen clause: uniform where uniform_choice [B] holds
        (Schöning), else zero-break if any, else a random one with probability noise, else the
        first minimum break (the SKC rule of walksat.py)."""
        candidates = self.variable_index[clause]                                          # [B, 3]
        breaks = self.break_counts(state, candidates)
        random_index = torch.randint(0, 3, clause.shape, generator=generator, device=clause.device)
        take_random = (breaks.min(dim=1).values > 0) & \
            (torch.rand(clause.shape, generator=generator, device=clause.device) < noise)
        index = torch.where(uniform_choice | take_random, random_index, breaks.argmin(dim=1))
        return candidates.gather(1, index.unsqueeze(1)).squeeze(1)

    def apply_flips(self, state, variables, active):
        """Flip variables [B] in the active slots and update their true-literal counts in place."""
        clauses, signs = self.occurrence_clause[variables], self.occurrence_sign[variables]   # [B, D]
        current = state.assignment.gather(1, variables.unsqueeze(1))
        delta = torch.where(current * signs > 0, -1, 1) * (signs != 0) * active.unsqueeze(1)
        state.true_count.scatter_add_(1, clauses, delta)
        state.assignment.scatter_(1, variables.unsqueeze(1), current * torch.where(active, -1.0, 1.0).unsqueeze(1))

    def walk(self, state, num_iterations, uniform_choice, noise, generator, budget=None):
        """One flip per slot per iteration until the slot satisfies every clause or its budget
        [B] (default num_iterations) is spent; returns the flips done per slot."""
        flips_done = torch.zeros(state.assignment.shape[0], dtype=torch.int64, device=state.assignment.device)
        for iteration in range(num_iterations):
            clause, active = self.choose_violated_clause(state, generator)
            if budget is not None:
                active &= flips_done < budget
            if iteration % SYNC_INTERVAL == 0 and not active.any():
                break
            variable = self.choose_variable(state, clause, uniform_choice, noise, generator)
            self.apply_flips(state, variable, active)
            flips_done += active
        return flips_done
