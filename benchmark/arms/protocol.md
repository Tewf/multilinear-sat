# The protocol every arm is priced on

One protocol for every variant, so that a rejection is a comparison of numbers taken the
same way and not a comparison of two experiments. The practice is the tensor-rank toolkit's:
every arm priced, the dominated ones rejected with their numbers kept, the survivor written
up as the algorithm ([../../method/algorithm.md](../../method/algorithm.md)).

## The cell

An arm on a family is one cell, over the family's instances decided satisfiable and its seeds:

- **p**, the per-restart success: satisfied heuristic slots at the end of a polish, over
  heuristic slot-runs (slots that are not the rigorous share, times runs completed).
- **cost per restart**, in ms at the arm's batch: the solver's own seed and polish seconds,
  over slot-runs.
- **expected time to a solution**, in ms: seconds over satisfied slot-runs, which is cost / p
  and stays defined under a schedule whose runs differ in length; infinite when no slot-run
  was satisfied, in which case the row is a lower bound and says so.
- **flips per solution**: walk steps over satisfied slot-runs, the machine-free number.
- beside them, the median time to the first solution of the batch (an anytime number, not
  part of the dominance rule) and the package temperature before and after each run.

**The budget.** Every arm spends the same budget per slot on a family, in units of its polish:
12 units on uf50, uf100, uf250 and n = 1000 (the Luby runs 1, 1, 2, 1, 1, 2, 4; or twelve
fixed-cutoff runs; or one run of twelve units with no restart), 4 units on n = 5000 (1, 1, 2)
to fit the evening. The polish arms change the unit (5n, 20n flips against 10n), which is the
factor they price. The base arm is uniform starts, the probsat rule, 4096 slots, the Luby
schedule, 10n flips per unit, no rigorous share; every other arm changes one factor of it,
and the two-factor arms the one-factor results suggested are listed as such in `arms.py`.

**n = 5000 was cut from the one-factor arms on the base stage's own numbers** (2026-08-29,
21:40): the base arm found nothing there in 200n flips per slot, p = 0 on every one of its 20
runs at 22.7 s a run, so every one-factor arm at n = 5000 would carry the same zero and price
nothing. The base's zero stands for all of them (`rejected.md` says so with the base's cells
and probSAT's beside them). **At n = 5000 only the base arm was measured**: the long-walk arm
(`polish_100n`, 100n flips per unit, 400n per slot over three Luby runs, about 230 s a run) is
defined in `arms.py` and was not run on 2026-08-29 (Mohamed's call, 23:38); it runs later with
the runner's own command, from `benchmark/`:

    python3 arms/run_arms.py --stages long_walk --families n5000-r4.20

and `python3 arms/dominance.py` then folds its cell into `front.md` and `rejected.md`. The
one-factor arms ran on uf250 and n = 1000 at both ratios.

## The instances

uf50-218, uf100-430, uf250-1065: the first 20 of each family in name order (SATLIB, all
satisfiable), seeds 0 and 1. n = 1000 and n = 5000 at ratios 4.20 and 4.26: five instances
each from `../generate_instances.py` (generator seeds 0 to 4), seeds 0 and 1. An instance is
**decided satisfiable** when any certificate exists: CaDiCaL's verdict in `../results.json`,
probSAT's model, or a walk's certified assignment; **unsatisfiable** on CaDiCaL's word;
**undecided** otherwise. Cells are over the decided-satisfiable instances, and each family's
table says how many were undecided, which at n = 5000 near the threshold is most of them.

## probSAT beside every family

One run to a solution per (instance, seed) on one core, process start and parse included,
with its own flip count; its cap is 60 s (120 s at n = 5000). It runs in its own stage, never
beside a CUDA run. Its wall time per solution is the number the batch's expected time is
read against; they are the same unit (ms per solution) on different hardware, which is the
comparison the library exists to make.

## Provenance

A frozen copy of the binary, named by commit and build time, is what every run executes; a
rebuild during the stage cannot change what the records were made with. A provenance block
opens every (stage, family): commit, binary path and sha256, probSAT's sha256, the GPU's name
and state, the two gate readings and the processes on the card, the package temperature, the
arguments. Every run record carries its command line, seed, per-run timeline and temperatures.

## The gate and the band

A CUDA stage starts only when two `nvidia-smi` readings a minute apart show 0 % utilisation
and under 6000 MiB used (an idle process holding memory is recorded, a computing one is a held
card), and the package is under 85 C; each run waits for the package to drop under 85 C.
Timings on this laptop vary by about 13 % run to run from throttling alone (the toolkit's
`MEASURING.md`, not re-measured here: `THERMAL_BAND` in `arms.py`, PROVISIONAL), so two
expected times within that band are not distinguished, and a ratio is quoted only where the
band cannot explain it.

## The dominance rule

Two cells are **distinguished** only when their ratio exceeds both the thermal band and two
standard errors of the log ratio under Poisson success counts, exp(2 sqrt(1/k_a + 1/k_b))
with k the satisfied slot-runs: at n = 1000 the counts are 2 to 30 per cell and a 30 %
difference in expected time is inside that noise, where on uf250 the counts are in the
thousands and the band governs. A zero count loses to any positive one. An arm is dominated
when another arm, **measured on every family it was measured on**, is at least as good on
expected time on each and strictly better on one, or not distinguished on expected time
anywhere and better on p on one; an arm measured on fewer families cannot dominate one
measured on more, since nothing says it is at least as good where it was not run. The front is
the set of arms no other dominates; per family, the Pareto front on (expected time, p) under
the same distinction. `rejected.md` keeps every dominated arm's cells beside its dominator's:
a rejection with its evidence deleted is indistinguishable from a whim. The tilted seed enters
only as a rejection on the sampling-walk records (94x a uniform start's expected time on the
runs it completed, against the brief's 2x admission).
