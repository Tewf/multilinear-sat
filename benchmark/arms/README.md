# Arms: the variants of the walk priced against each other

One folder, one role: every variant of the batched walk priced on one protocol, the dominated
ones rejected with their numbers kept, the survivor written as the algorithm.

| File | Role |
|---|---|
| [`protocol.md`](protocol.md) | the cell, the budget, the instances and what "decided" means, probSAT beside each family, the provenance block, the gate, the thermal band, the dominance rule |
| `arms.py` | the variants as data: the base arm, the one-factor and two-factor arms as settings of the library's flags, the families and their budgets, the stage plan |
| `run_arms.py` | runs every (arm, family, instance, seed) not yet recorded, probSAT beside the base stage, on a free card under 85 C; resumable |
| `arms_results.jsonl` | the records: one provenance block per (stage, family), one record per run with its command, seed, timeline and temperatures |
| `dominance.py` | prices the cells from the records, finds the fronts, writes the two files below |
| [`front.md`](front.md) | the arms no other arm dominates, overall and per family, with their numbers and probSAT's |
| [`rejected.md`](rejected.md) | every dominated arm: by which arm, on which families, its cells beside the dominator's; the tilted seed rejected on the sampling-walk records |

    python3 run_arms.py --dry-run        # what remains
    python3 run_arms.py                  # the brief's stages in order (two_factor by --stages)
    python3 dominance.py                 # front.md and rejected.md from the records

The surviving arm, as pseudocode with the number behind each choice:
[`../../method/algorithm.md`](../../method/algorithm.md).
