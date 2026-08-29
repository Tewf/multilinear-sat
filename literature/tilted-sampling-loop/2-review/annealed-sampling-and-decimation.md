# (c) Annealed and population sampling; (d) decimation guided by samples

Part of [2. The map, by line of work](README.md); the sections read in that file's order.

## (c) Annealed and population sampling for the tilted measure

- [neal2001ais] (a): a chain along an annealing sequence with weights that make the estimates
  converge as the number of runs grows. An estimator, not a mixing guarantee.
- Population annealing [hukushima2003popann, machta2010popann] (a); compared with simulated
  annealing and parallel tempering in [wang2015comparingmc] (a), for spin-glass ground states.
- Parallel tempering [hukushima1996exchange, swendsen1986replica]. On the SAT solution space the
  one verified result is negative: local search and parallel tempering "exhibit a sampling bias"
  [mann2010solutionspace] (a). **Not found in the computer science index at all.**
- Where the tilted measure stops being samplable: [mezard2005clustering] (a),
  [krzakala2007gibbs] (a, f), [montanari2008clusters] (f), [achlioptas2008barriers] (f),
  [montanari2006inequalities] (a), [montanari2011reconstruction] (a). Where it is samplable, all
  in a low-density or local-lemma regime: [moitra2019counting] (f), [feng2021ksat] (a),
  [jain2021towards, jain2021atomic] (a), [he2022nearlinear] (a), [galanis2021counting] (f),
  [he2023improved] (a), [chen2022fastsampling] (a). The optimisation barrier is [gamarnik2021ogp]
  (a). **Not found: a peer-reviewed hardness-of-sampling theorem for random k-SAT above the
  clustering threshold.**

## (d) Decimation guided by samples rather than messages

- [zhang2003backbone] (f) runs WalkSAT repeatedly and computes "pseudo-backbone frequencies", "the
  frequencies of literals appearing in all local minima", "as an estimation of the true backbone
  frequencies". The sampled bias steers the walk; **it never fixes a variable**. Journal version
  [zhang2004configuration] (record only); the backbone as an object of study is
  [slaney2001backbones] (f), analysis with no solver.
- Message-guided decimation, for contrast: survey propagation "uses the detailed probabilistic
  information obtained from the surveys in order to fix variables and simplify the problem"
  [braunstein2005sp] (a); the reinforcement variant uses "time-dependent external forcing
  messages on each variable" [chavas2005spreinforcement] (a).
- The precedent we hoped for is **not** [kroc2009decimation] (f): its "local heuristics" are
  syntactic, and sampling appears once, only as ground truth. [kroc2007spreveisited] (a) is
  measurement.
- The precedent that does exist: [machado2025localequations] (a) decimates on marginals of master
  equations for focused Metropolis search and greedy WalkSAT; the marginals are analytic, not
  counted. [cai2017decils] (f) decimates on the single best local-search assignment of the
  previous round, for MaxSAT.
- Frozen variables: [achlioptas2006geometry] (f), [zdeborova2007coloring] (a),
  [molloy2018freezing] (f), and the k = 3 caveat in [mann2010solutionspace] (a).
- Code: `RaffaeleMarino/The-Backtracking-Survey-Propagation-Algorithm-code` [marino_bsp_repo].
  **Not found: any public backbone-guided local search code** (seven `gh` queries).
