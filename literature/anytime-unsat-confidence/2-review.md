# 2. The map, by line of work

"Abstract fetched" means the full abstract was retrieved today from OpenAlex by DOI or from an
arXiv abstract page; "full text" means a PDF was fetched and its text extracted; "record only"
means DBLP or Crossref confirmed the bibliographic entry and nothing more.

## A. One-sided error and the price of a growing UNSAT confidence

- **[schoning1999, schoning2002]** random start plus O(n) walk steps, repeated; the number of
  repetitions is "within a polynomial factor of (2(1-1/k))^n" (abstract fetched). It gives no
  per-try bound free of that polynomial factor, which is what the design note assumed it gives.
  The journal version's algorithm is restated as `SRWA` in the fetched text of
  [lorenzworz2022longtails].
- **[paturi2005ppsz]** ResolveSat, the fastest randomised algorithm for k >= 4 and for unique
  k-SAT (abstract fetched); **[jiangcai2026ppsz]** the current 3-SAT record O*(1.307031578^n)
  (abstract fetched), which is a smaller base than Schöning's 4/3.
- **[impagliazzopaturi2001, impagliazzopaturizane2001]** the exponential time hypothesis and the
  sparsification lemma (record only); worst case only, silent on the average case.
- **[ko1982, zachos1988]** the collapses following from NP inside BPP (record only; both
  publishers and the Complexity Zoo returned 403, so neither statement was re-verified).
- **[trevisan2002rp, vadhan2007lasvegas]** fetched definitions of RP, coRP, ZPP and Las Vegas,
  used below to fix which class the design note's algorithm lands in.
- **[bensassonwigderson2001]** resolution width lower bounds from clause expansion (abstract
  fetched), re-verifying the resolution leg of `subexponential-sat-map.md`. It bounds refutations,
  not searches on satisfiable instances.

## B. Typical-case polynomial algorithms for random k-SAT

- **[cojaoghlan2010fix]** Fix is polynomial whp below `(1 - eps_k) 2^k ln(k)/k`;
  **[cojaoghlanfrieze2014walksat]** WalkSAT succeeds "in polynomial time with high probability"
  below `rho 2^k/k`; **[cojaoghlan2017walksatstalls]** WalkSAT fails whp above
  `c 2^k ln^2 k / k`. All three abstracts fetched, all asymptotic in k, none a constant at k = 3.
- **[alekhnovichbensasson2006]** linear-time random walk at small density on random 3-CNF
  (record only).
- **[cojaoghlan2011bpdecimation]** belief propagation guided decimation provably fails at
  `rho r_k/k` (abstract fetched), against experiments suggesting it worked near `r_k`.
- **[braunstein2005sp]** survey propagation, surveys over clusters (abstract fetched); empirical,
  no running-time theorem.
- **[achlioptascojaoghlan2008]** the shattering transition, whose location "corresponds to the
  point where all known polynomial-time algorithms fail" (abstract fetched). True in 2008; the
  design note repeats it as though still true at k = 3.
- **[marino2016bsp]** backtracking survey propagation, full text fetched: at K = 3 its threshold
  "practically coincide[s] with the SAT-UNSAT threshold", `alpha_a approx 4.268` against
  `alpha_s = 4.2667`, at N up to 10^6, in practically linear time; SID reaches 4.2525 in
  `O(N log N)`; the rigidity threshold is `alpha_r = 4.2635(10)`.
- **[seitz2005focused]** focused local search, WalkSAT included, keeps a linear-time regime "well
  into ratios alpha > 4.2" (abstract fetched).
- **[angelini2026timescaling]** there is one algorithmic threshold per time scaling, not one
  threshold (abstract fetched); the single barrier number our note uses does not exist.
- **[gamarnik2021ogp, kizildag2025ogpthresholds, breslerhuang2021lowdegree]** overlap gap and
  low-degree hardness, all asymptotic in k; the sharp m-OGP thresholds hold for "all k growing
  mildly with the number of Boolean variables", so not at fixed k = 3.
- **[dingslysun2022threshold]** the threshold itself is a theorem only for large k.

## C. Run-length distributions, restarts, runtime prediction

- **[hoos1999pac]** PAC, plus the flat statement that SLS "cannot be used to prove that a given
  problem instance is unsatisfiable" (full text fetched).
- **[hoosstutzle1999aij]** full text fetched: on hard random 3-SAT at approximately optimal noise
  WalkSAT's RLD is exponential, so "the probability of finding a solution within a fixed time
  interval is independent of the run-time spent before". Restarts buy nothing there.
- **[gomes2000heavytails, gomesselmankautz1998]** Pareto-Levy cost profiles in backtrack search,
  removed by rapid randomised restarts (record only; quoted through the fetched text of
  [lorenzworz2022longtails]).
- **[luby1993]** full text fetched: `S_univ`; Theorem 5, `T <= 192 l_p (log l_p + 5)`; Theorem 6,
  `P[run > t] <= exp(-t/(64 l_p log t))`; Theorem 7, the logarithmic factor is unavoidable.
- **[lorenzworz2022longtails, lorenz2017restarts]** full text fetched for the first: the hardness
  distribution across formulas is Johnson SB approaching lognormal, hence long-tailed, and
  restarts are proved useful there; Schöning's walk is itself approximately Johnson SB.
- **[hoosstutzle2000jar]** the empirical evaluation the RLD vocabulary comes from (record only;
  OpenAlex stores no abstract, so nothing is claimed here about its content).
- **[leytonbrown2009ehm, hutter2014runtimeprediction, xu2008satzilla]** empirical hardness models
  and portfolios; **[haimwalsh2009onlineestimation]** online estimation of the remaining cost of a
  CDCL run, restarts handled explicitly (abstract fetched). All predict time, never status.
- **[wald1945]** the sequential probability ratio test (record only).

## D. Incomplete methods aimed at unsatisfiability

- **[prestwichlynce2006]** full text fetched: a meta-encoding whose solutions are refutations, and
  `ranger`, a greedy randomised resolution algorithm "PAC if p_i > 0, p_i, p_t, p_g < 1, w = n and
  k >= n + 1", refuting HOLE2+f600 in about 0.15 seconds. It reports no probability at any time.
- **[audemardsimon2007gunsat]** the other local search refuter (record via web search and the ACM
  DL entry only; abstract not fetched).
- **[chakraborty2013approxmc, meelgroup_approxmc]** counts to a tolerance and confidence "by
  issuing a polynomial number of calls to a SAT solver" (abstract fetched; repository
  `gh repo view` verified), so its zero is a complete solver's answer, not an anytime confidence.
- **[gomes2006mbound]** XOR streamlining to the edge of unsatisfiability gives high-confidence
  bounds on the count (AAAI abstract fetched): the nearest published probabilistic statement about
  a formula, and it is about a count, not a status.
- **[xu2012predictingsat]** about 70 per cent satisfiability classification accuracy at the phase
  transition from polynomial-time features, stable in size (abstract fetched): a prior on UNSAT,
  computed before any search.
- **[caizhang2021deepcooperation, biere_kissat]** CDCL and SLS in cooperation; kissat's
  `rephase_walking()` calls `kissat_walk()` (gh api on both sources). A phase heuristic inside a
  complete solver, not a portfolio half.

## E. Relaxation as the seed of a local search

- **[putikhin2017continuousinit]** "a heuristic for finding an initial assignment based on
  non-linear optimization of continuous extension of given Boolean formula ... implemented in
  ProbSAT solver" (abstract fetched). Four pages, one recorded citation, no public code found.
- **[fu2021initialassignment]** non-random initial assignments from the clause-to-variable ratio,
  bolted onto six state-of-the-art SLS solvers (abstract fetched).
- **[zhang2020nlocalsat, myxxxsquared_nlocalsat]** the neural version of the same protocol, 27 to
  62 per cent improvement on the 2018 random track, with public code (README read).
- **[hofstadler_galoissat]** the only public repository matching "GaloisSAT", "a satisfiability
  solver for polynomial systems over small finite fields", unrelated to continuous seeding; the
  parent brief's TurboSAT returns zero repositories.
- **[kautzselman2003tenchallengesredux]** the six-year progress report on the ten challenges
  (record only), the companion to [selman1997tenchallenges].
