# Table 1: is the sampled tilted mean an estimate of anything?

Part of [the findings of the tilted loop](README.md); the sections read in that file's order.

## Table 1: is the sampled tilted mean an estimate of anything? (n = 12, enumeration)

RMS error of the weighted sample mean against the exact E_tilted[x], 5 seeds, 16n moves per sample:

| beta | move | S = 64 | S = 512 | S = 4096 | ESS at 4096 |
|---|---|---|---|---|---|
| 0.5 | metropolis (AIS weights) | 0.122 | 0.049 | 0.015 | 3801 |
| 0.5 | walk (SKC, exp(beta S) weights) | 0.564 | 0.542 | 0.545 | 4096 |
| 2.0 | metropolis (AIS weights) | 0.121 | 0.052 | 0.018 | 1580 |
| 2.0 | walk (SKC, exp(beta S) weights) | 0.249 | 0.219 | 0.223 | 4096 |

The annealed move is consistent (the error falls as 1/sqrt(S) at every rung count); the walk's
weights belong to no measure and its error does not move with S. The first run of this table
found a bug: freezing a chain at S = m biased the mean by 0.40 RMS.
