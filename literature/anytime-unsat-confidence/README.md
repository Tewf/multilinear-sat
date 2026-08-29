# Q6: an anytime Las Vegas SAT solver with a calibrated UNSAT posterior

**The question.** Can a randomised solver find solutions when they exist, never stop when they
do not, and report at every moment a number that behaves like the probability that the instance
is unsatisfiable, and what does the field already hold on each half?

## Verdict

1. **Nobody has published a probability of unsatisfiability updated by search failure.** Nine
   phrasings across OpenAlex, Crossref, web search and `gh search repos`, all empty (queries.md).
   The nearest prior art computes it before any search: a classifier at about 70 per cent
   accuracy at the phase transition from polynomial-time features [xu2012predictingsat].
2. **The question has a name and it is challenge five**, "a practical stochastic local search
   procedure for proving unsatisfiability" [selman1997tenchallenges], which the field's own
   progress report calls "wide open" [prestwichlynce2006]. Our version weakens the proof to a
   probability, which is the move nobody was found to have made.
3. **The theorem that bounds the whole design: SAT in RP implies NP = RP.** An algorithm whose
   UNSAT confidence grows meaningfully in polynomial time on every instance never accepts a
   satisfiable-looking unsatisfiable formula, so it decides SAT with one-sided error, which is
   RP by definition [trevisan2002rp]; RP is closed under polynomial-time reductions and sits
   inside NP, so NP = RP, and the hierarchy collapses. The design note says "coRP", which is the
   wrong side; its conclusions survive, its class name does not.
4. **The exact certificate is exponential and the design note overstates it.** Schöning's per-try
   success probability is within a *polynomial factor* of `(3/4)^n` [schoning1999, abstract], not
   at least `(3/4)^n`; and PPSZ at base 1.307031578 [jiangcai2026ppsz] is the better engine.
5. **"Above 4.2 every known algorithm fails" is false at k = 3.** Backtracking survey propagation
   reaches `alpha_a approx 4.268` against `alpha_s = 4.2667`, in practically linear time at
   `N = 10^6` [marino2016bsp]. No barrier at fixed k = 3 is a theorem [kizildag2025ogpthresholds].
6. **The Luby schedule buys nothing where the note puts it**: a well-tuned SLS on hard random
   3-SAT has an exponential, memoryless run-length distribution [hoosstutzle1999aij].
7. **Q2's "nobody seeds a local search from a relaxation" is wrong**: [putikhin2017continuousinit]
   did it into probSAT in 2017. No public code was found, so the replication is still worth doing.

## The baselines, and what "better" means

**SAT side, expected time to solution** (cost of one restart divided by the probability one
restart succeeds), on `uf250-1065`: `probSAT` [adrianopolus_probsat, balintschoning2012probsat]
and `kissat` [biere_kissat], both `gh repo view` verified today, at fixed hardware, seeds and
caps.

**UNSAT posterior**: `kissat`'s refutation time on `uuf50-218` (1000 instances) and `uuf250-1065`
(100 instances) [satlib_benchmarks, fetched today] against the time our posterior needs to reach
99 per cent on the same instances, **plus a reliability curve**: posterior bucketed into deciles
against the observed unsatisfiable fraction per bucket. No published kissat refutation time on
uuf250-1065 was found worth quoting, so that half must be measured locally. No solver was run for
this review.

**Prior**: [xu2012predictingsat], about 70 per cent classification accuracy from cheap features,
which any instance-conditional `pi` must beat.

**Seed replication**: [putikhin2017continuousinit] for the experiment and
[zhang2020nlocalsat, myxxxsquared_nlocalsat] for the protocol and the public code.

**Better means**: a lower expected time to solution than probSAT at equal budget; and a
reliability curve on the diagonal, reaching 99 per cent before kissat refutes. The predicted
failure is over-confidence in UNSAT, because a family-level survival function is a mixture of
exponentials and decays more slowly than any single satisfiable instance's
[hoosstutzle1999aij, lorenzworz2022longtails].

## Files

- [1-naming.md](1-naming.md): the problem in one sentence, PAC, ZPP, RLD, challenge five, and
  why our name hid two literatures.
- [2-review.md](2-review.md): the map in five lines of work, each entry with how it was verified.
- [3-state-of-the-art.md](3-state-of-the-art.md): the records, with upper bounds kept apart from
  lower bounds, and the empty row that is our question.
- [4-positioning/README.md](4-positioning/README.md): the design note section by section, theorem, measured
  elsewhere, open or wrong, with the wrong ones quoted.
- [5-plan.md](5-plan.md): seven rejections on paper, four steps to measure, each with a baseline.
- [queries.md](queries.md): every query, service and hit count, including every zero.
- [references.bib](references.bib): one entry per work, each with its verification note.

Contract: `2026-08-28_gaussian-surrogate-sat/review-contract.md`. Question:
`q6-brief.md` there. Design note tested: `../../method/anytime-las-vegas.md`.
No code outside this folder was changed and nothing was committed.
