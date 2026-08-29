# (e) Neural annealing and policy gradients; (f) GPU parallelism against slow mixing

Part of [2. The map, by line of work](README.md); the sections read in that file's order.

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
