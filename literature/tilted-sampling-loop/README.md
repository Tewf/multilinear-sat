# A loop where the mean-field gradient shapes the sampler and annealed samples correct it

**The question.** `method/sampling-gradient-loop.md` proposes to alternate a closed-form
mean-field gradient with annealed, importance-weighted samples of the tilted measure
`q_theta(x) e^{beta S(x)}`, using the closed form as a control variate and the samples for
decimation. Has the field done this, and does the assembly hold?

## Verdict

1. The identity is the log-partition gradient of an exponential family, equivalently the score
   function; the update is the natural gradient **in the mean parameters**, and information
   geometric optimisation states that for Bernoulli models it *is* PBIL [ollivier2017igo].
2. **Wrong as written**: the note steps `theta` with it and calls that a natural-gradient step.
3. **Wrong as written**: `g <- g_closed + (g_sample - g_closed)` is a no-op. The construction the
   note wants is MuProp's mean-field Taylor control variate [gu2016muprop]; nobody has used it
   for SAT, which is the one genuinely empty cell.
4. **Wrong as written**: after a WalkSAT walk the proposal has no density, so `w_b` is not a
   weight; and self-normalised weights need about `exp(KL)` samples
   [chatterjee2018samplesize].
5. A constant learning rate with a rising `beta` converges to a unit mass
   [costa2007ceconvergence].
6. Sample-guided decimation is nearly empty ground, but not empty: pseudo-backbone frequencies
   from WalkSAT minima exist and never decimate [zhang2003backbone], and decimation on the
   marginals of local-search master equations already beats belief-propagation-guided decimation
   past the clustering transition [machado2025localequations].
7. The trigger has no theory at `k = 3`: frozen variables are guaranteed only for `k >= 9`
   [achlioptas2006geometry] and near `alpha_s` at `k = 3` there are clusters with none
   [mann2010solutionspace].
8. Rigorous sampling of random k-SAT solutions is known only at densities below 2 when `k = 3`
   [he2023improved, chen2022fastsampling]; uf250 sits at 4.26.
9. **On "slow to sample, but the GPU is enough"**: half true. `B` parallel tries buy
   `1 - (1 - p)^B` for *finding* a solution and buy variance, not bias, for *estimating* the
   tilted mean, since "the bias does not decrease with the number of chains"
   [margossian2024nestedrhat]. No SAT sampler reports quality and throughput together.
10. No public cross-entropy or evolution-strategy loop runs on DIMACS, and no
    variational-neural-annealing code reads CNF.

## The baseline

**For the loop.** There is no cross-entropy or natural-evolution-strategy SAT solver, in the
literature or in public code (about twenty `gh` queries in [queries.md](queries.md)). The nearest
public code with a DIMACS reader and a sampled gradient is
**`omargup/Policy-Gradient-MaxSAT-Solver`**, REINFORCE with a baseline over an autoregressive
assignment sampler, on SATLIB [pgmaxsat_repo]; the nearest maintained estimation-of-distribution
implementation is **`EDAspy`**, whose `UMDAd` and `PBIL` are MIT-licensed and need only a
clause-count objective [edaspy_repo]. The nearest published *number* is
[machado2025localequations], whose sample-informed decimation passes the clustering threshold on
random 3-SAT. **And the primary control is the repository's own `mu` ascent** on the shared
scaffolding (`method/baselines.md`, `findings.md`).

**"Better" is the per-restart success probability per unit cost**, that is the median cost of a
restart divided by the fraction of restarts that reach a solution, at fixed hardware, seeds and
time cap, **on uf250-1065 and on the parity instances** (FourierSAT's parity set and
MM-Challenge-1 with `xnfSAT`, per `fft-walksat-las-vegas/README.md`). The numbers to beat are in
`findings.md`: `mu` solves 77 % of uf250 under the cap at a 2.0 s median, and 0 of 512 restarts
reach a solution on uf250 without the polish.

**For the GPU claim**, the baseline is `arashardakani/High-Throughput-SAT-Sampler`, 20267 unique
solutions per second on a V100 [ardakani2025htsat, htsat_repo], against `CMSGen` with the Barbarik
tester as the quality yardstick [cmsgen_repo, golia2021cmsgen]; **the measure is the bias of the
sampled tilted mean** against the exact one, by enumeration at `n <= 20` and a weighted model
count at `n = 50`, as a function of the batch `B` and of the flips per sample.

## Files

[1-naming.md](1-naming.md) the names the field uses ·
[2-review.md](2-review.md) the map, by line ·
[3-state-of-the-art.md](3-state-of-the-art.md) records, measures, hardware, and the two kinds of
bound · [4-positioning.md](4-positioning.md) the design note section by section ·
[5-plan.md](5-plan.md) what to build, what to reject on paper ·
[queries.md](queries.md) every query · [references.bib](references.bib) every citation with its
verification note.
