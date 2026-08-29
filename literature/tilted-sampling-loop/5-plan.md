# Plan: what to build, against what, measured by what

## Two corrections that cost nothing and must come first

1. **Step the mean, not the natural parameter.** `p <- (1 - eta) p + eta * (weighted sample mean)`
   is the natural-gradient step [ollivier2017igo]; `theta <- theta + eta (E_tilted[x] - p)` is not.
2. **Make the control variate a control variate.** Subtract, per sample, the score-function
   estimator of the first-order Taylor surrogate of `e^{beta S}` about `p`, whose expectation is
   closed form under the product measure [gu2016muprop]. As written the line is algebraically
   `g_sample` and reduces nothing.

Both are edits to a loop that does not exist yet, so they are free now and expensive later.

## The measurement that decides everything, and it is not a solver run

**The bias of the sampled tilted mean.** Nobody publishes sample quality and throughput together
(section (f) of [3-state-of-the-art.md](3-state-of-the-art.md)), so this number is both the gate
on our own loop and the gap in the field.

- **Ground truth**: exact enumeration of `E_tilted[x]` at `n <= 20`; at `n = 50`, the weighted
  model count with `Ganak` under the same literal weights, as `gaussian-like-objectives/5-plan.md`
  already specifies for the objective.
- **Estimate**: the loop's own `sum_b w_b x_b / sum_b w_b`, as a function of the batch `B`
  (64, 512, 4096) and of the number of walk flips per sample (0, 1, 10, 100).
- **Report bias and variance separately**, which is the whole point: more chains cut the variance
  and leave the bias, "the bias does not decrease with the number of chains"
  [margossian2024nestedrhat]. Plot both against `B` at densities 3.0, 3.86 (the clustering
  threshold [montanari2008clusters]) and 4.26.
- **Decide**: if the bias at `beta` large is comparable to the mean-field error the loop is meant
  to correct, the loop corrects nothing and the branch closes here.

## Then, and only then, the algorithmic comparison

**Baselines.**

- **In the repository**: the `mu` ascent on the shared scaffolding (`method/baselines.md`), whose
  numbers are already in `findings.md`, plus the polish-only control that `findings.md` flags as
  missing. This is the primary control.
- **Public code for the loop's own family, nearest available.** There is no cross-entropy or
  evolution-strategy solver for DIMACS. The two nearest are [pgmaxsat_repo], which reads DIMACS
  and trains an autoregressive sampler by REINFORCE with a baseline, and [edaspy_repo], whose
  `UMDAd` and `PBIL` are maintained and MIT-licensed and need a clause-count objective wired in.
  [pypop_repo] does not apply: it is continuous only.
- **Decimation**: [marino_bsp_repo] for survey-inspired and backtracking survey-propagation
  decimation. The published number to beat is [machado2025localequations], whose decimation
  "achieves a threshold that surpasses the clustering transition".
- **Sampling quality**: [cmsgen_repo] with the Barbarik tester as the CPU yardstick
  [golia2021cmsgen]; **throughput**: [htsat_repo], 20267 unique solutions per second on a V100
  [ardakani2025htsat], and [fastfouriersat_repo] on the continuous side.
- **Solving**: `probSAT` on uniform random 3-SAT, and on parity `xnfSAT` against its published
  MM-Challenge-1 table (`fft-walksat-las-vegas/README.md`).

**"Better" is the per-restart success probability per unit cost**: the median cost of a restart
divided by the fraction of restarts that reach a solution, at fixed hardware, seeds and cap, on
uf250-1065 and on the parity instances. `findings.md` gives the target to beat: `mu` at 77 % under
the cap with a 2.0 s median, and 0 restarts out of 512 reaching a solution on uf250 without the
polish.

## What to reject on paper, and why

1. **The weighted walk as written.** After a WalkSAT walk the proposal has no computable density,
   so `w_b` is not a weight. Either use annealed importance sampling, whose weights are products
   of ratios along a path of reversible kernels [neal2001ais], or drop the weights and declare the
   estimator biased.
2. **Large `beta` with self-normalised weights.** About `exp(KL)` samples are needed, "necessary
   and sufficient" [chatterjee2018samplesize]; at `beta -> infinity` that divergence is extensive.
   Keep `beta` where the effective sample size is measurable, and measure it.
3. **A constant learning rate with a rising `beta`.** The distribution "converges with probability
   1 to a unit mass"; probability 1 of finding the optimum "can only be achieved by using a
   sequence of decreasing smoothing parameters" [costa2007ceconvergence]. Schedule `eta`.
4. **Decimation on saturated tilted marginals, at `k = 3`, as a principled step.** Frozen variables
   are guaranteed in every cluster only for `k >= 9` [achlioptas2006geometry], and near `alpha_s`
   at `k = 3` there are "always clusters without any frozen variables" [mann2010solutionspace].
   Keep it as a heuristic, measure it, do not justify it by the freezing theory.
5. **Writing a new autoregressive or neural sampler.** The whole variational-neural-annealing line
   has no CNF reader, its own authors report annealing "globally unstable because of highly chaotic
   loss landscapes" [inack2022newmanmoore], and a differentiable SAT sampler that reads DIMACS and
   optimises a cost over sample statistics already exists [diffsat_repo].
6. **"Slow to sample, but the GPU is enough" as stated.** It is true for finding, where `B`
   independent tries give `1 - (1 - p)^B`, and false for the tilted mean, where the bias is
   invariant to `B` [margossian2024nestedrhat]. Split the claim before relying on it.

## One reframing worth testing rather than rejecting

If the biased, unmixed sample lands in dense accessible clusters rather than on the typical Gibbs
measure, the bias is the target and not the defect: local entropy reaches "sub-dominant clusters
of optimal solutions in a small number of steps, while standard Simulated Annealing either
requires extremely long cooling procedures or just fails" on random k-SAT
[baldassi2016localentropy]. The fidelity experiment above measures the bias; comparing it against
a replicated (robust ensemble) objective [baldassi2016robustensembles] on the same scaffolding is
one extra `--obj` and tells us which of the two readings is right.

## Order

1. The two corrections (edits to a design note).
2. The bias-versus-throughput measurement. No solver, no GPU cluster, one counter.
3. `probSAT`, the polish-only control, and the per-restart table, only if step 2 passes.
4. Decimation, and the local-entropy comparison, last.
