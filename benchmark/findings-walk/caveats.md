# Caveats of the walk's measurements

Part of [the findings of the walk](README.md); the sections read in that file's order.

## Caveats

- One laptop GPU shared with nothing during the stages (nvidia-smi checked), but a chassis
  that rode 80 to 95 C through the parity stage; the seconds carry that band. Seeds 0 and 1,
  20 instances per family, no confidence intervals: the binomial spread of p at 4096 slots is
  under 0.01, the instance-to-instance spread is 0.1 to 0.25 (section 3's prior fit).
- The walk's polish is this library's SKC at noise 0.5 and 10n flips, the Python record's
  protocol, not probSAT's rule at its own constants; probSAT beside it is one run to a
  solution per instance and seed, process start included, with its flip count as the
  machine-free number.
- The ascent is the library's projected gradient at the 0.1 defaults (step 0.1, momentum
  0.9, kick 0.3), which the 0.1 sweep never found a solving setting for; the Python's mu
  ascent was Adam at 0.05, and the two give the same p at 200 to 500 steps.
- The parities were walked with the skc rule only; probsat's rule, xnfSAT's noise and
  restart constants, and a longer cap were not tried, and 20 s at 1024 slots is neither the
  paper's 1000 s nor the toolkit's 5 s on one seed.
- The posterior's prior is fitted on the family it is then tested on (40 fractions of the
  same 20 instances at seeds 0 and 1); its reliability curve is on the diagonal because the
  satisfiable side is solved inside the first run, which says the walk is good on uf250,
  not that the posterior is calibrated on hard satisfiable instances, where the Q6 plan
  predicts over-confidence. The rigorous posterior cannot move at n = 250, as the record said.
- The CUDA walk is one thread per slot, latency-bound; a warp per slot was not tried.
