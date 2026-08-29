"""The annealed move against enumeration (n = 12): its weighted mean is consistent where the
walk's is biased, one rung reduces to plain importance sampling, and solutions met on the way are
recorded. Thresholds come from experiments/tilted_mean_bias.md (metropolis 0.033 and walk 0.22 RMS
at beta 2, 4n moves, S = 4096)."""
import sys
from pathlib import Path

import numpy as np
import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from annealing import anneal                                                  # noqa: E402
from brute_force_reference import exact_tilted_weights                        # noqa: E402
from dimacs import formula_from_clauses                                       # noqa: E402
from flip_kernel import FlipKernel                                            # noqa: E402
from random_instances import planted_3sat, random_3sat                        # noqa: E402
from rounding import count_unsatisfied                                        # noqa: E402
from sampling import draw_assignments                                         # noqa: E402
from tilted_mean_bias import NUM_CLAUSES, NUM_VARIABLES, sampled_tilted_mean  # noqa: E402


def small_problem():
    clauses = random_3sat(NUM_VARIABLES, NUM_CLAUSES, 0)
    formula = formula_from_clauses(NUM_VARIABLES, clauses)
    theta = torch.tensor(np.random.default_rng(0).uniform(-0.5, 0.5, NUM_VARIABLES), dtype=torch.float32)
    return clauses, formula, FlipKernel(formula), theta.reshape(1, -1)


def test_annealed_mean_is_consistent_and_the_walked_mean_is_not():
    clauses, formula, kernel, theta = small_problem()
    beta, moves, num_samples = 2.0, 4 * NUM_VARIABLES, 4096
    points, weights = exact_tilted_weights(NUM_VARIABLES, clauses, theta[0].double().numpy(), beta)
    exact = torch.tensor(weights @ points, dtype=torch.float32)
    errors = {}
    for mode in ("metropolis", "walk"):
        estimate, _ = sampled_tilted_mean(mode, formula, kernel, theta, beta, num_samples, moves,
                                          torch.Generator().manual_seed(1))
        errors[mode] = (estimate - exact).square().mean().sqrt().item()
    assert errors["metropolis"] < 0.1
    assert errors["walk"] > 2 * errors["metropolis"]


def test_one_rung_is_plain_importance_sampling():
    _, formula, kernel, theta = small_problem()
    raw = draw_assignments(torch.tanh(theta).expand(256, -1), torch.Generator().manual_seed(2))
    state = kernel.initialise(raw)
    satisfied_before = formula.num_clauses - state.num_violated()
    log_weights, _, _ = anneal(kernel, state, theta.expand(256, -1), torch.full((256,), 0.7), 1,
                               torch.Generator().manual_seed(3), torch.ones(256, dtype=torch.bool))
    assert torch.allclose(log_weights, 0.7 * satisfied_before.float())
    assert torch.equal(state.true_count, (state.assignment[:, formula.variable_index] * formula.sign > 0).sum(-1))


def test_solutions_met_on_the_way_are_recorded_and_inactive_slots_do_not_move():
    clauses, _ = planted_3sat(12, 30, 4)
    formula = formula_from_clauses(12, clauses)
    kernel, theta = FlipKernel(formula), torch.zeros(1, 12)
    raw = draw_assignments(torch.zeros(512, 12), torch.Generator().manual_seed(5))
    state = kernel.initialise(raw)
    active = torch.arange(512) % 2 == 0
    _, found, saved = anneal(kernel, state, theta.expand(512, -1), torch.full((512,), 3.0), 48,
                             torch.Generator().manual_seed(6), active)
    assert found.any() and not found[~active].any()
    assert torch.all(count_unsatisfied(saved[found], formula) == 0)
    assert torch.equal(state.assignment[~active], raw[~active])
