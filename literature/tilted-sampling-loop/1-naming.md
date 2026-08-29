# The problem in one sentence, and what the field calls it

**Our sentence.** Alternate a closed-form mean-field gradient with annealed samples from the
tilted measure, each correcting the other, and decimate on the sampled marginals, to find a
satisfying assignment.

## The identity has four names, all older than the note

`d/d theta log E_theta[e^{beta S}] = E_tilted[x] - p` is:

1. the **score-function** or **likelihood-ratio** identity, `grad E[f] = E[f grad log q]`
   [glynn1990lr, williams1992reinforce], surveyed with its two rivals in [mohamed2020mcgrad];
2. the gradient of the **log-partition function of an exponential family**, equal to the mean
   parameter of the tilted member [wainwrightjordan2008];
3. the **positive phase minus negative phase** of the Boltzmann-machine learning rule
   [ackley1985boltzmann];
4. the **natural gradient in the mean parametrisation** of the Bernoulli family: the
   information-geometric optimisation flow reduces to exactly this and "we recover the PBIL
   algorithm" for Bernoulli distributions [ollivier2017igo].

Careful with (4): `E_tilted[x] - p` is the *ordinary* gradient in the natural parameter theta
and the *natural* gradient in the mean parameter p. The note steps theta with it; PBIL, the
univariate marginal distribution algorithm, the cross-entropy method and IGO step p with it.
See [4-positioning.md](4-positioning.md).

## The loop's four moves, each with a name

| The note's move | The field's name |
|---|---|
| sample from `q_theta`, weight by `e^{beta S}`, move the mean to the weighted mean | **cross-entropy method** with Boltzmann (soft) selection [rubinstein1999ce, deboer2005cetutorial]; **Boltzmann-selection estimation-of-distribution algorithm** [mahnig2001sds]; **reward-weighted regression** [peters2007rwr]; **model-predictive path integral** control [williams2016mppi] |
| the same update read as a distribution step | **natural evolution strategies** [wierstra2014nes], **information-geometric optimisation** [ollivier2017igo] |
| raise `beta` on a schedule between draws | **annealed importance sampling** [neal2001ais], **population annealing**, **simulated annealing** on the satisfied-clause count |
| subtract the closed-form part so only the residual is sampled | **control variate**, specifically the **first-order Taylor expansion of a mean-field network** [gu2016muprop, titsias2022doublecv]; **Rao-Blackwellised score function** [titsias2015localexpectation, liu2019raoblackwell] |
| fix variables whose sampled marginal saturates | **decimation**; with messages it is belief-propagation- or survey-propagation-guided decimation, with samples it is **backbone-guided** search |

## Vocabulary we were missing

- **Exponential tilting** (Esscher transform): `q_theta(x) e^{beta S}/Z` is the tilted or
  Gibbs measure; `log E[e^{beta S}]` is its **cumulant generating function**, and `beta` is
  the **entropic-risk** parameter. Rare-event simulation calls the search for the right
  tilting **adaptive importance sampling**, which is where the cross-entropy method was born.
- **Self-normalised importance sampling** is the name of `sum_b w_b x_b / sum_b w_b`: biased
  at order `1/B`, and its required `B` is `exp(KL)` [chatterjee2018samplesize].
- **Frozen variable**, **backbone**, **clustering** and **dynamical threshold** name what the
  note calls "the solution cluster"; **overlap gap property** names the barrier
  [gamarnik2021ogp].

## Why our name differs

We named the object by the method we had in mind ("gradient and sampling as one loop"). The
field names it by the distribution being moved: it is an estimation-of-distribution algorithm
on a Bernoulli product with Boltzmann selection, an annealing schedule and decimation. Every
piece has a literature; the assembly is what has to be defended.
