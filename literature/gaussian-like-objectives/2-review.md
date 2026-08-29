# The map, by line of work

Every entry was fetched during this review; service and identifier are in
[references.bib](references.bib). "Abstract" means the abstract was read now, "full text" that
the body was read now.

**Surveys, read first for the vocabulary.** [velasquez2025dataless] surveys optimisation where a
single instance is encoded in a network and solved by training it, with no data, which is our
setting; its abstract names no SAT objective. [mojzisek2025neuralsatsurvey] shows graph networks
implicitly performing "a process very similar to continuous relaxations of MaxSAT". Neither
surveys the objectives themselves, which is why the map below had to be built term by term.

## The objective as an exact probability

- **Weighted model counting** [chavira2008wmc]. `P(all clauses satisfied)` under independent
  literal weights is a weighted model count: `#P`-hard, with exact solvers. Abstract.
- **Semantic loss** [xu2018semanticloss, semanticloss_repo]. The negative logarithm of the
  probability that a constraint holds under independent Bernoulli outputs, computed exactly by
  knowledge compilation and descended by gradient. Abstract plus code. Our objective, exact,
  used for neural training rather than for solving.
- **Cluster expansion form of the Lovász Local Lemma** [bissacot2011clusterlll]. Relates
  `P(no bad event)` under a product measure to the independent-set polynomial and the polymer
  gas and expands its logarithm. Abstract. The published form of `pair-expansion.md`.
- **Approximate counting and the Local Lemma** [moitra2019counting]. Approximate counting of
  satisfying assignments at width logarithmic in the degree. Abstract. Says where the object is
  tractable; is not an optimiser.

## Sampling versions of the same skeleton

- **Cross-entropy method** [rubinstein1999ce, deboer2005cetutorial]. Optimisation as rare-event
  estimation under a Bernoulli product law: sample, keep an elite fraction, update the parameters
  by minimising cross-entropy. Steps 1, 4 and 6 of the original skeleton, published in 1999.
- **Cross-entropy and splitting for counting satisfying assignments**
  [rubinsteinkroese2007satcount, rubinstein2008semiiterative, botev2008splitting]. The same
  machinery aimed at SAT counting; the 2007 item is a manuscript with an abstract only.
- **Probability collectives** [wolpert2006probabilitycollectives]. Minimise over product
  distributions an expected cost plus an entropy term, by gradient and Newton steps. Abstract.
- **Variational autoregressive networks** [wu2019van] and **variational neural annealing**
  [hibatallah2021vna]. Minimise a variational free energy by policy-gradient updates of a
  sampler; the mean-field case is a product of Bernoullis. Abstract plus code. Spin glasses
  only; the public code has no SAT reader.
- **Learning genotypes with neural networks** [churchill2016genotypes]. Learned samplers against
  population-based incremental learning on MaxSAT. Abstract confirms MaxSAT.

## Mean-field corrections and message passing

- **Information-based neural approach to constraint satisfaction** [jonsson2001informationcsp].
  An annealing algorithm whose free energy differs from the conventional mean-field one, tested
  on k-SAT and reported comparable to GSAT with walk. Abstract. The closest published ancestor
  of "correct the mean-field objective, then descend it" for SAT.
- **CCCP for the Bethe and Kikuchi free energies** [yuille2002cccp] and **Harnessing the Bethe
  free energy** [bapst2016bethe]. A convergent direct minimiser of the tree-exact functional,
  and that functional as the right object for random constraint satisfaction. Abstracts.
- **Belief-propagation-guided decimation** [montanari2007bpdecimation] and its failure
  [cojaoghlan2017bpdecimation]. The correlated-marginal alternative to a product measure, and
  the proof that decimating on those marginals fails below the threshold. Abstracts.
- **Beyond-mean-field fluctuations for constraint satisfaction** [foos2025beyondmeanfield].
  Beyond-mean-field means and variances for MAX-2-SAT as a spin glass, with Glauber dynamics.
  Abstract. Same vocabulary, different mechanism: it corrects a dynamics, not an objective.

## The continuous SAT line and its stated objection

- **GaloisSAT** [kim2026galoissat]. Full text: "we do not directly encode the global conjunction
  of all clauses (the and operation) as a product, since a single unsatisfied clause would
  reduce the product to zero and eliminate gradient information"; it uses the sum instead.
- **torchmSAT** [hosny2024torchmsat]. One differentiable function approximating MaxSAT, trained
  per instance on a GPU. Abstract. The objective is the count, not a probability.
- **FourierCSP** [cen2025fouriercsp] and **unconstrained hybrid SAT** [zhang2025outofbox].
  Walsh-Fourier continuous local search on finite-domain CSP with mirror descent, and the box
  constraint replaced by penalties. Abstracts. Both change the geometry, not the objective.
- **Quantum-inspired approximations to CSP** [lanham2022quantuminspired]. Approximates the
  uniform measure over satisfying assignments in the Fourier domain. Abstract.

## Probabilistic-method losses, and the count's law

- **Erdős goes neural** [karalias2020erdos]. A loss from the probabilistic method whose low value
  certifies that the distribution contains a valid low-cost solution, then derandomised.
  Abstract. First-moment reasoning as a loss, never second-moment.
- **Principled objective relaxation** [wang2022principledrelaxation]. Entry-wise concavity of the
  relaxed objective makes a low loss a guarantee on the rounded solution. Abstract.
- **Physics-inspired graph networks** [schuetz2022pignn]. Relaxes the Hamiltonian to a
  differentiable loss and projects. Abstract. The expectation objective, our `mu`, at scale.
- **Normal approximation under local dependence** [chen2004localdependence], **Chen-Stein
  Poisson approximation** [arratia1989poisson], **Poisson-binomial computation**
  [hong2013poissonbinomial, poibin_cran]. The tools `regimes.md` uses; nothing found applies any
  of them as an optimisation objective.
- **Second moment for thresholds** [achlioptas2006twomoments, achlioptas2004threshold]. A proof
  technique over random formulas, not an algorithm. Abstracts.
