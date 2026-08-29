"""The decisive number of the tilted loop: the per-restart success probability p of one polish
(L SKC flips of the flip kernel) started from four seeds, the cost of a restart, and their ratio,
the expected time to a solution. Seeds: uniform random; all false; mu ascent for T Adam steps
rounded by sign; the tilted loop for T steps, then draws from its final q_theta (optionally the
same with walk_mode walk, whose weights are biased). Every seed is polished the same way on the
same 512 slots. A replication of Putikhin and Kascheev (EWDTS 2017), who seeded probSAT from a
continuous extension without publishing a per-restart number, with a new estimator. One JSONL
record per (family, instance, seed method, seed), resumable; the table is seed_table.py."""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import torch

PACKAGE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PACKAGE))
from adjacency import build_clause_adjacency            # noqa: E402
from configuration import Configuration                  # noqa: E402
from dimacs import read_dimacs                           # noqa: E402
from flip_kernel import FlipKernel                       # noqa: E402
from methods import build_method                         # noqa: E402
from rounding import round_to_assignment                 # noqa: E402
from sampling import draw_assignments                    # noqa: E402
from tilted_loop import TiltedLoop                       # noqa: E402

FAMILIES = ["uf50-218", "uf100-430", "uf250-1065"]
INSTANCES_DIRECTORY = PACKAGE.parent / "benchmark" / "instances"
SEED_METHODS = ["uniform", "all_false", "mu", "tilted", "tilted_walk"]
DEFAULT_SEED_METHODS = SEED_METHODS[:4]


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--device", default=Configuration.device)
    parser.add_argument("--families", nargs="+", default=FAMILIES)
    parser.add_argument("--instances", type=int, default=20)
    parser.add_argument("--slots", type=int, default=512)
    parser.add_argument("--slots-per-group", type=int, default=32, help="S of the tilted loop; G = slots / S")
    parser.add_argument("--steps", type=int, default=500, help="T, the seeding steps of mu and of the tilted loop")
    parser.add_argument("--polish-flips-per-variable", type=int, default=10, help="L / n of the polish")
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1])
    parser.add_argument("--seed-methods", nargs="+", default=DEFAULT_SEED_METHODS, choices=SEED_METHODS)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "seed_comparison.jsonl")
    return parser.parse_args()


def elapsed_since(start, device):
    if device == "cuda":
        torch.cuda.synchronize()
    return time.perf_counter() - start


def mu_seed(formula, configuration, steps, seed):
    """sign(p) after `steps` Adam steps of the mu ascent on batch_size restarts."""
    adjacency = build_clause_adjacency(formula).to(configuration.device)
    objective, relaxation = build_method("mu", formula, adjacency, configuration.variance_floor)
    generator = torch.Generator(device=configuration.device).manual_seed(seed)
    parameters = relaxation.initial_parameters((configuration.batch_size, formula.num_variables), generator,
                                               configuration.init_scale)
    optimizer = torch.optim.Adam([parameters], lr=configuration.learning_rate)
    for _ in range(steps):
        value = objective(relaxation.point(parameters), with_diagnostics=False)
        optimizer.zero_grad()
        (-value.ascent_target.sum()).backward()
        optimizer.step()
    with torch.no_grad():
        return round_to_assignment(relaxation.point(parameters)), {}


def tilted_seed(formula, configuration, steps, seed):
    """Draws from the loop's q_theta after `steps` steps (run through, solutions on the way counted)."""
    loop = TiltedLoop(formula, configuration, seed)
    solved_during_seed, min_unsat_seen = 0, formula.num_clauses
    for _ in range(steps):
        min_unsat, solution, numbers = loop.step()
        solved_during_seed += solution is not None
        min_unsat_seen = min(min_unsat_seen, min_unsat)
    p = torch.tanh(loop.theta)
    draws = draw_assignments(p.repeat_interleave(configuration.tilted_slots_per_group, dim=0), loop.generator)
    return draws, dict(final_beta=numbers[0], final_ess=numbers[1], final_mu=numbers[2],
                       saturated_fraction=numbers[3] / formula.num_variables, min_unsat_during_seed=min_unsat_seen,
                       steps_with_a_solution=solved_during_seed, weights=loop.configuration.walk_mode)


def make_seed(method, formula, arguments, seed):
    """(assignments [slots, n], extra numbers to record, seconds)."""
    device, slots = arguments.device, arguments.slots
    generator = torch.Generator(device=device).manual_seed(seed)
    start = time.perf_counter()
    if method == "uniform":
        seeds, extra = draw_assignments(torch.zeros(slots, formula.num_variables, device=device), generator), {}
    elif method == "all_false":
        seeds, extra = torch.full((slots, formula.num_variables), -1.0, device=device), {}
    elif method == "mu":
        seeds, extra = mu_seed(formula, Configuration(batch_size=slots, device=device), arguments.steps, seed)
    else:
        configuration = Configuration(tilted_num_groups=slots // arguments.slots_per_group,
                                      tilted_slots_per_group=arguments.slots_per_group, device=device,
                                      walk_mode="walk" if method == "tilted_walk" else "metropolis")
        seeds, extra = tilted_seed(formula, configuration, arguments.steps, seed)
    return seeds, extra, elapsed_since(start, device)


def polish(kernel, seeds, flips, noise, seed, device):
    """(fraction of slots satisfied after `flips` SKC flips, seconds)."""
    generator = torch.Generator(device=device).manual_seed(seed + 1000)
    start = time.perf_counter()
    state = kernel.initialise(seeds)
    kernel.walk(state, flips, torch.zeros(seeds.shape[0], dtype=torch.bool, device=device), noise, generator)
    fraction = (state.num_violated() == 0).float().mean().item()
    return fraction, elapsed_since(start, device)


def provenance(arguments):
    query = ["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader"]
    try:
        gpu_processes = subprocess.run(query, capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        gpu_processes = "nvidia-smi unavailable"
    head = subprocess.run(["git", "rev-parse", "--short=10", "HEAD"], cwd=PACKAGE, capture_output=True, text=True).stdout.strip()
    return dict(kind="provenance", timestamp=datetime.now().isoformat(timespec="seconds"), commit=head,
                device=arguments.device, torch=torch.__version__,
                gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
                gpu_processes_at_start=gpu_processes, arguments={k: str(v) for k, v in vars(arguments).items()})


def existing_keys(path):
    if not path.exists():
        return set()
    with open(path) as handle:
        records = [json.loads(line) for line in handle if line.strip()]
    return {(r["family"], r["instance"], r["seed_method"], r["seed"]) for r in records if r.get("kind") == "run"}


def main():
    arguments = parse_arguments()
    done = existing_keys(arguments.output)
    noise = Configuration.walksat_noise
    with open(arguments.output, "a") as output:
        output.write(json.dumps(provenance(arguments)) + "\n")
        warmed_up = False
        for family in arguments.families:
            for path in sorted((INSTANCES_DIRECTORY / family).glob("*.cnf"))[: arguments.instances]:
                formula = read_dimacs(path).to(arguments.device)
                kernel = FlipKernel(formula)
                flips = arguments.polish_flips_per_variable * formula.num_variables
                if not warmed_up:     # every seed method and the polish once, untimed: no start-up cost in a record
                    for method in arguments.seed_methods:
                        polish(kernel, make_seed(method, formula, arguments, 0)[0], flips, noise, 0, arguments.device)
                    warmed_up = True
                for seed in arguments.seeds:
                    for method in arguments.seed_methods:
                        if (family, path.name, method, seed) in done:
                            continue
                        seeds, extra, seed_seconds = make_seed(method, formula, arguments, seed)
                        fraction, polish_seconds = polish(kernel, seeds, flips, noise, seed, arguments.device)
                        cost_ms = (seed_seconds + polish_seconds) * 1000 / arguments.slots
                        record = dict(kind="run", family=family, instance=path.name, seed_method=method, seed=seed,
                                      slots=arguments.slots, steps=arguments.steps, polish_flips=flips,
                                      success_fraction=fraction, seed_seconds=round(seed_seconds, 4),
                                      polish_seconds=round(polish_seconds, 4), cost_per_restart_ms=round(cost_ms, 4),
                                      expected_time_ms=round(cost_ms / fraction, 2) if fraction > 0 else None,
                                      kernel_flips_per_second_per_chain=round(flips / polish_seconds),
                                      timestamp=datetime.now().isoformat(timespec="seconds"), **extra)
                        output.write(json.dumps(record) + "\n")
                        output.flush()
                        print(f"{family} {path.name} seed={seed} {method:12s} p={fraction:.4f} "
                              f"seed={seed_seconds:.2f}s polish={polish_seconds:.2f}s cost/restart={cost_ms:.3f}ms", flush=True)


if __name__ == "__main__":
    main()
