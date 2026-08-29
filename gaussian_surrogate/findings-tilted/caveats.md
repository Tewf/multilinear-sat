# Caveats of the tilted loop's measurements

Part of [the findings of the tilted loop](README.md); the sections read in that file's order.

## Caveats

- One GPU, seeds {0, 1}, 20 instances per family, no confidence intervals; the contention detector
  is the uniform arm's polish time, not a log of other processes.
- **The kernel is launch-bound (about 15 kernel launches per flip, 3k flips per second per
  chain), and every seed that runs the walk inside its steps pays that overhead 500 times over:**
  the cost columns of the tilted and tilted_walk rows are this implementation's, not the
  algorithm's. A fused kernel (the C++ port) would cut their seeding cost by the same factor as
  the polish, so the p column and the flips-per-slot column are what survive a port; the expected
  times do not, and per unit of flips the verdict is unchanged (tilted_walk spends 25x the flips
  per satisfied slot of a uniform start on uf250).
- The polish is the repository's flip kernel, not probSAT (three orders of magnitude slower per
  chain). Putikhin and Kascheev (EWDTS 2017) seeded probSAT itself with a different continuous
  extension; this is a replication with a different local search and seed, and their per-restart
  number is not published.
- The tilted seed draws its 512 slots from q_theta after T steps; rounding sign(p) per group
  (16 distinct starts) was not measured. T = 500, 2n moves per step, the beta schedule and every
  other constant were set once and never tuned; no decimation, no proposal correction beyond
  AIS, the Luby schedule kept on faith (`../method/not-built.md`).
- The Beta prior was fitted on the tilted_walk arm's fractions after 500 seeding steps, while the
  calibration loop's early restarts come from a fresh theta; the moment fit gave a < 1, whose
  marginal likelihood decays as k^(-0.45), which is why 0.99 takes 20,000 failures. A prior with
  mass at p = 0 (a family-level survival function is a mixture) is the review's step 2, unmeasured.
- The rigorous groups spent half the slots on a bound that cannot move at n = 250; they are in the
  run because the brief asked for them.
