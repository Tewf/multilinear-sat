"""From a relaxed point to a +-1 assignment, and how many clauses that assignment violates."""
import torch


def round_to_assignment(p):
    """sign(p) with ties sent to +1, shape [B, n] of +-1.0."""
    return torch.where(p >= 0, 1.0, -1.0)


def count_unsatisfied(assignment, formula):
    """Number of clauses with no true literal under each row of assignment, shape [B]."""
    literal_true = assignment[:, formula.variable_index] * formula.sign > 0   # [B, m, 3]
    return (~literal_true.any(dim=-1)).sum(dim=-1)


def count_unsatisfied_python(clauses, assignment):
    """Independent check in plain Python: clauses as lists of DIMACS literals, assignment as a
    sequence of +-1 indexed from variable 1 at position 0."""
    return sum(1 for clause in clauses
               if not any(assignment[abs(literal) - 1] == (1 if literal > 0 else -1)
                          for literal in clause))
