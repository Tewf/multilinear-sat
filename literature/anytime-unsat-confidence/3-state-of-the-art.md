# 3. The state of the art: who holds what, measured how

Upper bounds (an algorithm exists) are kept apart from lower bounds (no algorithm of a class
exists). Every number below comes from a document fetched today.

## Upper bounds, worst case

| Claim | Holder | Bound | How measured |
|---|---|---|---|
| 3-SAT, randomised | [jiangcai2026ppsz] | `O*(1.307031578^n)` | proof; PPSZ unchanged, a new LP dual certificate for the recombination |
| k-SAT for k >= 4, and unique k-SAT | [paturi2005ppsz] | `O(2^{0.5625n})` for 4-CNF, `O(2^{0.386n})` unique 3-SAT | proof |
| k-SAT, simplest | [schoning1999] | repetitions within a polynomial factor of `(2(1-1/k))^n`, that is `(4/3)^n` at k = 3 | proof |

The Schöning bound is the one the design note builds on and it is the weakest of the three. It
is also the only one of the three whose per-try success probability the note uses directly, and
the polynomial factor in the paper's own abstract is the part the note drops.

## Upper bounds, random 3-SAT at the threshold

The reference point is `alpha_s(K = 3) = 4.2667`, the cavity-method estimate quoted by
[marino2016bsp]. It is not a theorem: the satisfiability conjecture is proved only for large k
[dingslysun2022threshold].

| Algorithm | Reach at k = 3 | Time | Size | Source |
|---|---|---|---|---|
| Backtracking survey propagation | `alpha_a approx 4.268`, "practically coincide[s]" with `alpha_s` | practically linear in N | to N = 10^6 | [marino2016bsp], full text |
| Survey inspired decimation | `alpha_a = 4.2525` | `O(N log N)` measured | N = O(10^5) | [marino2016bsp] quoting its refs |
| Focused local search, WalkSAT included | linear-time regime "well into ratios alpha > 4.2" | linear | not stated in the abstract | [seitz2005focused] |
| Fix | `(1 - eps_k) 2^k ln(k)/k`, asymptotic in k | polynomial whp | asymptotic | [cojaoghlan2010fix] |
| WalkSAT, proved | `rho 2^k/k`, asymptotic in k | polynomial whp | asymptotic | [cojaoghlanfrieze2014walksat] |

**The record holder on the satisfiable side at k = 3 is therefore BSP, not any local search, and
it reaches the threshold.** No hardware is stated for BSP in the fetched text beyond the sizes.

[angelini2026timescaling] is the correction to this whole table: the algorithmic threshold is not
one number but one number per time scaling, "linear, quadratic, cubic regimes (and so on)", so a
solver allowed superlinear time is being compared against the wrong barrier.

## Lower bounds, and for which class

| Statement | Class ruled out | Regime | Source |
|---|---|---|---|
| No `2^{o(n)}` algorithm for 3-SAT | all, conjecturally | worst case | [impagliazzopaturi2001] |
| Resolution width `Omega(n)` on expanding CNF | resolution refutations | worst case and random | [bensassonwigderson2001] |
| WalkSAT ineffective above `c 2^k ln^2 k / k` | WalkSAT itself | random, large k | [cojaoghlan2017walksatstalls] |
| BPD fails above `rho r_k / k` | belief propagation guided decimation | random, all k | [cojaoghlan2011bpdecimation] |
| Low-degree polynomials fail above `(1 + o_k(1)) kappa* 2^k log k / k`, `kappa* approx 4.911` | low-degree, covering Fix, BPD, SP decimation, local algorithms | random, asymptotic in k | [breslerhuang2021lowdegree] |
| Sharp m-OGP thresholds | stable and insensitive algorithms | random, "all k growing mildly with n" | [kizildag2025ogpthresholds] |

**Nothing in this table is a lower bound at fixed k = 3.** The barrier our design note treats as
settled at k = 3 is an empirical statement of 2008 [achlioptascojaoghlan2008] that
[marino2016bsp] has since falsified for that value of k.

## The UNSAT side: what is actually held

| Object | Best known | Measure | Source |
|---|---|---|---|
| Refutation by local search | `ranger`, PAC for refutation, beats SATZ on HOLE2+f600 (about 0.15 s) | wall clock on hand-built instances | [prestwichlynce2006] |
| Anytime bound on a model count | MBound, high-confidence bounds by XOR streamlining | confidence on the bound | [gomes2006mbound] |
| Count within tolerance and confidence | ApproxMC, by polynomially many complete SAT calls | `(epsilon, delta)` | [chakraborty2013approxmc] |
| Probability that an instance is unsatisfiable | a classifier on polynomial-time features, about 70 per cent accuracy | classification accuracy at the phase transition | [xu2012predictingsat] |
| Probability of unsatisfiability updated by search failure | **nobody** | none | nine phrasings, queries.md |

The last row is the state of the art for our actual question, and the answer is that the row is
empty. The fourth row is the strongest published number in that direction and it uses no search
at all.

## Distributions, which is what a posterior needs

- Per instance, well-tuned SLS on hard random 3-SAT has an exponential RLD
  [hoosstutzle1999aij]. An exponential survival function makes the posterior arithmetic exact
  and makes restarts worthless.
- Across instances, the hardness distribution is long-tailed, Johnson SB approaching lognormal
  [lorenzworz2022longtails], and backtrack search cost profiles are Pareto-Levy
  [gomes2000heavytails]. A family-level survival function is therefore a mixture of exponentials
  and decays far more slowly than any one instance's.
- Distribution-free, the universal strategy has the tail bound
  `P[run > t] <= exp(-t/(64 l_p log t))` [luby1993, Theorem 6], with `l_p` the optimal fixed
  cutoff's expected time, which is unknown and instance-specific.
