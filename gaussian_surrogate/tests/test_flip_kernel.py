"""The batched flip kernel: maintained counts against counts from scratch, the violated set,
the choice rules, agreement with walksat.py on one slot, and Schöning's success rate on uf20-91."""
from pathlib import Path

import numpy as np
import pytest
import torch

from dimacs import formula_from_clauses, read_dimacs
from flip_kernel import FlipKernel
from random_instances import random_3sat
from rounding import count_unsatisfied
from walksat import build_occurrence_lists, flip_variable

UF20 = Path(__file__).resolve().parents[2] / "benchmark" / "instances" / "uf20-91" / "uf20-01.cnf"


def random_problem(num_variables=15, num_clauses=60, num_slots=8, seed=0):
    clauses = random_3sat(num_variables, num_clauses, seed)
    formula = formula_from_clauses(num_variables, clauses)
    generator = torch.Generator().manual_seed(seed)
    assignment = torch.where(torch.rand(num_slots, num_variables, generator=generator) < 0.5, -1.0, 1.0)
    return clauses, formula, FlipKernel(formula), assignment, generator


def counts_from_scratch(state, formula):
    return (state.assignment[:, formula.variable_index] * formula.sign > 0).sum(dim=-1)


@pytest.mark.parametrize("uniform", [False, True], ids=["skc", "schoening"])
def test_maintained_counts_and_violated_set_after_a_walk(uniform):
    _, formula, kernel, assignment, generator = random_problem()
    state = kernel.initialise(assignment)
    uniform_choice = torch.full((assignment.shape[0],), uniform)
    kernel.walk(state, 25, uniform_choice, noise=0.5, generator=generator)
    assert torch.equal(state.true_count, counts_from_scratch(state, formula))
    assert torch.equal(state.num_violated(), count_unsatisfied(state.assignment, formula))
    assert torch.all(state.assignment.abs() == 1.0)


def test_chosen_clause_is_violated_and_uniform():
    _, formula, kernel, assignment, generator = random_problem(num_slots=1)
    state = kernel.initialise(assignment)
    violated = state.violated[0].nonzero().squeeze(1).tolist()
    assert len(violated) >= 2
    picks = torch.stack([kernel.choose_violated_clause(state, generator)[0] for _ in range(4000)]).squeeze(1)
    assert set(picks.tolist()) <= set(violated)
    frequencies = torch.bincount(picks, minlength=formula.num_clauses)[violated] / picks.numel()
    assert torch.all((frequencies - 1 / len(violated)).abs() < 0.35 / len(violated))


def python_break_count(assignment, variable, clauses):
    """Clauses in which the variable's literal is the only true one."""
    count = 0
    for clause in clauses:
        own = [literal for literal in clause if abs(literal) - 1 == variable]
        true_literals = [literal for literal in clause if assignment[abs(literal) - 1] == np.sign(literal)]
        if own and true_literals == own:
            count += 1
    return count


def test_skc_choice_takes_a_zero_break_or_the_minimum_break_without_noise():
    clauses, formula, kernel, assignment, generator = random_problem(num_slots=32, seed=3)
    state = kernel.initialise(assignment)
    clause, active = kernel.choose_violated_clause(state, generator)
    chosen = kernel.choose_variable(state, clause, torch.zeros(32, dtype=torch.bool), noise=0.0, generator=generator)
    for slot in active.nonzero().squeeze(1).tolist():
        row = state.assignment[slot].tolist()
        candidates = formula.variable_index[clause[slot]].tolist()
        breaks = {variable: python_break_count(row, variable, clauses) for variable in candidates}
        assert chosen[slot].item() in candidates
        assert breaks[chosen[slot].item()] == min(breaks.values())


def test_one_slot_agrees_with_walksat_on_the_same_flip_sequence():
    _, formula, kernel, assignment, _ = random_problem(num_slots=1, seed=5)
    state = kernel.initialise(assignment)
    variable_index, sign = formula.variable_index.numpy(), formula.sign.numpy()
    occurrence_clauses, occurrence_signs = build_occurrence_lists(variable_index, sign, formula.num_variables)
    x = assignment[0].numpy().copy()
    true_count = (x[variable_index] * sign > 0).sum(axis=1)
    rng = np.random.default_rng(5)
    for variable in rng.integers(formula.num_variables, size=40):
        flip_variable(x, true_count, variable, occurrence_clauses, occurrence_signs)
        kernel.apply_flips(state, torch.tensor([variable]), torch.tensor([True]))
        assert np.array_equal(state.true_count[0].numpy(), true_count)
        assert np.array_equal(state.assignment[0].numpy(), x)
    assert np.array_equal(state.violated[0].numpy(), true_count == 0)


def test_inactive_slots_are_left_untouched():
    _, formula, kernel, assignment, _ = random_problem(num_slots=2)
    state = kernel.initialise(assignment)
    before = (state.assignment.clone(), state.true_count.clone())
    kernel.apply_flips(state, torch.tensor([0, 0]), torch.tensor([True, False]))
    assert torch.equal(state.assignment[1], before[0][1]) and torch.equal(state.true_count[1], before[1][1])
    assert state.assignment[0, 0] == -before[0][0, 0]
    assert torch.equal(state.true_count, counts_from_scratch(state, formula))


@pytest.mark.skipif(not UF20.exists(), reason="run benchmark/download_satlib.py for uf20-91")
def test_schoening_walk_on_uf20_succeeds_at_a_rate_consistent_across_seeds():
    formula, num_slots = read_dimacs(UF20), 4096
    kernel, rates = FlipKernel(formula), []
    for seed in (0, 1, 2):
        generator = torch.Generator().manual_seed(seed)
        assignment = torch.where(torch.rand(num_slots, formula.num_variables, generator=generator) < 0.5, -1.0, 1.0)
        state = kernel.initialise(assignment)
        kernel.walk(state, 3 * formula.num_variables, torch.ones(num_slots, dtype=torch.bool), 0.0, generator)
        rates.append((state.num_violated() == 0).float().mean().item())
    assert min(rates) > 0.75 ** formula.num_variables          # Schöning's one-try bound
    standard_error = (np.mean(rates) * (1 - np.mean(rates)) / num_slots) ** 0.5
    assert max(rates) - min(rates) < 6 * standard_error
