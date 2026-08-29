# The map, by line of work

Every entry was fetched during this review; service and identifier in
[references.bib](references.bib). "(a)" the abstract was read now, "(f)" the full text. Numbers
and barriers are in [3-state-of-the-art.md](3-state-of-the-art.md), so this file says only what
each work does and does not do.

**Surveys first.** [krejca2019edatheory] (a) is the runtime theory of univariate
estimation-of-distribution algorithms; its benchmarks are OneMax and LeadingOnes and it names no
combinatorial problem. [mohamed2020mcgrad] (a) is the survey of Monte Carlo gradient estimation.
Between them they cover (a) and (b); neither mentions satisfiability.

## (a) The identity as an update rule

- [wierstra2014nes] (a): natural gradient of expected fitness over a search distribution, Gaussian
  only, no Bernoulli instance and no combinatorial benchmark.
- [ollivier2017igo] (a) is the theorem behind the note: "the cross-entropy method is recovered in
  a particular case", and "for Bernoulli distributions on {0,1}^d, we recover the PBIL algorithm".
  It says nothing about clustered or constrained search spaces.
- Cross-entropy method [rubinstein1999ce, deboer2005cetutorial], with the convergence statement
  about the smoothing parameter in [costa2007ceconvergence] (f).
- Bernoulli estimation-of-distribution algorithms: PBIL [balujacaruana1995pbil], the univariate
  marginal distribution algorithm [muhlenbein1996umda], the factorised distribution algorithm
  [muhlenbein1999fda] (a), Boltzmann selection schedules [mahnig2001sds] (title only). Runtime
  theory: [witt2019umdaonemax, krejca2020umdalower, lehre2018pbillevel, lehre2019bivariate].
- On SAT itself, only [pelikan2003hboa] (record only, MAXSAT) and [churchill2016genotypes] (a,
  MaxSat). **No runtime theory of any such algorithm on SAT was found.**
- The same update elsewhere: reward-weighted regression [peters2007rwr], model-predictive path
  integral control [williams2016mppi], and the two-phase Boltzmann rule [ackley1985boltzmann].

## (b) Variance reduction, and the control variate the note wants

- Score function and its baseline [glynn1990lr, williams1992reinforce].
- [gu2016muprop] (a): "a control variate based on the first-order Taylor expansion of a mean-field
  network", unbiased. The note's construction, done correctly, for neural networks. Extended by
  [titsias2022doublecv] (a) for discrete latent variables.
- Rao-Blackwellisation: exact per-variable expectations, "similar to Gibbs sampling but easily
  parallelisable" [titsias2015localexpectation] (a); variance reduced without changing bias
  [liu2019raoblackwell] (a). Latent-variable models, not optimisation.
- [tang2020escv] (a) has control variates for evolution strategies but needs Markov decision
  process structure; [geffner2020approx] (a) builds one from a quadratic approximation, for
  reparameterised continuous distributions only.
- The cost of the weights: about exp(KL) samples, "necessary and sufficient", with formulas for
  Gibbs measures [chatterjee2018samplesize, agapiou2017is]. Importance sampling on a formula with
  a search inside the proposal is [gogate2011samplesearch] (record only); the annealed-path
  version of the whole loop is [delmoral2006smc].
- **Nobody was found using a closed-form mean-field gradient as the control variate of a sampled
  gradient for SAT.**

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

## (e) Neural annealing, autoregressive samplers, policy gradients for SAT

- The variational-neural-annealing line does not read CNF: [khandoker2023rnnvca] (a) on max-cut,
  nurse scheduling and the travelling salesman; [sanokowski2023vagco, sanokowski2024diffuco] (f)
  on graph problems cast as Ising or quadratic binary models; [ma2024mpvan] (a) on Ising. The
  warning is [inack2022newmanmoore] (a): neural annealing "globally unstable because of highly
  chaotic loss landscapes" on a glassy model.
- Generative samplers over SAT solutions exist but are supervised
  [freivalds2022diffusionsat, mojzisek2025neuralsatsurvey] (a); policy gradient on SAT learns a
  heuristic inside a local search, not a sampler's parameters [yolcu2019learninglocalsearch] (a).
- GFlowNets [bengio2021gfn, bengio2023gfnfoundations] (a); the combinatorial application's
  released code dispatches on four graph problems [zhang2023letflowstell] (f, source).
  **Not found: a GFlowNet for SAT**, paper or code.
- Public code: [pgmaxsat_repo] reads DIMACS and trains an autoregressive sampler by REINFORCE with
  a baseline; [diffsat_repo, nickles2018diffsat] reads DIMACS and samples a multiset of models
  minimising a differentiable cost over sample statistics. **No public cross-entropy or
  evolution-strategy loop on DIMACS was found** (about twenty `gh` queries).

## (f) Does GPU parallelism compensate for slow mixing?

- [margossian2024nestedrhat] (f) is written for "thousands of chains almost as quickly as a single
  chain, using hardware accelerators such as GPUs", and says "the bias does not decrease with the
  number of chains". Ensemble adaptation on such hardware is [hoffman2022ghmc] (a), which removes
  adaptation bias, not non-convergence bias. Finding a solution is the other problem: `B`
  independent tries give `1 - (1 - p)^B`, and that is what parallelism does buy.
- GPU population samplers with throughput: [barash2017gpupa] (f), [fang2014gpupt] (a). Ising only.
- GPU SAT: continuous local search [cen2025massivelyparallel] (f), a hybrid solver
  [dai2025turbosat] (a), and one public GPU discrete local search with no paper [marchsat_repo].
  **Not found: a GPU WalkSAT paper reporting flips per second.**
- SAT samplers and bias: [wei2004samplesat] (f), [gomes2006xorsample] (a),
  [chakraborty2013unigen] (a), [golia2021cmsgen] (f), [dutra2018quicksampler] (f), and the one
  GPU sampler [ardakani2025htsat] (f), which reports throughput and **no** uniformity measure.
  The papers that measure quality are on the CPU; the papers that measure throughput are on the
  GPU; nobody measures both.
- The reframing: dense accessible clusters rather than the typical Gibbs measure
  [baldassi2015subdominant, baldassi2016robustensembles] (a), applied to random k-SAT in
  [baldassi2016localentropy] (a). Hardware built on that idea beats SAT solvers on 3-SAT
  [aadit2022sparseising] (a), on field-programmable gates rather than a GPU.
