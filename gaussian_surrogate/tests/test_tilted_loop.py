"""The tilted loop's parts (the Luby sequence and budgets, the per-group optimisers) and the loop
end to end: a planted instance solved and certified, an unsatisfiable one logged to the cap."""
import csv
import json
import math
import subprocess
import sys
from pathlib import Path

import torch

from configuration import Configuration
from dimacs import formula_from_clauses
from group_optimizers import GroupAdam, NaturalStep
from luby import LubyRestarts, luby
from random_instances import planted_3sat
from rounding import count_unsatisfied_python
from tilted_loop import TRAJECTORY_COLUMNS, solve_tilted

PACKAGE = Path(__file__).resolve().parent.parent
UNSATISFIABLE = [[1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3], [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3]]


def test_luby_sequence():
    assert [luby(index) for index in range(1, 16)] == [1, 1, 2, 1, 1, 2, 4, 1, 1, 2, 1, 1, 2, 4, 8]


def test_luby_restarts_follow_each_groups_budget():
    restarts = LubyRestarts(num_groups=2, unit_steps=3)     # group 0 at index 1 (1, 1, 2, ...), group 1 at index 2 (1, 2, ...)
    events = [restarts.advance() for _ in range(12)]
    assert events[2] == [0, 1] and events[5] == [0] and events[8] == [1] and events[11] == [0, 1]
    assert restarts.num_restarts == 6 and all(not event for index, event in enumerate(events) if index not in (2, 5, 8, 11))


def test_group_adam_first_step_is_the_signed_learning_rate_and_reset_is_per_group():
    theta = torch.zeros(2, 3)
    adam = GroupAdam(theta, learning_rate=0.1)
    gradient = torch.tensor([[1.0, -2.0, 0.5], [-3.0, 3.0, -0.1]])
    adam.step(gradient)
    assert torch.allclose(theta, 0.1 * gradient.sign(), atol=1e-6)
    adam.step(gradient)
    adam.reset([1])
    assert torch.all(adam.first[1] == 0) and adam.count[1] == 0 and torch.any(adam.first[0] != 0)
    before = theta.clone()
    adam.step(gradient)
    assert torch.allclose(theta[1] - before[1], 0.1 * gradient[1].sign(), atol=1e-6)


def test_natural_step_adds_the_scaled_gradient():
    theta = torch.ones(1, 2)
    NaturalStep(theta, 0.5).step(torch.tensor([[2.0, -4.0]]))
    assert theta.tolist() == [[2.0, -1.0]]


def test_loop_finds_and_certifies_a_planted_solution():
    clauses, _ = planted_3sat(30, 120, 2)
    configuration = Configuration(tilted_num_groups=4, tilted_slots_per_group=8, time_limit_seconds=10.0, device="cpu")
    result = solve_tilted(formula_from_clauses(30, clauses), configuration, seed=0)
    assert result.solved and count_unsatisfied_python(clauses, result.assignment) == 0


def test_loop_runs_to_the_cap_on_an_unsatisfiable_formula_and_logs_the_schedule(tmp_path):
    configuration = Configuration(tilted_num_groups=3, tilted_slots_per_group=4, luby_unit_steps=2, beta_max=0.2,
                                  time_limit_seconds=1.0, device="cpu")
    path = tmp_path / "trajectory.csv"
    result = solve_tilted(formula_from_clauses(3, UNSATISFIABLE), configuration, seed=1, trajectory_path=str(path))
    assert not result.solved and result.min_unsat_at_rounding >= 1 and result.num_restarts > 0
    with open(path) as handle:
        rows = list(csv.DictReader(handle))
    assert rows and list(rows[0]) == TRAJECTORY_COLUMNS and len(rows) == result.num_steps
    assert all(math.isfinite(float(row[column])) for row in rows for column in TRAJECTORY_COLUMNS)
    assert all(configuration.beta_initial - 1e-6 <= float(row["beta"]) <= configuration.beta_max + 1e-6 for row in rows)
    assert all(1.0 - 1e-4 <= float(row["ess"]) <= configuration.tilted_slots_per_group + 1e-3 for row in rows)
    assert all(int(row["min_unsat"]) >= 1 and 0 <= float(row["saturated"]) <= 3 for row in rows)
    assert int(rows[-1]["restarts"]) == result.num_restarts


def test_rigorous_groups_count_failures_and_the_posteriors_rise(tmp_path):
    configuration = Configuration(tilted_num_groups=4, tilted_slots_per_group=4, rigorous_fraction=0.5,
                                  beta_prior_a=2.0, beta_prior_b=30.0, time_limit_seconds=1.0, device="cpu")
    path = tmp_path / "trajectory.csv"
    result = solve_tilted(formula_from_clauses(3, UNSATISFIABLE), configuration, seed=2, trajectory_path=str(path))
    assert not result.solved
    assert result.rigorous_failures == result.heuristic_failures == 8 * result.num_steps
    assert result.posterior_rigorous > 0.5 and result.posterior_beta > 0.5
    with open(path) as handle:
        rows = list(csv.DictReader(handle))
    posteriors = [float(row["posterior_beta"]) for row in rows]
    assert all(later >= earlier for earlier, later in zip(posteriors, posteriors[1:]))
    assert posteriors[-1] == result.posterior_beta and int(rows[-1]["rigorous_failures"]) == result.rigorous_failures


def test_rigorous_groups_alone_find_a_planted_solution():
    clauses, _ = planted_3sat(30, 120, 6)
    configuration = Configuration(tilted_num_groups=4, tilted_slots_per_group=8, rigorous_fraction=1.0,
                                  time_limit_seconds=10.0, device="cpu")
    result = solve_tilted(formula_from_clauses(30, clauses), configuration, seed=0)
    assert result.solved and count_unsatisfied_python(clauses, result.assignment) == 0
    assert result.heuristic_failures == 0 and result.rigorous_failures < 32 * result.num_steps


def test_command_line_solves_with_obj_tilted(tmp_path):
    clauses, _ = planted_3sat(30, 120, 4)
    cnf = tmp_path / "planted.cnf"
    cnf.write_text(f"p cnf 30 {len(clauses)}\n" + "".join(" ".join(map(str, clause)) + " 0\n" for clause in clauses))
    command = [sys.executable, str(PACKAGE / "solve.py"), str(cnf), "--obj", "tilted", "--device", "cpu",
               "--time-limit", "10", "--tilted-num-groups", "4", "--tilted-slots-per-group", "8"]
    completed = subprocess.run(command, capture_output=True, text=True, cwd=PACKAGE)
    assert completed.returncode == 10, completed.stderr
    statistics = json.loads(next(line for line in completed.stdout.splitlines() if line.startswith("c json "))[7:])
    assert statistics["status"] == "SATISFIABLE" and statistics["steps"] >= 1
    assert {"posterior_rigorous", "posterior_beta", "rigorous_failures", "heuristic_failures"} <= set(statistics)
