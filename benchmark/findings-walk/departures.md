# Departures of the port from its brief, with the reason

Part of [the findings of the walk](README.md); the sections read in that file's order.

## Departures from the brief, with the reason

- Runs are batch-synchronous (run k = seed_steps * luby(k) iterations then polish_flips *
  luby(k) flips, every slot restarting together) instead of the 0.1 per-slot Luby index,
  because the walk phase needs one budget per launch; `--luby-unit` stays as the old
  spelling of `--seed-steps` so `benchmark/results.md` and the 0.1 harness still run.
- `walk_flips_per_launch` (32) steps per kernel launch instead of one flip per launch: the
  launch-bound Python kernel was the artefact to remove; the certificate is checked after
  every launch and a satisfied slot idles inside the launch.
- The metropolis rule proposes a uniform variable of the formula (the annealing move of the
  Python record, symmetric, so exp(beta S) is stationary), not a variable of a violated row.
- The tilted seed steps theta plainly with the decreasing rate, not with Adam (the Python's
  default optimiser), because the brief asked for the decreasing step and no control variate.
- Parities are rows of the same formula with a flag, so one occurrence list serves gradient
  and walk; the parser reads both `x 1 2 0` (cnf2xnf) and `x1 2 0` (the toolkit's writer,
  whose glued literal the first version dropped, caught by the toolkit's re-multiplication).
- The verification through `decide-rank-by-sat --solver` needed an adapter named xnfsat
  (`../as-xnfsat/`), because the toolkit hands x lines by name and runs
  multilinear-sat on its 3-cut CNF; the toolkit itself is not modified. The instance was not
  solved by either route, nor by xnfsat in the toolkit's own record.
- The compiled Beta prior default is the C++ uniform-arm fit on uf250 (0.4698, 5.0207), not
  the Python calibration's (0.4546, 0.8283), which was fitted on its tilted_walk restart
  (mean p 0.354), a different restart from the one this port polishes with.
- The MM-Challenge cap is 20 s at 1024 slots, five seeds; the brief left the cap to me.
- The tilted arm ran on uf250 only, seeds 0 and 1, and was stopped after 7 of its 120 runs when
  the package reached 97 C under the coordinator's 30-minute ceiling on the card; its row says
  so, and the Python record's verdict on all three families stands.
