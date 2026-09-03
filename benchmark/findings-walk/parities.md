# Native parities on MM-Challenge-1

Part of [the findings of the walk](README.md); the sections read in that file's order.

## 4. Parities (`../parity_challenge.md`)

The ten MM-Challenge-1 XNFs (19 251 variables, 55 983 clauses, 729 parities of length 23)
and the toolkit's own matmul_3x3x3 at rank 23 (`--emit-xnf`: 19 251 variables, 55 890
clauses, 729 parities), 1024 slots, 50n SKC flips per run on the Luby schedule, cap 20 s,
seeds 0 to 4, from all-false starts (xnfSAT's default, which its paper found better than
random) and from the ascent at 200 iterations. Today's numbers to beat (toolkit branch
las-vegas-sat, one seed, 5 s cap): xnfsat 3 of 10 (4-4-4-4-1 in 0.03 s, 2-2-2-2-A in 2.39 s,
2-2-2-2-D in 0.83 s), kissat none; on matmul_3x3x3 at 23 xnfsat 0 of 5 in 60 s.

| instance | all-false walk, solved / 5 | best violated rows at the cap | ascent then walk, solved / 5 | best violated rows |
|---|---|---|---|---|
| MM-23-2-2-2-2-3 | 0 | 27 to 30 | 0 | 543 to 562 |
| MM-23-2-2-2-2-A | 0 | 18 to 21 | 0 | 545 to 569 |
| MM-23-2-2-2-2-B | 0 | 20 to 22 | 0 | 547 to 568 |
| MM-23-2-2-2-2-C | 0 | 19 to 22 | 0 | 544 to 799 |
| MM-23-2-2-2-2-D | 0 | 19 to 23 | 0 | 772 to 805 |
| MM-23-2-2-2-2-M | 0 | 16 to 21 | 0 | 774 to 798 |
| MM-23-2-2-2-3-4 | 0 | 29 to 35 | 0 | 781 to 807 |
| MM-23-2-2-2-4-A | 0 | 23 to 27 | 0 | 780 to 801 |
| MM-23-2-2-2-4-B | 0 | 25 to 27 | 0 | 777 to 812 |
| MM-23-4-4-4-4-1 | 0 | 37 to 44 | 0 | 785 to 804 |
| matmul_3x3x3 at 23 | 0 | 6 to 7 | 0 | 767 to 790 |

None solved, where xnfsat solves three of ten within five seconds. The native parity does
what it should (a parity is one row, its flip a toggle; the walk on the XNF reaches 16 to 44
violated rows of 56 700 from all false, and 6 to 7 on the toolkit's formula) and the SKC
rule at noise 0.5 with 20 s does not close the last rows. The ascent's rounded point is a
far worse start than all false here, 540 to 810 rows against 16 to 44: on Brent equations
the relaxation's landscape does not point at the decompositions, which is the replication's
answer to the toolkit's step 3.

**The xnf rule closes half the gap and no instance (2026-09-01).** With xnfSAT's weighted
break ported as `--walk-rule xnf` (the caveat above was that only SKC had been tried), the
same protocol reaches 5 to 15 violated rows on the 2-2-2-2 instances against SKC's 16 to 30,
14 to 23 on the 2-2-2-3/4, 27 to 31 on 4-4-4-4-1, and 4 to 5 on the toolkit's formula
against 6 to 7 - every instance roughly halved, none solved. Under the same rule the
ascent's start improves from 540-810 to 216-266 and stays an order of magnitude behind all
false, so the relaxation verdict does not move. Two readings. First, the instance the rule
helps least, 4-4-4-4-1, is the one xnfsat solves fastest (0.03 s), so what separates the
solvers there is not the variable score. Second, the shape matches the n = 5000 boundary of
[../arms/front.md](../arms/front.md): xnfsat spends its five seconds as one uninterrupted
chain of about 5e7 flips where each of our 1024 slots gets about 1e6 across its Luby runs,
and Brent equations, like n = 5000, look like formulas that pay for one long walk rather
than many short ones. The next lever is the budget shape (fewer slots, far longer runs), not the rule - measured
2026-09-03 in the section below: a real efficiency lever, but it closes no instance.

Verification on matmul_2x2x2 at rank 7 through the toolkit's `decide-rank-by-sat --solver`
route, which reads the model back and re-multiplies it: given the binary itself the toolkit
names it multilinear-sat, hands it the 3-cut CNF and runs the 0.1 defaults (the ascent alone,
one thread), and reports NO after 60 s (its documented third answer for a solver that can only
find); given the `benchmark/as-xnfsat/xnfsat` adapter it hands the XNF, and the walk from all
false at 4096 slots gives no answer in 120 s. The re-multiplication is what caught the parser
bug on the way (a model of the mutilated formula was refused); the toolkit's own record has
xnfsat at 0 of 5 and yalsat at 1 of 5 in 60 s on this fixture, so no route holds a verified
model of it. On an XNF read correctly the solver's own checker certifies every model it
reports, which the brute-force doctest cases on tiny XNFs cover.

## The budget shape is a real efficiency lever and still closes nothing (2026-09-03)

The lever the previous section left unmeasured, tested: the ten MM-Challenge-1 XNFs from all
false, the xnf rule, a 60 s cap, three shapes of the same flip budget - the GPU's 4096 short
Luby chains against a few long fixed-schedule walks on the CPU (8 chains, and 1). None solves.
What moves is the floor and the flips it costs to reach it: on seven of ten instances a CPU
long walk reaches fewer violated rows than the 4096-slot batch while spending **10 to 40x
fewer flips** (the batch ~1.1e9, the eight-chain walk ~3e7). The clearest cell is
`MM-23-2-2-2-2-A`: the single long chain reaches **2 violated rows of 56 700** on 1e8 flips
where the batch sits at 5 on 1.05e9. So the shape reading of the n = 5000 boundary holds -
fewer, longer walks descend far more per flip - but the last two to seven rows do not close,
and on the three hardest instances (`2-2-2-4-A`, `4-B`, `4-4-4-4-1`) the long shape does not
even lower the floor. The residue tracks the instance, not the budget: the shape is a real
efficiency lever, not the missing solve. The gap to xnfsat, which solves three of these, is
not the budget shape either - its single chain also runs about 6x faster per flip than this
solver's (1e7/s against 1.6e6/s), so implementation throughput and the last-rows barrier are
what remain, not the number of chains. The raw per-instance cells are kept as a local archive
and not committed; the floors quoted here are the record.

**A records caveat found on the way.** Before commit `bb322b7`, `walk_rule_name` had no case
for `WalkRule::Xnf` and serialised it as `metropolis`, so every `--walk-rule xnf` row in
`parity_challenge.jsonl` carries `walk_rule: metropolis`. The rule was applied (skc, metropolis
and xnf give three distinct floors, 22 / 107 / 18 on `MM-23-2-2-2-2-A`), so the prose above and
in the earlier sections is right; only the machine-readable label was wrong, and is fixed.
