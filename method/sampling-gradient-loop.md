# Gradient and sampling as one loop: the tilted objective, estimated and corrected

Design note, 2026-08-29, the design as proposed: the loop was built as `--obj tilted` in the Python
record (`../gaussian_surrogate/`), then as the `tilted` seed of the library, and measured in
`../benchmark/findings-walk/`; [algorithm.md](algorithm.md) says what survived. Mohamed's idea: not gradient against sampling but the
two feeding each other, the gradient shaping the sampling distribution and the samples making
the gradient more accurate than mean field, so that the guide improves and the formula can be
simplified. Under the product parametrisation this has an exact form.

## The identity (checked by enumeration, n = 9, m = 38, errors 1e-10)

Let x in {-1, 1}^n be independent with natural parameters theta, p = tanh(theta), so that
d log q_theta(x) / d theta_i = x_i - p_i. For any f >= 0, and in particular the tilted
objective f = e^{beta S(x)} with S the satisfied-clause count,

    d/d theta  log E_theta[ e^{beta S} ]  =  E_tilted[x] - p,        E_tilted[.] under q_theta(x) e^{beta S(x)} / Z.

The exact ascent direction of the tilted log-partition is the mean of the tilted samples minus
the current means. Its two limits are the two methods of this branch:

- beta -> 0:  (E_tilted[x] - p) / beta -> Cov_p(x, S) = d mu / d theta, the mean-field gradient
  that `mu` ascends (linear response). Its second order in beta is the mean-variance objective
  of [tilted-objective.md](../gaussian_surrogate/method/tilted-objective.md), whose implicit beta the Gaussian F follows.
- beta -> infinity: E[x | x satisfies F] - p, the mean of the solutions minus p: the
  cross-entropy update with the satisfying assignments as the elite set, and the exact gradient
  of log P(all satisfied), the weighted model count.

## The loop

    repeat
        draw B assignments x^(b) from q_theta                       (GPU: B independent Bernoulli draws)
        move each a few flips toward S = m at inverse temperature beta   (Metropolis on S, or a
                                                                          short WalkSAT walk: the
                                                                          annealed sample)
        weight w_b: annealed-importance-sampling weights if the walk is a Metropolis kernel on S
                    (detailed balance, so the weights exist); after a WalkSAT walk no proposal
                    density exists and the self-normalised e^{beta S} weights are BIASED,
                    which must be measured, not assumed (review Q7)
        g_sample  ←  sum_b w_b x^(b) / sum_b w_b  -  p
        g_closed  ←  beta * d mu / d theta  [+ second-order term from the pairs, if wanted]
        h_sample  ←  (1/S) sum_b (x0_b - p) beta S(x0_b)   on the RAW draws x0_b, whose expectation
                                                          is exactly g_closed (a random quantity
                                                          with known mean: MuProp's mean-field
                                                          Taylor control variate)
        g  ←  g_sample - lambda (h_sample - g_closed)     (the sampled part estimates only what
                                                          mean field misses; the note's first
                                                          version added a constant, a no-op)
        theta ← theta + eta_t g ;  raise beta on a schedule; eta_t decreasing (with constant
                                   smoothing the cross-entropy iteration collapses to a unit
                                   mass with probability 1: Costa, Jones, Kroese 2007)
        if some E_tilted[x_i] is within delta of +-1: fix x_i, simplify F, drop i    (decimation)
    until a sample satisfies F (certified) or the restart budget ends

What each half does for the other. The gradient of the closed form points the sampler where
samples are starved (the large-deviation regime, where a random draw satisfies nothing); the
samples, once the walk has moved them near S = m, carry the correlations the product measure
cannot express, and their mean corrects the direction toward the solution cluster. The same
samples give the empirical covariance of the clause indicators under the tilted measure, which
replaces the closed-form pair sum (the 3 to 86x cost of F) by a Monte Carlo estimate at the cost
of a few flips per sample on the GPU. The variables whose tilted mean saturates are candidates for
fixing, which would be decimation guided by samples rather than by messages; at k = 3 near the
threshold there are clusters with no frozen variable (frozen variables are guaranteed only for
k >= 9), so the trigger has no theory there and the step stays unbuilt until measured.

## What it is, in the field's terms (to be confirmed by the review)

The update theta <- theta + eta (E_tilted[x] - p) is the plain gradient step in the natural
parameters, which to first order is the natural-gradient step in the means (information-geometric
optimisation makes it exact in the means, and for Bernoulli models that recovers PBIL: Ollivier,
Arnold, Auger, Hansen 2017); the cross-entropy method with soft elites is its large-beta form; the subtraction of the
closed-form gradient is a control variate (Rao-Blackwellisation of the score-function estimator
by its mean-field expectation); the walk between draw and weight is annealed or population
importance sampling; fixing saturated variables is backbone or belief-propagation-guided
decimation with the samples in the role of the messages. Names to search: natural evolution
strategies (Wierstra, Schaul, Glasmachers, Sun, Peters, Schmidhuber 2014), cross-entropy method
with smoothing (Rubinstein and Kroese), REINFORCE with baselines and control variates,
Rao-Blackwellised score-function estimators, annealed importance sampling (Neal 2001),
population annealing, variational neural annealing (Hibat-Allah et al. 2021), simulated
annealing on the satisfied-clause count, backbone-guided local search (Zhang, Rangan, Looks
2003), survey-propagation-guided decimation, "linear response" for the beta -> 0 limit.

## What is not claimed

Nothing here escapes the barriers of [anytime-las-vegas.md](anytime-las-vegas.md): the tilted
partition function is #P-hard to evaluate and its sampled gradient is exact only in expectation;
near the random threshold the tilted measure at large beta is the clustered solution space and
sampling it is the hard part (the walk mixes slowly, which is the same obstacle every local
method meets). The measurable claim is the same as before: does this loop raise the per-restart
success probability of the polish, per unit of cost, above `mu` ascent and above a random or
all-false start. A continuous start for probSAT was tried once (Putikhin and Kascheev 2017,
no code, no per-restart number), so the measurement is a replication with a new estimator.
