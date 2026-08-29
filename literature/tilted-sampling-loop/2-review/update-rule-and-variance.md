# (a) The identity as an update rule; (b) variance reduction

Part of [2. The map, by line of work](README.md); the sections read in that file's order.

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
