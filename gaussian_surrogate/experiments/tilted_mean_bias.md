# Bias of the sampled tilted mean, by enumeration

Random 3-SAT, n = 12, m = 51, theta ~ U(-0.5, 0.5), exact E_tilted[x] by enumeration of the cube. RMS error over the 12 coordinates, mean over 5 seeds; moves per sample are AIS rungs (metropolis) or SKC flips (walk), as multiples of n; zero moves is plain importance sampling from q_theta for both. ESS is the mean effective sample size of the weights.

| beta | move | moves / n | S = 64 | S = 512 | S = 4096 | ESS at 4096 |
|---|---|---|---|---|---|---|
| 0.5 | metropolis | 0 | 0.196 | 0.065 | 0.025 | 1333 |
| 0.5 | metropolis | 1 | 0.146 | 0.058 | 0.018 | 2179 |
| 0.5 | metropolis | 4 | 0.131 | 0.043 | 0.022 | 3155 |
| 0.5 | metropolis | 16 | 0.122 | 0.049 | 0.015 | 3801 |
| 0.5 | walk | 0 | 0.196 | 0.065 | 0.025 | 1333 |
| 0.5 | walk | 1 | 0.510 | 0.494 | 0.496 | 3647 |
| 0.5 | walk | 4 | 0.562 | 0.541 | 0.544 | 4083 |
| 0.5 | walk | 16 | 0.564 | 0.542 | 0.545 | 4096 |
| 2.0 | metropolis | 0 | 0.560 | 0.325 | 0.139 | 26 |
| 2.0 | metropolis | 1 | 0.371 | 0.168 | 0.054 | 79 |
| 2.0 | metropolis | 4 | 0.276 | 0.104 | 0.033 | 334 |
| 2.0 | metropolis | 16 | 0.121 | 0.052 | 0.018 | 1580 |
| 2.0 | walk | 0 | 0.560 | 0.325 | 0.139 | 26 |
| 2.0 | walk | 1 | 0.239 | 0.203 | 0.208 | 3151 |
| 2.0 | walk | 4 | 0.248 | 0.219 | 0.222 | 4069 |
| 2.0 | walk | 16 | 0.249 | 0.219 | 0.223 | 4096 |
