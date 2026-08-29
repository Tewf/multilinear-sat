"""Every tunable of the solver in one place, with the defaults the command line uses; each field
is a flag of the same name in solve.py. Constants of the tilted loop are PROVISIONAL: set once,
never tuned."""
from dataclasses import dataclass

import torch


@dataclass
class Configuration:
    batch_size: int = 64                  # random restarts optimised in parallel (gradient methods)
    learning_rate: float = 0.05           # Adam step on theta (gradient methods)
    steps_per_restart: int = 500          # Adam steps before every slot is reinitialised
    rounding_interval: int = 25           # steps between sign(p) checks
    init_scale: float = 1.0               # theta ~ Uniform(-init_scale, init_scale), both loops
    variance_floor: float = 1e-6          # max(var, floor) under the square root
    walksat_flips_per_variable: int = 2   # polish budget = this * number of variables
    walksat_noise: float = 0.5            # probability of a random flip in WalkSAT/SKC, polish and kernel
    polish_top_slots: int = 1             # rounded slots polished per check, fewest unsat first
    time_limit_seconds: float = 20.0
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    # the tilted sampling-gradient loop (--obj tilted)
    tilted_num_groups: int = 16                    # G groups, one theta each
    tilted_slots_per_group: int = 32               # S samples per group; B = G * S slots
    tilted_walk_flips_per_variable: float = 2.0    # L_walk = this * n kernel flips per sample and step
    tilted_learning_rate: float = 0.1              # eta, the step on theta
    tilted_optimizer: str = "adam"                 # adam | natural (theta += eta g)
    beta_initial: float = 0.05
    beta_growth_factor: float = 1.05               # applied while the group's ESS stays above the floor
    beta_max: float = 5.0
    ess_floor_fraction: float = 0.25               # raise beta while ESS >= this * S, else hold
    control_variate_coefficient: float = 0.0       # lambda in g_hat - lambda (h_hat - g_closed); 0 because the
                                                   # correction only added noise (see tilted_gradient.py)
    luby_unit_steps: int = 50                      # a group's restart budget = luby(i) * this, in steps
    saturation_threshold: float = 0.99             # |p_i| above it counts as a saturated mean in the log
