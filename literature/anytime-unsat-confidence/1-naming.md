# 1. The problem in one sentence, and what the field calls it

## The sentence

Build a randomised SAT solver that finds a solution when one exists and never stops when none
does, and that reports, at every moment of a run in which it has found nothing, a number that
behaves like the probability that the instance is unsatisfiable.

## Our name against the field's

We called it "an anytime Las Vegas solver with a calibrated UNSAT posterior". Four of those
five words are the name of the method we already had in mind, and three of them are used by
the field for something else.

**Las Vegas.** The field's definition is exact and narrower than our use: a Las Vegas algorithm
"always produces the correct answer when it stops but whose running time is a random variable"
[luby1993], and the class of those that stop in expected polynomial time is ZPP = RP cap coRP
[vadhan2007lasvegas]. Our algorithm is Las Vegas on the satisfiable side only. On the
unsatisfiable side it never stops, which makes it a semi-decision procedure, and the moment a
posterior is allowed to end the run it stops being Las Vegas at all and becomes one-sided error.

**The property we actually want on the satisfiable side has a name: PAC**, probabilistic
asymptotic completeness. An algorithm is PAC for a class if for every soluble instance the
probability of having found a solution tends to one with run time [hoos1999pac]. The same paper
states the other half of our problem in one line: these algorithms "cannot be used to prove that
a given problem instance is unsatisfiable".

**Anytime UNSAT confidence is challenge five.** Selman, Kautz and McAllester's ten challenges
[selman1997tenchallenges] ask, as number five, for "a practical stochastic local search
procedure for proving unsatisfiability", and the field's own verdict fifteen years ago was that
"this one remains wide open" [prestwichlynce2006]. Our question is challenge five weakened from
a proof to a probability, which is a change nobody found has made.

**Posterior.** In the field the number attached to a formula before any search is the output of
a *satisfiability classifier* built on *empirical hardness model* features
[xu2012predictingsat, leytonbrown2009ehm, xu2008satzilla]. The number attached to a *count* with
a tolerance and a confidence is *approximate model counting* [chakraborty2013approxmc] or a
*bounding model counter* [gomes2006mbound]. Neither is a posterior updated by failure.

**Run length, not run time.** Hoos and Stützle's vocabulary is the *run-length distribution*
(RLD) and its survival function [hoosstutzle1999aij]; the design note's `S(t)` is that survival
function, and the family-level object the note fits is the *hardness distribution* across
instances [lorenzworz2022longtails], which is a different random variable.

**Restart schedule.** Our "Luby schedule" is the *universal strategy* `S_univ` of [luby1993].

## The acronyms to search with

RP, coRP, ZPP, BPP; ETH; PPSZ; SLS; RLD; PAC; SPRT (sequential probability ratio test)
[wald1945]; OGP (overlap gap property) [gamarnik2021ogp]; BPD (belief propagation guided
decimation) [cojaoghlan2011bpdecimation]; SP, SID and BSP (survey propagation, survey inspired
decimation, backtracking survey propagation) [braunstein2005sp, marino2016bsp]; CDCL; PAR-2.

## Why the naming matters here

Searching for "UNSAT posterior" returns nothing in any service (queries.md, nine phrasings).
Searching for "predicting satisfiability" returns [xu2012predictingsat] immediately, and
searching for "initial assignment" plus "continuous extension" returns
[putikhin2017continuousinit], which is the experiment the parent branch had recorded as
unoccupied ground. Both were missed by our own name for the problem.
