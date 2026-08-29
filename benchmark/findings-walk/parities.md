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
rule at noise 0.5 with 20 s does not close the last rows; xnfSAT is yalsat's probSAT-style
rule with its own constants, and the probsat rule of this walk was not tried on these
instances (caveat). The ascent's rounded point is a far worse start than all false here,
540 to 810 rows against 16 to 44: on Brent equations the relaxation's landscape does not
point at the decompositions, which is the replication's answer to the toolkit's step 3.

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
