"""Fidelity of the surrogates to what they claim to approximate (the Q1 plan): at points sampled
along the F, mu and fourier trajectories, the exact log P(all satisfied) under the product
measure from one SDD compilation per instance, against log F, mu, logsum (the factorised
mean-field model count) and the pair cluster expansion; measured by Spearman rank correlation,
gradient cosine, and the slope of each surrogate against the truth. Writes a JSONL and a table."""
import argparse
import json
import sys
import time
from pathlib import Path

import torch

PACKAGE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PACKAGE))
from adjacency import build_clause_adjacency             # noqa: E402
from configuration import Configuration                  # noqa: E402
from dimacs import read_dimacs                           # noqa: E402
from methods import build_method                         # noqa: E402
from moments import expected_satisfied, pair_unsat_probability, unsat_probability, variance  # noqa: E402
from exact_count import ExactCounter                     # noqa: E402
from fidelity_table import write_table                   # noqa: E402

FAMILIES = ["uf50-218"]        # uf100-430 joins via --families when the compilation scales
SATLIB_ROOT = PACKAGE.parent / "benchmark" / "instances"
TRAJECTORY_METHODS = ["F", "mu", "fourier"]
INSTANCES_PER_FAMILY = 10
BATCH_SIZE = 16
STEPS = 500
SAMPLE_INTERVAL = 25
SLOTS_SAMPLED = 4
SEED = 0
INTERIOR = 1.0 - 1e-9   # drop points where some clause is unsatisfied almost surely: every
                        # surrogate and the truth are -inf together there and rank nothing


def trajectory_points(formula, method_name, configuration, arguments):
    """The first SLOTS_SAMPLED slots of the method's gradient dynamics at every sample event."""
    objective, relaxation = build_method(method_name, formula,
                                         build_clause_adjacency(formula), configuration.variance_floor)
    generator = torch.Generator(device=arguments.device).manual_seed(SEED)
    parameters = relaxation.initial_parameters((arguments.batch_size, formula.num_variables),
                                               generator, configuration.init_scale)
    optimizer = torch.optim.Adam([parameters], lr=configuration.learning_rate)
    samples = []
    for step in range(1, arguments.steps + 1):
        value = objective(relaxation.point(parameters), with_diagnostics=False)
        if step % SAMPLE_INTERVAL == 0:
            with torch.no_grad():
                samples.append(relaxation.point(parameters)[:SLOTS_SAMPLED].clone())
        optimizer.zero_grad()
        (-value.ascent_target.sum()).backward()
        optimizer.step()
        relaxation.project(parameters)
    return torch.cat(samples)


def surrogate_panel(points, formula, adjacency, variance_floor):
    """{surrogate name: (values [B], gradients [B, n])} at each point, by autograd."""
    p = points.clone().requires_grad_(True)
    unsat = unsat_probability(p, formula)
    pair_unsat = pair_unsat_probability(p, adjacency)
    mu = expected_satisfied(unsat, formula.num_clauses)
    var = variance(unsat, pair_unsat, adjacency)
    z = (mu - formula.num_clauses + 0.5) / var.clamp(min=variance_floor).sqrt()
    logsum = torch.log1p(-unsat).sum(dim=-1)
    first, second = adjacency.pair_index[:, 0], adjacency.pair_index[:, 1]
    both_satisfied = (1.0 - unsat[:, first] - unsat[:, second] + pair_unsat).clamp_min(1e-300)
    pair = logsum + (both_satisfied.log()
                     - torch.log1p(-unsat[:, first]) - torch.log1p(-unsat[:, second])).sum(dim=-1)
    panel = {}
    for name, value in [("log_F", torch.special.log_ndtr(z)), ("mu", mu),
                        ("logsum", logsum), ("pair", pair)]:
        gradient, = torch.autograd.grad(value.sum(), p, retain_graph=True)
        panel[name] = (value.detach(), gradient.detach())
    return panel


def spearman(a, b):
    """Rank correlation; the values are continuous, so ties are not a concern."""
    def centred_ranks(values):
        ranks = torch.empty_like(values)
        ranks[values.argsort()] = torch.arange(len(values), dtype=values.dtype)
        return ranks - ranks.mean()
    ra, rb = centred_ranks(a.double()), centred_ranks(b.double())
    return float(ra @ rb / (ra.norm() * rb.norm()))


def instance_record(name, formula, configuration, arguments):
    started = time.perf_counter()
    counter = ExactCounter(formula)
    compile_seconds = time.perf_counter() - started
    points = torch.cat([trajectory_points(formula, method, configuration, arguments)
                        for method in TRAJECTORY_METHODS])
    with torch.no_grad():
        interior = unsat_probability(points, formula).max(dim=-1).values < INTERIOR
    kept = points[interior].to(torch.float64)
    exact = [counter.log_probability_and_gradient(point) for point in kept.tolist()]
    exact_value = torch.tensor([value for value, _ in exact], dtype=torch.float64)
    exact_gradient = torch.tensor([gradient for _, gradient in exact], dtype=torch.float64)
    panel = surrogate_panel(kept, formula, build_clause_adjacency(formula), configuration.variance_floor)
    record = dict(instance=name, points=int(interior.sum()), dropped=int((~interior).sum()),
                  sdd_nodes=counter.node_count, compile_seconds=round(compile_seconds, 2),
                  seconds=round(time.perf_counter() - started, 1))
    centred = exact_value - exact_value.mean()
    for surrogate, (value, gradient) in panel.items():
        cosine = (gradient * exact_gradient).sum(-1) / (
            gradient.norm(dim=-1) * exact_gradient.norm(dim=-1)).clamp_min(1e-30)
        record[surrogate] = dict(
            spearman=round(spearman(value, exact_value), 4),
            cosine_median=round(float(cosine.median()), 4),
            slope=round(float((value - value.mean()) @ centred / (centred @ centred)), 4))
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--device", default="cpu")   # tiny tensors; leaves the card to the arms
    parser.add_argument("--families", nargs="*", default=FAMILIES)
    parser.add_argument("--instances", type=int, default=INSTANCES_PER_FAMILY)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--steps", type=int, default=STEPS)
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent)
    arguments = parser.parse_args()
    configuration = Configuration(batch_size=arguments.batch_size, device=arguments.device)
    records, jsonl = [], arguments.out_dir / "fidelity.jsonl"
    with open(jsonl, "w") as handle:
        for family in arguments.families:
            for path in sorted((SATLIB_ROOT / family).glob("*.cnf"))[:arguments.instances]:
                record = dict(family=family,
                              **instance_record(path.stem, read_dimacs(path).to(arguments.device),
                                                configuration, arguments))
                records.append(record)
                handle.write(json.dumps(record) + "\n")
                print(f"{family} {record['instance']:22s} points={record['points']:4d} "
                      f"rho_F={record['log_F']['spearman']:.3f} rho_mu={record['mu']['spearman']:.3f} "
                      f"cos_F={record['log_F']['cosine_median']:.3f} slope_F={record['log_F']['slope']:.3f} "
                      f"{record['seconds']}s", flush=True)
    write_table(records, arguments.out_dir / "fidelity.md", arguments)


if __name__ == "__main__":
    main()
