# 5. Plan: what to reject on paper, what to measure, against what

## Reject on paper, with the reason

1. **A confidence that grows meaningfully in polynomial time on every instance.** It puts SAT in
   RP [trevisan2002rp], hence NP = RP and the hierarchy collapses. Not a research direction.
2. **Schöning as the rigorous half.** Replace it with PPSZ: same one-sided structure, base
   1.307031578 against 4/3 [jiangcai2026ppsz, paturi2005ppsz]. Either way the exponential half
   is a footnote, since `(4/3)^n` at n = 250 is beyond any measurement; the rigorous certificate
   should be stated once as the reason the posterior is not a proof, and never run.
3. **The Luby schedule over the polish.** Where the RLD is exponential no schedule helps
   [hoosstutzle1999aij]; where it does not, Luby is right but our polish has not been shown to be
   there. Measure the RLD first, then decide. Do not implement a schedule on faith.
4. **A family-level `S(t)` as the calibration.** It is a mixture of exponentials, decays more
   slowly than any instance's, and biases `P(UNSAT)` upward exactly on hard satisfiable instances
   [hoosstutzle1999aij, lorenzworz2022longtails]. If a family-level `S` is used anyway, the
   reliability curve must be reported, not the point estimate.
5. **Calling the seed experiment new.** [putikhin2017continuousinit] ran it into probSAT in 2017.
   Write it as replication with a different objective.
6. **Claiming kissat as the portfolio's complete half.** kissat is one complete solver with a
   walk-based phase heuristic [biere_kissat]. If a portfolio is wanted, build one and cite
   [xu2008satzilla, caizhang2021deepcooperation].
7. **An anytime UNSAT confidence from approximate counting.** ApproxMC reaches zero only through
   a complete SAT call [chakraborty2013approxmc]; MBound's confidence is on a count, not a status
   [gomes2006mbound].

## Step 1: the prior, which is free and is currently a constant

Build `pi(instance)` from polynomial-time features rather than from the family. **Baseline:**
[xu2012predictingsat], about 70 per cent classification accuracy at the phase transition from
cheap features, on instances of the sizes complete methods can settle, with a classifier trained
on the smallest instances. **Measured by:** accuracy and, since a posterior is wanted, log loss
and a reliability curve, on `uf250-1065` against `uuf250-1065` [satlib_benchmarks]. A prior that
loses to a two-feature decision tree is not worth carrying.

## Step 2: the run-length distribution of our own polish

Before any posterior, measure `S(t)` per instance on `uf50-218` and `uf250-1065`, several hundred
independent runs each, and test it against an exponential. **Baseline:** [hoosstutzle1999aij],
whose published finding is that WalkSAT at approximately optimal noise passes that test on hard
random 3-SAT; and [lorenzworz2022longtails], whose finding is that the across-instance hardness
distribution is Johnson SB approaching lognormal. **Measured by:** a Kolmogorov-Smirnov statistic
against the fitted exponential per instance, and the fitted Johnson SB across instances. The
answer decides step 3 and decides whether restarts are worth anything at all.

## Step 3: the posterior, and its reliability curve

Only now compute `P(UNSAT | no solution by t)` from `pi` of step 1 and `S` of step 2, and run it
on both halves of a family. **Baselines, both named:**

- **For the SAT side, expected time to solution**, that is the cost of one restart divided by the
  probability that one restart succeeds: `probSAT` [adrianopolus_probsat, balintschoning2012probsat]
  and `kissat` [biere_kissat], on `uf250-1065`, same hardware, same seeds, same caps.
- **For the UNSAT side, kissat's refutation time** on `uuf50-218` (1000 instances) and
  `uuf250-1065` (100 instances) [satlib_benchmarks, biere_kissat], against the time our posterior
  needs to reach 99 per cent on the same instances, plus **a reliability curve**: bucket the
  reported posterior into deciles and plot the observed fraction of unsatisfiable instances in
  each bucket. No number for kissat on uuf250-1065 was found published in a form worth quoting,
  so this half of the baseline must be measured locally; no solver was run for this review.

**"Better" means**: on the SAT side, a lower expected time to solution than probSAT at the same
budget; on the UNSAT side, reaching 99 per cent before kissat refutes, with a reliability curve
that lies on the diagonal. Missing the diagonal is the informative failure, and its predicted
direction is over-confidence in UNSAT.

## Step 4: the seed experiment, as a replication

Three-way seed comparison into an unmodified `probSAT` [adrianopolus_probsat]: random, all-zero,
and the rounded point of our objective, everything else fixed. **Baselines:**
[putikhin2017continuousinit], the same experiment with a different continuous extension and no
public code, and [zhang2020nlocalsat], the neural version with 27 to 62 per cent improvement on
the 2018 random track and a public repository [myxxxsquared_nlocalsat] to reproduce the protocol
from. **Measured by:** per-restart success probability and expected time to solution at fixed
budget, on `uf250-1065` and on MM-Challenge-1 as `fft-walksat-las-vegas/5-plan.md` already sets
out. Publishing the code and the numbers is most of the contribution, since the 2017 paper has
neither.

## What would make the branch worth a paper, and what would close it

- Worth a paper: a reliability curve on the diagonal on uuf250-1065, with the time to 99 per cent
  reported against kissat's refutation time. Nobody has published one (queries.md, nine phrasings).
- Also worth a paper, separately: the seed replication with code, if the seed raises the
  per-restart success probability by more than its cost.
- Closes the branch: a posterior systematically above the diagonal that no amount of family
  modelling straightens, which is what step 2 predicts if the hardness distribution is
  long-tailed, plus a seed that does not pay for its gradient steps.
- Out of scope, permanently: the barrier region at k = 3. BSP is already at the threshold
  [marino2016bsp], and no known relaxation-seeded local search is near it.
