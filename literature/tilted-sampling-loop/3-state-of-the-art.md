# State of the art: records, measures, hardware, and the two kinds of bound

## Who holds the record, and on what

- **The loop's own family has no record on SAT.** No published cross-entropy method or evolution
  strategy solver number on any SAT benchmark was found, and no public code runs such a loop on
  DIMACS. The nearest published applications of a Bernoulli estimation-of-distribution algorithm
  to satisfiability are hierarchical Bayesian optimisation on MAXSAT [pelikan2003hboa] (record
  verified, no number retrieved) and learned samplers on MaxSat [churchill2016genotypes].
- **Sample-guided decimation**: [machado2025localequations], PNAS 2025, decimating on the
  marginals of master equations for focused Metropolis search and greedy WalkSAT, "achieves a
  threshold that surpasses the clustering transition, outperforming conventional methods like
  Belief Propagation-guided decimation" on random 3-SAT. This is the number to beat for the
  decimation half. Message-guided decimation's usable code is
  `RaffaeleMarino/The-Backtracking-Survey-Propagation-Algorithm-code`.
- **Stochastic local search on uniform random 3-SAT**: probSAT and kissat, per the sibling review
  `fft-walksat-las-vegas/README.md`. On the parity instances: xnfSAT on MM-Challenge-1, and
  FastFourierSAT solving 300 of 300 parity-learning instances at a 60 s cap on an A100.
- **In this repository**, on an RTX 4060 with one seed: `mu` solves 77 % of uf250-1065 under the
  time cap at a 2.0 s median, `F` 38 % at 9.6 s; without the polish, 512 restarts of `mu` reach a
  solution on 0.39 % of uf100-430 tries and 0 % of uf250 (`findings.md`). That zero is the
  quantity the loop has to move.

## Upper bounds: what provably works, and where

- **UMDA on OneMax**: O(mu n) for mu >= c log n, and O(mu sqrt n) for mu >= c' sqrt(n log n)
  [witt2019umdaonemax]. **PBIL on LeadingOnes**: O(n lambda log lambda + n^2) for
  lambda = Omega(log n) [lehre2018pbillevel]. These are the only runtime theorems for this family,
  and their benchmarks are not constraint satisfaction [krejca2019edatheory].
- **Cross-entropy method**: with a constant smoothing parameter the distribution converges with
  probability 1 to a unit mass and finds the optimum with probability arbitrarily close to 1;
  probability 1 requires decreasing smoothing [costa2007ceconvergence].
- **Sampling satisfying assignments in polynomial time.** Bounded degree: d <~ 2^{k/60}
  [moitra2019counting]; k >= 20 log k + 20 log d + 60 [feng2021ksat]; Delta <~ 2^{k/5.741}
  [jain2021atomic]; a Delta^5 local-lemma condition in near-linear time [he2022nearlinear].
  Random formulas by density: alpha < 2^{k/300}/k^3 [galanis2021counting], improved to
  alpha <~ 2^{k/3} [he2023improved], and alpha <= 2^{0.039 k} in n^{1+o_k(1)} time
  [chen2022fastsampling]. **At k = 3 all of these are densities below 2.** uf250 is at 4.26.

## Lower bounds and barriers: a different claim

- **UMDA on OneMax**: Omega(mu sqrt n + n log n) [krejca2020umdalower]; univariate models fail on
  deception, where bivariate ones may help [lehre2019bivariate].
- **Importance sampling**: about exp(KL(target || proposal)) samples are "necessary and
  sufficient" [chatterjee2018samplesize, agapiou2017is]. For the tilted measure at large beta
  against a product measure this divergence is extensive in n.
- **The clustered phase**: shattering is rigorous for (1 + eps)(2^k/k) ln k <= r <=
  (1 - eps) 2^k ln 2 [achlioptas2008barriers]; alpha_d(3) = 3.86 against alpha_s(3) = 4.267, and
  "local Monte Carlo Markov Chain strategies are effective up to the clustering phase transition"
  [krzakala2007gibbs, montanari2008clusters]. The dynamical transition is proved to be purely
  dynamical [montanari2006inequalities].
- **The overlap gap property** rules out stable algorithms [gamarnik2021ogp]. It is a statement
  about **optimisation**, not about sampling, and it is not an NP-hardness result.
- **Counting hardness** is worst case and bounded degree, not random and not above clustering
  [bezakova2019correlationdecay, galanis2021inapprox]. **Not found**: a peer-reviewed
  hardness-of-sampling theorem for random k-SAT above the clustering threshold.
- **Frozen variables** are guaranteed in every cluster only for k >= 9 [achlioptas2006geometry],
  and at k = 3 near the threshold there are clusters with none [mann2010solutionspace].

## (f) Does the GPU compensate for slow mixing? The records, and the missing measurement

- **Throughput records.** Population annealing: "10 ps per spin flip", about 230 times a serial
  CPU code and about 2300 with multi-spin coding, on a Tesla K80 [barash2017gpupa]. Parallel
  tempering: "33.5 picoseconds per spin flip attempt" on the Edwards-Anderson model
  [fang2014gpupt]. GPU SAT sampling: 20267 unique solutions per second on a single V100, 33.6x to
  523.6x over CPU samplers [ardakani2025htsat]. Continuous local search on SAT: gradients "100+
  times faster" than the CPU prototype [cen2025massivelyparallel]; a hybrid solver "up to over
  200x" on a DGX GB200 [dai2025turbosat]. A sparse Ising machine on field-programmable hardware
  beats "competition-winning SAT solvers (by 4-700x in runtime to reach 95% accuracy)" on 3-SAT
  [aadit2022sparseising].
- **Quality records, all on the CPU.** XOR constraints, "provably arbitrarily close to uniform"
  [gomes2006xorsample]; UniGen with guarantees [chakraborty2013unigen]; a tester accepting CMSGen
  and UniGen3 and rejecting QuickSampler on all 50 instances [golia2021cmsgen].
- **The bound that answers the claim.** More chains reduce the persistent variance linearly and
  leave the bias untouched: "the bias does not decrease with the number of chains"
  [margossian2024nestedrhat]. So the GPU buys `1 - (1 - p)^B` on the *finding* problem and
  nothing on the *bias* of the estimated tilted mean. This is a bound, not a benchmark, and it
  is the reason the claim "slow to sample, but the GPU is enough" is half true.
- **No result holds both ends.** Not found: any sampler reporting sample quality against
  throughput on a GPU. That gap is the measurement this branch can occupy cheaply.

## Hardware, so the numbers can be compared

`findings.md` is one RTX 4060 Mobile, batch 64 and 512, one seed, Python and PyTorch; a step of
`F` costs 3.1 to 26 times a step of `mu` at batch 64 and up to 86 at batch 512. Published
comparisons in this area run on very different machines: an A100 for FastFourierSAT, a Xeon
E5-2690 for xnfSAT, an NVIDIA DGX GB200 node for [dai2025turbosat]. No result below is
transferable without re-running it here.
