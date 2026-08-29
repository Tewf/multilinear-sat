# The five pieces of the design note, claim by claim

Part of [4. Positioning](README.md); the sections read in that file's order.

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
