# What the tilted loop does not build, and why

Companion to [sampling-gradient-loop.md](../../method/sampling-gradient-loop.md). The loop as coded
(`tilted_loop.py`, 2026-08-29) leaves two pieces of the design note out on purpose and builds
one in two forms, one of them labelled biased.

## Decimation

The note's last step fixes every variable whose tilted mean is within delta of +-1, simplifies
the formula and drops the variable. Not built, for two reasons. The loop is measured first
(`experiments/seed_comparison.py`), and only a loop that raises the per-restart success
probability earns a simplification of its formula. And the trigger has no theory at k = 3:
frozen variables are guaranteed in every cluster only for k >= 9 (Achlioptas and Ricci-Tersenghi
2006), and near the threshold at k = 3 there are always clusters without any frozen variable
(Mann and Hartmann 2010), so a saturated tilted mean on uf250 is a heuristic signal, not a
backbone (review `literature/tilted-sampling-loop/4-positioning.md`). The count of saturated
means is logged at every step so that the case for decimation can be read off the trajectories
before any is written.

## The weights: built twice, one of them biased

The note offers two moves between the draw and the weight. Both exist behind `walk_mode`.
`metropolis` is the annealed-importance-sampling ladder of `annealing.py` (Neal 2001): a
Metropolis kernel that leaves q_theta e^{beta_k S} invariant at each rung, so the weights are
those of a measure and the sampled tilted mean is consistent. `walk` is the WalkSAT/SKC rule of
`walksat.py` followed by self-normalised exp(beta S) weights; after such a walk no proposal
density exists, the weights belong to no measure, and the estimate is biased. The label
"biased" travels with it into the trajectory (`weights_biased`), the `c json` line and the
tables. The bias of both is measured by enumeration in `experiments/tilted_mean_bias.md`.
What the walk buys is reach: the SKC rule moves a sample to S = m where the Metropolis kernel at
the same budget does not, which is the trade the seed comparison measures.

## The control variate at its written coefficient

`g = g_hat - lambda (h_hat - g_closed)` is built with h_hat the MuProp mean-field control
variate (Gu, Levine, Sutskever, Mnih 2016), lambda a tunable (`control_variate_coefficient`)
whose default is 0. Measured on uf50-01 with S = 32 and 2n SKC flips (2026-08-29, the job
folder's `notes.md`): with the raw count uncentred the correction multiplies the
per-coordinate noise of g by 100 at beta 0.05 and by 30000 at beta 1; centred at mu(p), which
leaves its expectation unchanged, it still adds 8 % at beta 0.05, 140 % at beta 0.2 and 26x at
beta 1. After 2n flips the annealed samples share no noise with their raw draws, so the
correction can only add its own. The centred form is what the code computes;
`--control-variate-coefficient 1` restores the note's merge, and the AIS move with fewer rungs
is where it would have a chance, which is not measured.
