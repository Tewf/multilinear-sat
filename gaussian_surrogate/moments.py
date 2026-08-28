"""The first two moments of the number of unsatisfied clauses when the variables are
independent with means p in (-1, 1)^n, batched over B points."""


def literal_false_factors(p, variable_index, sign):
    """(1 - sign * p[variable]) for every slot; a slot with sign 0 contributes the factor 1."""
    return 1.0 - sign * p[:, variable_index]


def unsat_probability(p, formula):
    """U_j(p) = P(clause j unsatisfied) = (1/8) prod (1 - s p_i), shape [B, m]."""
    return literal_false_factors(p, formula.variable_index, formula.sign).prod(dim=-1) / 8.0


def pair_unsat_probability(p, adjacency):
    """U_jk(p) = P(clauses j and k both unsatisfied) for every pair sharing a variable, [B, P]."""
    factors = literal_false_factors(p, adjacency.slot_variable, adjacency.slot_sign)
    return adjacency.pair_scale * factors.prod(dim=-1)


def expected_satisfied(unsat, num_clauses):
    """mu(p) = m - sum_j U_j, shape [B]."""
    return num_clauses - unsat.sum(dim=-1)


def variance(unsat, pair_unsat, adjacency):
    """var(p) = sum_j U_j (1 - U_j) + 2 sum_{j<k sharing} (U_jk - U_j U_k), shape [B].
    Pairs sharing no variable are independent and contribute 0; the factor 2 turns the
    sum over unordered pairs into the sum over ordered pairs."""
    first, second = adjacency.pair_index[:, 0], adjacency.pair_index[:, 1]
    covariance = pair_unsat - unsat[:, first] * unsat[:, second]
    return (unsat * (1.0 - unsat)).sum(dim=-1) + 2.0 * covariance.sum(dim=-1)
