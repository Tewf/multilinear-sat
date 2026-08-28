"""Every tunable of the solver in one place, with the defaults the command line uses."""
from dataclasses import dataclass

import torch


@dataclass
class Configuration:
    batch_size: int = 64                  # random restarts optimised in parallel
    learning_rate: float = 0.05           # Adam step on theta
    steps_per_restart: int = 500          # Adam steps before every slot is reinitialised
    rounding_interval: int = 25           # steps between sign(p) checks
    init_scale: float = 1.0               # theta ~ Uniform(-init_scale, init_scale)
    variance_floor: float = 1e-6          # max(var, floor) under the square root
    walksat_flips_per_variable: int = 2   # polish budget = this * number of variables
    walksat_noise: float = 0.5            # probability of a random flip in WalkSAT/SKC
    polish_top_slots: int = 1             # rounded slots polished per check, fewest unsat first
    time_limit_seconds: float = 20.0
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
