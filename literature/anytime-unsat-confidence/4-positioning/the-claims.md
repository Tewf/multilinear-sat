# What the note claimed it could and could not claim, checked

Part of [4. Positioning](README.md); the sections read in that file's order.

## Worst case. Wrong class, right conclusion.

> "such an algorithm would put SAT in coRP, hence NP in BPP, hence NP = RP and the polynomial
> hierarchy collapses (Ko 1982; Zachos)"

The algorithm never announces SAT without a witness and may announce UNSAT wrongly, so
`Pr[accept | x not in SAT] = 0` and `Pr[accept | x in SAT] >= 1/2`, which is the definition of
**RP**, not coRP [trevisan2002rp, Definition 4]. SAT in RP gives NP = RP at once, since RP is
closed under polynomial-time reductions and lies inside NP [trevisan2002rp, Theorem 1]; Ko and
Zachos are needed only for the weaker hypothesis NP inside BPP. The note's own "a posterior, not a
proof" is what rules coRP out, since coRP would require never announcing UNSAT on a satisfiable
instance. Everything after the class name is **theorem**: `(4/3)^n` tries, subexponential 3-SAT
contradicting ETH [impagliazzopaturi2001], and local reasoning escaping no width or degree bound
[bensassonwigderson2001].

## Typical case, satisfiable side. One large error, two small ones.

> "Above that, up to the threshold 4.267, every known algorithm fails"

**Wrong, and the largest factual error in the note.** At K = 3 backtracking survey propagation's
algorithmic threshold "practically coincide[s] with the SAT-UNSAT threshold", `alpha_a approx
4.268` against `alpha_s = 4.2667`, in practically linear time at `N = 10^6` [marino2016bsp, full
text]; survey inspired decimation already reached 4.2525 in `O(N log N)`. The sentence is
[achlioptascojaoghlan2008]'s statement of 2008, falsified at k = 3 since 2016. Smaller:
**[cojaoghlanfrieze2014walksat] says "polynomial time", not "linear time"** in its own abstract;
and "probSAT to about 4.2" is conservative, since focused local search keeps a linear-time regime
"well into ratios alpha > 4.2" [seitz2005focused]. The overlap gap sentence is **right as
qualified** ("for large k"), and [kizildag2025ogpthresholds] sharpens why: the m-OGP thresholds
need "k growing mildly with the number of Boolean variables", so **no barrier at k = 3 is a
theorem at all**. Add [angelini2026timescaling]: one threshold per time scaling, so "the barrier
region" is not a single place.

## Typical case, unsatisfiable side. Open, plus one wrong fact.

The uuf families are real: SATLIB ships `uuf50-218`, 1000 instances, and `uuf250-1065`, 100
instances [satlib_benchmarks]. The Wald framing is right in spirit and incomplete: an SPRT needs a
specified alternative `p_1` [wald1945], and on an unsatisfiable instance no success is ever
observed, so `p` is not identifiable from the run and must come from the family, which is gap 1.

> "The industrial answer to 'never stops on UNSAT' is a portfolio whose complete half does stop,
> which kissat already is (its rephasing walk)."

**Wrong in fact.** kissat is one complete CDCL solver whose `rephase_walking()` calls
`kissat_walk()` as a phase heuristic (`gh api` on `src/rephase.c` and `src/walk.c`)
[biere_kissat]. It is not a portfolio and has no incomplete half that could carry a posterior. The
portfolio claim belongs to [xu2008satzilla], the cooperation claim to [caizhang2021deepcooperation].

## What decides whether it is worth building. Wrong word, right experiment.

> "The one unoccupied number"

[putikhin2017continuousinit] occupied it in 2017, with the same solver the note proposes. What is
genuinely undone: that measurement with our objective, on public instances, with published numbers
and code. Replication plus extension, not new ground, and it should be written that way.
