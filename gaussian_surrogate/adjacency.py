"""The clause pairs that share a variable, precomputed once and laid out so that U_jk is one
batched product: six (variable, sign) slots per pair and one scalar per pair."""
from dataclasses import dataclass

import numpy as np
import torch


@dataclass
class ClauseAdjacency:
    pair_index: torch.Tensor     # [P, 2] clause indices j < k
    slot_variable: torch.Tensor  # [P, 6] variable of each factor (0 for a padded slot)
    slot_sign: torch.Tensor      # [P, 6] literal sign; 0 for a padded slot, whose factor is 1
    pair_scale: torch.Tensor     # [P] 2^(shared same-sign variables) / 64, or 0 when a shared
                                 #     variable has opposite signs (both clauses cannot be unsat)

    @property
    def num_pairs(self):
        return self.pair_index.shape[0]

    def to(self, device):
        return ClauseAdjacency(self.pair_index.to(device), self.slot_variable.to(device),
                               self.slot_sign.to(device), self.pair_scale.to(device))


def _pairs_sharing_a_variable(variable_index):
    """All unordered clause pairs (j < k) with a variable in common, as int arrays J, K."""
    num_clauses = variable_index.shape[0]
    clause_of = np.repeat(np.arange(num_clauses), 3)
    order = np.argsort(variable_index.ravel(), kind="stable")
    boundaries = np.flatnonzero(np.diff(variable_index.ravel()[order])) + 1
    keys = []
    for group in np.split(clause_of[order], boundaries):
        if group.size > 1:
            group = np.sort(group)
            first, second = np.triu_indices(group.size, 1)
            keys.append(group[first] * num_clauses + group[second])
    unique_keys = np.unique(np.concatenate(keys)) if keys else np.zeros(0, dtype=np.int64)
    return unique_keys // num_clauses, unique_keys % num_clauses


def build_clause_adjacency(formula):
    variable_index = formula.variable_index.cpu().numpy()
    sign = formula.sign.cpu().numpy()
    first, second = _pairs_sharing_a_variable(variable_index)
    variables_j, signs_j = variable_index[first], sign[first]
    variables_k, signs_k = variable_index[second], sign[second]
    same_variable = variables_j[:, :, None] == variables_k[:, None, :]       # [P, 3, 3]
    sign_product = signs_j[:, :, None] * signs_k[:, None, :]
    shared_same_sign = (same_variable & (sign_product > 0)).sum(axis=(1, 2))
    shared_opposite_sign = (same_variable & (sign_product < 0)).any(axis=(1, 2))
    pair_scale = np.where(shared_opposite_sign, 0.0, 2.0 ** shared_same_sign / 64.0)
    slot_of_k_is_shared = same_variable.any(axis=1)                            # [P, 3]
    slot_variable = np.concatenate([variables_j, np.where(slot_of_k_is_shared, 0, variables_k)], axis=1)
    slot_sign = np.concatenate([signs_j, np.where(slot_of_k_is_shared, 0.0, signs_k)], axis=1)
    return ClauseAdjacency(
        torch.from_numpy(np.stack([first, second], axis=1).astype(np.int64)),
        torch.from_numpy(slot_variable.astype(np.int64)),
        torch.from_numpy(slot_sign.astype(np.float32)),
        torch.from_numpy(pair_scale.astype(np.float32)))
