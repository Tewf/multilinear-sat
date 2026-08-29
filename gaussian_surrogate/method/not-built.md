# What the tilted loop does not build, and why

Companion to [sampling-gradient-loop.md](sampling-gradient-loop.md). The loop as coded
(`tilted_loop.py`, 2026-08-29) leaves three pieces of the design note out, on purpose.

## Decimation

The note's last step fixes every variable whose tilted mean is within delta of +-1, simplifies
the formula and drops the variable. Not built. The reason: the loop is measured first
(`experiments/seed_comparison.py`), and only a loop that raises the per-restart success
probability earns a simplification of its formula. Decimation also changes the object under
test between steps (a smaller formula, a different m), which would make the trajectory's mu,
ESS and min unsat incomparable across a run. The count of saturated means is logged at every
step so that the case for decimation can be read off the trajectories before any is written.

## A tempered walk and a proposal correction

The note offers two walks between the draw and the weight: Metropolis on S at inverse
temperature beta, or a short WalkSAT walk. The loop uses the WalkSAT/SKC rule of `walksat.py`
(or Schöning's for the rigorous groups) at every beta, and the weights exp(beta S) carry no
proposal correction. So the weighted samples are not draws from q_theta e^{beta S} / Z, and the
identity of the note holds for them only at beta -> 0, where the walk's own drift dominates:
on uf50-01 at beta 0.05 the sampled direction has norm 4.0 against 0.19 for the closed form.
The loop is, in the field's terms, the cross-entropy method with the walk as the elite
generator and the tilt as a soft elite threshold. A Metropolis walk on log q_theta + beta S,
which would make the weights exact up to burn-in, is the first thing to build if the measured
loop is worth improving.

## The control variate at its written coefficient

`g = g_hat - lambda (h_hat - g_closed)` is built, with lambda a tunable
(`control_variate_coefficient`) whose default is 0. Measured on uf50-01 with S = 32 and 2n
flips (2026-08-29, `notes.md` of the job folder): with the raw count uncentred the
correction multiplies the per-coordinate noise of g by 100 at beta 0.05 and by 30000 at
beta 1; centred at mu(p) (which leaves its expectation unchanged) it still adds 8 % at
beta 0.05, 140 % at beta 0.2 and 26x at beta 1. The annealed samples are decorrelated from
their raw draws after 2n flips, so the raw-draw estimate shares no noise with g_hat and can
only add its own. The centred form is what the code computes; `--control-variate-coefficient 1`
restores the note's merge.
