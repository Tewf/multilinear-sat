"""Bernoulli draws have the means they were drawn from; tilted weights normalise per group and
their effective sample size lies in [1, S] with the two limits exact."""
import numpy as np
import pytest
import torch

from sampling import draw_assignments, effective_sample_size, tilted_weights

NUM_GROUPS, SLOTS_PER_GROUP = 4, 16


def random_counts(seed):
    generator = torch.Generator().manual_seed(seed)
    return torch.randint(0, 40, (NUM_GROUPS * SLOTS_PER_GROUP,), generator=generator)


def test_weights_normalise_within_every_group():
    beta = torch.tensor([0.0, 0.1, 1.0, 5.0])
    weights = tilted_weights(random_counts(0), beta, NUM_GROUPS)
    assert weights.shape == (NUM_GROUPS, SLOTS_PER_GROUP)
    assert torch.all(weights >= 0)
    assert weights.sum(dim=1).tolist() == pytest.approx([1.0] * NUM_GROUPS, abs=1e-6)


def test_weights_match_the_explicit_exponential_formula():
    counts, beta = random_counts(1), 0.3
    expected = np.exp(beta * counts.view(NUM_GROUPS, -1).double().numpy())
    expected /= expected.sum(axis=1, keepdims=True)
    assert tilted_weights(counts, beta, NUM_GROUPS).double().numpy() == pytest.approx(expected, abs=1e-6)


def test_effective_sample_size_limits_and_range():
    counts = random_counts(2)
    assert effective_sample_size(tilted_weights(counts, 0.0, NUM_GROUPS)).tolist() \
        == pytest.approx([SLOTS_PER_GROUP] * NUM_GROUPS, abs=1e-4)
    unique_maximum = torch.arange(NUM_GROUPS * SLOTS_PER_GROUP)      # one strict maximum per group
    assert effective_sample_size(tilted_weights(unique_maximum, 50.0, NUM_GROUPS)).tolist() \
        == pytest.approx([1.0] * NUM_GROUPS, abs=1e-4)
    for beta in (0.05, 0.5, 3.0):
        ess = effective_sample_size(tilted_weights(counts, beta, NUM_GROUPS))
        assert torch.all(ess >= 1.0 - 1e-5) and torch.all(ess <= SLOTS_PER_GROUP + 1e-4)


def test_effective_sample_size_is_invariant_to_the_normalisation():
    weights = torch.rand(NUM_GROUPS, SLOTS_PER_GROUP, generator=torch.Generator().manual_seed(3))
    unnormalised = effective_sample_size(weights * 7.0)
    assert unnormalised.tolist() == pytest.approx(effective_sample_size(weights / weights.sum(1, keepdim=True)).tolist(), rel=1e-5)


def test_draws_are_signs_with_the_requested_means():
    num_draws, p = 20000, torch.tensor([-0.9, -0.3, 0.0, 0.5, 0.95])
    x = draw_assignments(p.expand(num_draws, -1), torch.Generator().manual_seed(4))
    assert x.shape == (num_draws, 5)
    assert torch.all(x.abs() == 1.0)
    standard_error = ((1 - p.square()) / num_draws).sqrt()
    assert torch.all((x.mean(dim=0) - p).abs() < 4 * standard_error + 1e-3)
