"""The bias of the sampled tilted mean against enumeration on a small formula, for both moves of
the loop (the AIS ladder over the Metropolis kernel, and the SKC walk with exp(beta S) weights),
as a function of the number of samples S and of the moves per sample. Zero moves is plain
importance sampling from q_theta, the same for both. Writes a markdown table."""
import argparse
import sys
from pathlib import Path

import numpy as np
import torch

PACKAGE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PACKAGE))
sys.path.insert(0, str(PACKAGE / "tests"))
from annealing import anneal                                            # noqa: E402
from brute_force_reference import exact_tilted_weights                  # noqa: E402
from dimacs import formula_from_clauses                                 # noqa: E402
from flip_kernel import FlipKernel                                      # noqa: E402
from random_instances import random_3sat                                # noqa: E402
from sampling import draw_assignments, effective_sample_size, normalised_weights   # noqa: E402

NUM_VARIABLES, NUM_CLAUSES = 12, 51          # ratio 4.25
BETAS = (0.5, 2.0)
SAMPLE_COUNTS = (64, 512, 4096)
MOVES_PER_VARIABLE = (0, 1, 4, 16)
NUM_SEEDS = 5


def sampled_tilted_mean(mode, formula, kernel, theta, beta, num_samples, moves, generator):
    """(estimate of E_tilted[x], ESS) from num_samples raw draws moved `moves` times."""
    p = torch.tanh(theta)
    raw = draw_assignments(p.expand(num_samples, -1), generator)
    state = kernel.initialise(raw)
    beta_slots = torch.full((num_samples,), beta)
    if moves == 0:
        log_weights = beta_slots * (formula.num_clauses - state.num_violated())
    elif mode == "metropolis":
        log_weights, _, _ = anneal(kernel, state, theta.expand(num_samples, -1), beta_slots, moves, generator,
                                   torch.ones(num_samples, dtype=torch.bool))
    else:
        kernel.walk(state, moves, torch.zeros(num_samples, dtype=torch.bool), 0.5, generator)
        log_weights = beta_slots * (formula.num_clauses - state.num_violated())
    weights = normalised_weights(log_weights, 1)
    return (weights.T * state.assignment).sum(dim=0), effective_sample_size(weights).item()


def measure(seed_formula=0):
    clauses = random_3sat(NUM_VARIABLES, NUM_CLAUSES, seed_formula)
    formula, kernel = formula_from_clauses(NUM_VARIABLES, clauses), FlipKernel(formula_from_clauses(NUM_VARIABLES, clauses))
    theta = torch.tensor(np.random.default_rng(seed_formula).uniform(-0.5, 0.5, NUM_VARIABLES), dtype=torch.float32)
    rows = []
    for beta in BETAS:
        points, exact_weights = exact_tilted_weights(NUM_VARIABLES, clauses, theta.double().numpy(), beta)
        exact = torch.tensor(exact_weights @ points, dtype=torch.float32)
        for mode in ("metropolis", "walk"):
            for moves_per_variable in MOVES_PER_VARIABLE:
                for num_samples in SAMPLE_COUNTS:
                    errors, ess = [], []
                    for seed in range(NUM_SEEDS):
                        generator = torch.Generator().manual_seed(seed)
                        estimate, sample_size = sampled_tilted_mean(mode, formula, kernel, theta.reshape(1, -1), beta,
                                                                    num_samples, moves_per_variable * NUM_VARIABLES, generator)
                        errors.append((estimate - exact).square().mean().sqrt().item())
                        ess.append(sample_size)
                    rows.append(dict(beta=beta, mode=mode, moves=moves_per_variable, samples=num_samples,
                                     rms_error=float(np.mean(errors)), ess=float(np.mean(ess))))
    return rows


def write_table(rows, path):
    lines = ["# Bias of the sampled tilted mean, by enumeration", "",
             f"Random 3-SAT, n = {NUM_VARIABLES}, m = {NUM_CLAUSES}, theta ~ U(-0.5, 0.5), exact E_tilted[x] by "
             f"enumeration of the cube. RMS error over the {NUM_VARIABLES} coordinates, mean over {NUM_SEEDS} seeds; "
             "moves per sample are AIS rungs (metropolis) or SKC flips (walk), as multiples of n; zero moves is plain "
             "importance sampling from q_theta for both. ESS is the mean effective sample size of the weights.", "",
             "| beta | move | moves / n | S = 64 | S = 512 | S = 4096 | ESS at 4096 |", "|---|---|---|---|---|---|---|"]
    for beta in BETAS:
        for mode in ("metropolis", "walk"):
            for moves in MOVES_PER_VARIABLE:
                cells = {r["samples"]: r for r in rows if (r["beta"], r["mode"], r["moves"]) == (beta, mode, moves)}
                lines.append(f"| {beta} | {mode} | {moves} | " + " | ".join(f"{cells[s]['rms_error']:.3f}" for s in SAMPLE_COUNTS)
                             + f" | {cells[SAMPLE_COUNTS[-1]]['ess']:.0f} |")
    path.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "tilted_mean_bias.md")
    arguments = parser.parse_args()
    rows = measure()
    for row in rows:
        print(row)
    write_table(rows, arguments.out)
    print(f"wrote {arguments.out}")
