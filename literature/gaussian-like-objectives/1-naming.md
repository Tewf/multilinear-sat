# The problem, and what the field calls each piece

**One sentence.** Maximise, over a product measure on the Boolean variables, the probability
that every clause is satisfied, using a closed-form approximation of that probability built
from the mean and the variance of the satisfied-clause count.

## The object being maximised

| Our word | The field's word | Source |
|---|---|---|
| `P(all clauses satisfied)` at `p` | **weighted model count** with literal weights `p_i` | [chavira2008wmc] |
| the same, as a training loss | **semantic loss**, computed exactly by knowledge compilation | [xu2018semanticloss] |
| independence across variables | **product measure**, **naive mean field** | [wu2019van] |
| independence across clauses (`logsum`) | first-order (mean-field) term of the same count | [bissacot2011clusterlll] |
| `U_jk - U_j U_k` correction | **Plefka** second order, **TAP**, **beyond mean field** | [foos2025beyondmeanfield] |
| the tree-exact functional | **Bethe free energy**, minimised by **CCCP** | [yuille2002cccp, bapst2016bethe] |
| our `L_pair` closure | **Kirkwood superposition**, a **cluster expansion** truncated at pairs | [bissacot2011clusterlll] |

Computing the object exactly is `#P`-hard, which is why every method above is an
approximation of it and why an exact counter is a *measurement instrument*, not a rival solver.

## The shape of `F`

`F = Phi((mu - m + 1/2)/sigma)` is strictly increasing in `z = (1/2 - lambda)/sigma`, so the
criterion is the ratio and not the normal law. That ratio has three names, all older than this
branch: the **safety-first criterion** of Roy, maximise the probability of exceeding a target
under a normal approximation [roy1952safetyfirst]; the **deterministic equivalent of a chance
constraint**, `mu + kappa sigma`, in chance-constrained programming [charnes1959chance]; and
the **probability of improvement** acquisition function [kushner1964pi]. The tilted form
`mu + (beta/2) sigma^2` of `tilted-objective.md` is the **mean-variance** or **entropic-risk**
objective, and its `log E[e^{beta S}]` is the **cumulant generating function**.

## The algorithm skeleton, piece by piece

- "Each literal a Bernoulli, sample, update the parameters": the **cross-entropy method**
  [rubinstein1999ce, deboer2005cetutorial], and **estimation of distribution algorithms**
  (univariate marginal distribution algorithm, population-based incremental learning).
- "Take a gradient of an expectation estimated by sampling": the **score function** or
  **REINFORCE** estimator, used exactly this way in variational annealing [wu2019van].
- "Optimise a product distribution's expected cost with an entropy term": **probability
  collectives** [wolpert2006probabilitycollectives]; the annealed version is **variational
  classical annealing** [hibatallah2021vna].
- "The normalised sum of clause indicators is approximately Gaussian": the **central limit
  theorem under local dependence**, by Stein's method [chen2004localdependence]; the competing
  law is the **Chen-Stein Poisson approximation** [arratia1989poisson].
- "Invert the generating function of the count": the **Poisson-binomial** distribution and its
  discrete-Fourier-transform evaluation [hong2013poissonbinomial, poibin_cran].
- "Cumulant or cluster expansion of `log P(N = 0)`": the **abstract polymer gas** and the
  **Lovász Local Lemma** in its cluster-expansion form [bissacot2011clusterlll].

## The name that must not be borrowed

In random k-SAT, the **second-moment method** bounds `P(formula is satisfiable)` by
`E[Z]^2 / E[Z^2]`, where `Z` counts satisfying assignments and the randomness is the
**formula** [achlioptas2006twomoments, achlioptas2004threshold]. Our `mu` and `sigma^2` are
moments of a **clause count** under a product measure on assignments, at a fixed formula and a
fixed `p`. Same two words, different probability space, no result transfers in either
direction. The brief listed both under one heading; they are two questions.

## Why our name differs

"Gaussian surrogate" names our approximation, not the object. Searching for it finds nothing,
which is a statement about the query. The searchable names are the table above.
