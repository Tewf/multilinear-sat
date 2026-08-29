# Positioning: the design note, section by section

Verdicts: **theorem** (known, cite it), **measured elsewhere** (a number exists, cite it),
**open** (nobody found doing it), **wrong** (the note's sentence is quoted and corrected).

## "The identity (checked by enumeration, n = 9, m = 38, errors 1e-10)"

**Theorem.** It is the gradient of the log-partition function of the exponential family obtained
by adjoining `S` to the sufficient statistics [wainwrightjordan2008], equivalently the
score-function identity [glynn1990lr, williams1992reinforce, mohamed2020mcgrad], equivalently the
two-phase Boltzmann-machine rule [ackley1985boltzmann]. The enumeration confirmed textbook
algebra. Nothing here is ours.

## The `beta -> 0` limit

**Theorem**, and correctly stated: `S` is multilinear, so `Cov_p(x_i, S) = (1 - p_i^2)
dE[S]/dp_i = dmu/dtheta_i`. "Linear response" is the field's name.

## The `beta -> infinity` limit

**Theorem, and already named in this repository.** `E[x | SAT] - p` is the exact gradient of the
log weighted model count, which is the gradient of the semantic loss
[xu2018semanticloss, `gaussian-like-objectives/2-review/README.md`]; the update with the satisfying set
as the elite is the cross-entropy method at its rare-event limit [rubinstein1999ce].

## "a natural-gradient step in the exponential family": **wrong as written**

The note says: *"The update theta <- theta + eta (E_tilted[x] - p) is a natural-gradient step in
the exponential family (the Fisher metric is what removes the (1 - p^2) factors)"*.
`E_tilted[x] - p` is the **ordinary** gradient in the natural parameter `theta` and the
**natural** gradient in the mean parameter `p`. Adding it to `theta` is therefore plain gradient
ascent, not a natural-gradient step, and it is not invariant under reparametrisation. The
information-geometric optimisation flow makes the correct version explicit: for Bernoulli
distributions "we recover the PBIL algorithm" [ollivier2017igo], and PBIL steps `p`. Fix: step
`p <- (1 - eta) p + eta * (weighted sample mean)`, or divide by `1 - p^2` before stepping `theta`.

## "g  <-  g_closed + ( g_sample - g_closed )": **wrong, it is a no-op**

The note's parenthesis is right about the intent: *"the closed form is a control variate ... so
the sampled part estimates only what mean field misses, the correlations"*. The line is not.
`g_closed` is deterministic, so `g_closed + (g_sample - g_closed) = g_sample` exactly, with the
same variance. A control variate must be a **random** variable with known mean, subtracted
inside the sample average. The construction the note wants exists: build the first-order Taylor
surrogate of `e^{beta S}` about `p`, whose score-function expectation is closed form under the
product measure, and average `(e^{beta S(x_b)} - surrogate(x_b)) (x_b - p)` over the batch. That
is exactly MuProp, "a control variate based on the first-order Taylor expansion of a mean-field
network" [gu2016muprop], extended in [titsias2022doublecv]. **Open** for SAT: no one was found
doing it there.

## "weight w_b ∝ e^{beta S} / (proposal correction) ... the walk makes the proposal informative"

**Wrong, then measured elsewhere.** After "a short WalkSAT walk" the proposal density is not
computable, so the correction cannot be formed and the weights are not the weights of any
measure. Annealed importance sampling is the construction that keeps computable weights: kernels
reversible with respect to the intermediate tilted measures, weights a product of ratios along
the path [neal2001ais]. Even with correct weights, self-normalised importance sampling needs
about `exp(KL)` samples, "necessary and sufficient", with explicit formulas for Gibbs measures
[chatterjee2018samplesize, agapiou2017is]. And the bias is measured: on the 3-SAT solution space
"standard stochastic local-search (SLS) algorithms like 'ASAT' and 'MCMCMC' (also known as
'parallel tempering') exhibit a sampling bias" [mann2010solutionspace].

## "theta <- theta + eta g ; raise beta on a schedule"

**Measured elsewhere.** With a constant smoothing parameter the cross-entropy method's
distribution "converges with probability 1 to a unit mass" and the probability of having found
the optimum is only "arbitrarily close to 1"; eventual generation with probability 1 "can only be
achieved by using a sequence of decreasing smoothing parameters" [costa2007ceconvergence]. A
fixed `eta` will freeze the loop on a wrong assignment. Boltzmann selection schedules for exactly
this update are published [mahnig2001sds].

## "if some E_tilted[x_i] is within delta of +-1: fix x_i ... decimation"

**Open, with one named competitor and one theorem against the trigger.** Sample-derived variable
frequencies from a pool of WalkSAT local minima exist, as "pseudo-backbone frequencies", but they
steer the walk and never decimate [zhang2003backbone]; decimation on marginals of the *dynamics*
rather than of belief propagation is done analytically and "achieves a threshold that surpasses
the clustering transition, outperforming conventional methods like Belief Propagation-guided
decimation" [machado2025localequations]. Monte Carlo marginals plus decimation is the empty cell.
Against the trigger: frozen variables are guaranteed in every cluster only for `k >= 9`, and "it
remains open whether frozen variables exist for `k <= 8`" [achlioptas2006geometry]; at `k = 3`
near the threshold there are "always clusters without any frozen variables"
[mann2010solutionspace]. A saturation test has no theory behind it on uf250.

## "the empirical covariance of the clause indicators ... replaces the closed-form pair sum"

**Open.** No precedent found. The arithmetic is favourable (about `9 alpha^2 n / 2` pairs against
`B` samples), the statistics are not free: each covariance entry carries a `1/sqrt(B)` error and
the pair sum adds about `4100` of them on uf50 alone (`method/baselines.md`).

## "What is not claimed"

**Correct, and sharper than written.** Rigorous sampling of random k-SAT solutions is known only
at density `alpha <~ 2^{k/3}` [he2023improved] or `2^{0.039 k}` in near-linear time
[chen2022fastsampling]; at `k = 3` both are below `2`, and uf250 sits at `4.26`. Local Markov
chains are "effective up to the clustering phase transition" `alpha_d(3) = 3.86`
[krzakala2007gibbs, montanari2008clusters], and the overlap gap property rules out stable
algorithms [gamarnik2021ogp]. **Not found**: a peer-reviewed hardness-of-sampling theorem for
random k-SAT above clustering, so "hard" here means "no algorithm known", not "proved hard".

## One correction to a sibling review

`gaussian-like-objectives/5-plan.md` rejects *"Sampling to estimate the objective"* as "redundant
where the closed form exists, starved where it does not". That rejection stands for the
*objective*; this note samples the *correction* to a closed-form gradient, which is a different
proposal. The "starved" half of the objection survives intact as [chatterjee2018samplesize].
