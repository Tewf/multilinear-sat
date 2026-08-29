# The UNSAT posterior against kissat

Part of [the findings of the walk](README.md); the sections read in that file's order.

## 3. The posterior (`../posterior_calibration.md`)

uf250-1065 against uuf250-1065, the first 20 instances of each: the walk from uniform starts,
10n SKC flips at 4096 slots, half the batch rigorous (Schöning's rule from uniform starts for
3n flips), cap 20 s, prior P(SAT) = 0.5, Beta(0.4698, 5.0207) fitted by moments on the 40
uniform-arm fractions of section 2 on uf250 (mean 0.0856, one fraction of zero); kissat's
refutation, fastest of three runs, beside it.

| what | result |
|---|---|
| satisfiable instances solved | 20 of 20, all inside the first run (0.08 to 0.11 s), before any failure is counted |
| their posterior | the prior, 0.5, for all 20: no false alarm at any threshold |
| unsatisfiable instances at the cap | 20 of 20 in [0.99, 0.999) after 86 to 91 runs, 176 000 to 186 000 failed restarts |
| reliability curve | on the diagonal: bin [0.5, 0.9) holds 20 instances, 0 unsatisfiable; bin [0.99, 0.999) holds 20, all unsatisfiable |
| kissat's refutation | 1.13 to 4.17 s, median 2.54 s, exit 20 every time |
| time to a 0.99 posterior | at the 42nd run on all 20 instances (86 016 failed restarts): 7.9 to 8.1 s on the 7 instances run on a cool chassis (0.22 s per run), 14.0 to 15.8 s on the 13 run while the package throttled at 95 C beside a rebuild (0.33 to 0.39 s per run); 3.1x kissat's median at full speed |
| the rigorous posterior | at the prior throughout: (3/4)^250 / 2253 = 2.7e-35 per try |

The Beta-mixture posterior depends on the failure count alone once the prior is fixed, and the
count per run is fixed by the batch, so the crossing falls on the same run everywhere and only
the run's seconds vary. At the card's speed 0.99 comes about 8 s after the start, three times
kissat's refutation, and stays a posterior. The first pass of this experiment put the crossing
at 16 s because the harness kept only the tail of the solver's log (fixed in `walk_runs.py`); the
second pass shares its second half with a rebuild, which is why both bands are reported. The
rigorous half is arithmetic that cannot move at n = 250.
