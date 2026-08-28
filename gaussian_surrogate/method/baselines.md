# Baselines and what is shared

## Three methods, one search loop

| `--obj`   | maximises                          | parameters and point                          |
|-----------|------------------------------------|-----------------------------------------------|
| `F`       | log F                              | theta free, p = tanh(theta)                   |
| `mu`      | mu = m - sum_j U_j                 | theta free, p = tanh(theta)                   |
| `fourier` | mu, on FourierSAT's own geometry   | x on the box [-1, 1]^n, clipped after a step  |

`mu` and `fourier` maximise the same function: FourierSAT's clause polynomial on ±1 with
independent means is exactly 1 - U_j, so its sum is mu up to the constant m. What separates
them is the relaxation: an unconstrained theta through tanh, or a projected ascent on the
box. `F` differs from `mu` only in the function.

Everything else is one code path (`solver.py`), so a difference in the table can only come
from the objective or the relaxation:

- a batch of `batch_size` restarts optimised at once by Adam with one learning rate;
- every `rounding_interval` steps, the point *evaluated in that step* is rounded by sign
  (ties to +1) and the violated clauses of every slot are counted;
- the slot with the fewest violations gets a WalkSAT/SKC polish (`walksat.py`: a random
  unsatisfied clause; a zero-break variable if one exists, else with probability
  `walksat_noise` a random one, else the minimum-break one; `walksat_flips_per_variable * n`
  flips);
- after `steps_per_restart` steps every slot is reinitialised; the run stops at the first
  satisfying assignment or at the wall-clock limit;
- a reported assignment is re-checked clause by clause in plain Python before it is printed.

The relaxation is a small object (`relaxation.py`) with three methods: initial parameters
from Uniform(-init_scale, init_scale), the map from parameters to the point, and the
projection after a step (nothing for tanh; `clamp_` to the box for `fourier`). Every method
logs mu, sigma^2 and F on its trajectory; a baseline evaluates the Gaussian moments without
gradient and only when a trajectory is being written, so its step costs what its own
objective costs.

## Why `fourier` is projected Adam and not L-BFGS-B

The author's plan names L-BFGS-B for the FourierSAT baseline, and FourierSAT's own
experiments used a quasi-Newton method (SLSQP, per its paper). Here the baseline runs
projected Adam on the box instead, for one reason: the scaffolding above is a batch of
restarts on the GPU, and L-BFGS-B is a CPU routine that handles one problem at a time, while
`torch.optim.LBFGS` is neither box-constrained nor a genuine per-sample method. Keeping the
optimiser identical keeps the comparison about the objective; a separate, unbatched L-BFGS-B
column would answer a different question (optimiser quality) and is not run.

## The cost asymmetry

A step of `mu` evaluates 3 m factors. A step of `F` also evaluates six factors for every pair
of clauses sharing a variable. Writing d_v for the number of clauses containing variable v,
the number of such pairs is at most sum_v C(d_v, 2) (pairs sharing two variables are counted
twice in that sum). In uniform random 3-SAT with m = alpha n clauses, d_v is close to
Poisson(3 alpha), so the pair count is about 9 alpha^2 n / 2, against alpha n clauses: about
9 alpha / 2 pairs per clause, and roughly 1 + 9 alpha, near 40 at alpha = 4.26, times the
multiplications of a `mu` step. The command line prints the pair count: 4045 to 4106 pairs for
the 218 clauses of the uf50-218 instances it was run on, against 9 alpha^2 n / 2 = 4277.

On a GPU the wall-clock ratio is smaller than the arithmetic ratio, because launch overhead is
paid by both; the measured ratio, and what it does to a time-capped comparison, belong to
`findings.md`. The consequence for reading the table is fixed in advance: under a time cap
`mu` takes more steps, more rounding events and more polishes per second than `F`, so
"solved within the cap" and "how close the rounded point is" are two different questions and
the table reports both.
