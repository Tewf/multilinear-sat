"""The SDD counter against enumeration: log P(all satisfied) exactly, gradient by central
differences, on tiny random formulas."""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("pysdd")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "experiments"))

from brute_force_reference import enumerate_cube          # noqa: E402
from dimacs import formula_from_clauses                   # noqa: E402
from exact_count import ExactCounter                      # noqa: E402
from random_instances import random_3sat                  # noqa: E402

NUM_VARIABLES, NUM_CLAUSES = 8, 30
STEP = 1e-5


def probability_all_satisfied(clauses, p):
    _, probability, counts = enumerate_cube(NUM_VARIABLES, clauses, p)
    return float(probability[counts == len(clauses)].sum())


@pytest.mark.parametrize("instance_seed", [0, 1])
@pytest.mark.parametrize("point_seed", [0, 1, 2])
def test_counter_matches_enumeration(instance_seed, point_seed):
    clauses = random_3sat(NUM_VARIABLES, NUM_CLAUSES, instance_seed)
    counter = ExactCounter(formula_from_clauses(NUM_VARIABLES, clauses))
    p = np.random.default_rng(point_seed).uniform(-0.9, 0.9, NUM_VARIABLES)
    log_probability, gradient = counter.log_probability_and_gradient(p)
    assert log_probability == pytest.approx(math.log(probability_all_satisfied(clauses, p)), abs=1e-9)
    for index in range(NUM_VARIABLES):
        shifted = p.copy()
        shifted[index] += STEP
        upper = math.log(probability_all_satisfied(clauses, shifted))
        shifted[index] -= 2 * STEP
        lower = math.log(probability_all_satisfied(clauses, shifted))
        assert gradient[index] == pytest.approx((upper - lower) / (2 * STEP), abs=1e-5)
