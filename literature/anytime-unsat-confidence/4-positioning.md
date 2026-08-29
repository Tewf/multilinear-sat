# 4. Positioning: the design note, section by section

`gaussian_surrogate/method/anytime-las-vegas.md`, every claim labelled **theorem**, **measured
elsewhere**, **open** or **wrong**, with the wrong ones quoted.

## Piece 1, Seed. Wrong.

> "The reviews found nobody using a relaxation as the initial assignment of a local search"

[putikhin2017continuousinit] is exactly that, into probSAT: "a heuristic for finding an initial
assignment based on non-linear optimization of continuous extension of given Boolean formula ...
implemented in ProbSAT solver". [fu2021initialassignment] does the non-random-initialisation half
for six SLS solvers. The same sentence stands in `fft-walksat-las-vegas/5-plan.md` as "the
combination nobody was found to have run", and is wrong there too. **What survives**: no public
code was found for the 2017 paper (three `gh search repos` phrasings, zero hits), it is four pages
with one recorded citation, and it does not use our objective. "Done once elsewhere without code"
is honest; "nobody" is not.

## Piece 2, Polish. Measured elsewhere.

The probSAT and xnfSAT records are established in the parent reviews and not re-litigated.
Nothing wrong.

## Piece 3, Restarts on the Luby schedule. Theorem, misapplied.

[luby1993] is exact: Theorem 5, `T(S_univ, p) <= 192 l_p (log l_p + 5)`; Theorem 7, the
logarithmic factor is unavoidable. But the note runs it over a well-tuned SLS on random 3-SAT,
where the RLD is exponential and memoryless, so "the probability of finding a solution within a
fixed time interval is independent of the run-time spent before" [hoosstutzle1999aij]: no schedule
helps, and independent parallel runs already give optimal speedup. Luby pays where the tail is
long, across formulas [lorenzworz2022longtails] and in backtrack search [gomes2000heavytails], not
inside one SLS run. **Open**: which regime our polish is in, which nothing here has measured.

## Piece 4, The rigorous half. Wrong by a polynomial factor.

> "On a satisfiable 3-CNF one such try succeeds with probability at least (3/4)^n, so after K
> failed rigorous tries P(no solution seen | SAT) <= (1 - (3/4)^n)^K <= exp(-K (3/4)^n)"

[schoning1999]'s own abstract says the process "has to be repeated only t times, on the average
... where t is within a polynomial factor of (2(1-1/k))^n". The per-try probability is therefore
`>= c (3/4)^n / poly(n)` and the bound is `exp(-K c (3/4)^n / poly(n))`. Small in the exponent,
fatal to the sentence, because the point of the piece is that the bound is exact. **Also the wrong
engine**: PPSZ has base 1.307031578 against Schöning's 1.3333 [jiangcai2026ppsz, paturi2005ppsz],
so the same construction needs strictly fewer tries. The structure is otherwise a **theorem** and
holds for every instance.

## Piece 5, The posterior. Arithmetic right, calibration open, three gaps.

`P(UNSAT | no solution by t) = (1 - pi)/((1 - pi) + pi S(t))` is Bayes and needs no citation.

1. **`S(t)` is instance-specific and only failures are observed.** Per instance the RLD is
   exponential with an instance-specific rate [hoosstutzle1999aij]; across instances the hardness
   is long-tailed [lorenzworz2022longtails], Pareto-Levy in backtrack search
   [gomes2000heavytails]. A family-level `S` is a mixture of exponentials and decays more slowly
   than any single instance's, so it **overstates** `P(UNSAT)` on the hard satisfiable instances,
   which are the ones that matter. The failure mode has a predictable sign.
2. **`pi` should not be a family constant.** [xu2012predictingsat] gets about 70 per cent
   satisfiability accuracy at the phase transition from polynomial-time features stable in
   instance size. An instance-conditional prior is available and free.
3. **A distribution-free `S` exists**: [luby1993, Theorem 6],
   `P[run > t] <= exp(-t/(64 l_p log t))`, with `l_p` unknown and instance-specific. That is the
   honest shape of the bound the note wants.

> "Either way the number is a posterior, not a proof."

**Right**, and it is the sentence that contradicts the next section.

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

## Not done in the world against not done here

**Not done in the world**: a calibrated probability of unsatisfiability updated by search failure,
and a reliability curve for one (nine phrasings, four services, all empty); and challenge five
itself [selman1997tenchallenges, prestwichlynce2006]. **Not done here**: seeding an SLS from a
relaxation, which was done once elsewhere without code; and predicting satisfiability from cheap
features [xu2012predictingsat], which is the prior the posterior needs and which is thoroughly
done elsewhere.
