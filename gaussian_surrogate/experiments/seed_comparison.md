# Seed comparison: per-restart success of one polish from four seeds

- Date 2026-08-29T13:06:18; commit 5cc1981f13; device cuda (NVIDIA GeForce RTX 4060 Laptop GPU), torch 2.13.0+cu130; other GPU processes at start: none
- 512 slots per run, T = 500 seeding steps (mu: Adam on the mu objective; tilted: the loop, G = slots / 32 groups), polish = 10 n SKC flips of the flip kernel, noise 0.5; instances: the first 20 of each family; seeds [0, 1].
- p = mean over runs of the fraction of slots satisfied after the polish; cost = median over runs of (seed seconds + polish seconds) / slots; expected time = cost / p. The tilted seed draws the slots from its final q_theta; its ESS and saturated fraction are the loop's last step.
- Replication of Putikhin and Kascheev, EWDTS 2017 (DOI 10.1109/EWDTS.2017.8110119): they seeded probSAT from a continuous extension; their abstract gives no per-restart number and no code was found. Where their protocol is recoverable it differs from this one in the local search (probSAT against the SKC kernel) and in the seed (a nonlinear optimisation of a continuous extension against mu ascent and the tilted loop). Nearest public code of the loop's family, not run here: omargup/Policy-Gradient-MaxSAT-Solver (REINFORCE with a baseline, reads DIMACS, no licence) and VicentePerezSoloviev/EDAspy (PBIL and UMDA, MIT).

| family | seed | runs | p | instances with p > 0 | cost / restart (ms) | expected time (ms) | seed s | polish s | ESS | saturated | seeding steps with a solution | weights |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| uf50-218 | uniform | 40 | 0.5490 | 40/40 | 0.304 | 0.6 | 0.00 | 0.16 | - | - | - | - |
| uf50-218 | all_false | 40 | 0.5581 | 40/40 | 0.304 | 0.5 | 0.00 | 0.16 | - | - | - | - |
| uf50-218 | mu | 40 | 0.5881 | 40/40 | 0.860 | 1.5 | 0.31 | 0.16 | - | - | - | - |
| uf50-218 | tilted | 40 | 0.5622 | 40/40 | 34.477 | 61.3 | 17.61 | 0.16 | 19.6 | 0.277 | 31/40 | metropolis |
| uf100-430 | uniform | 40 | 0.2979 | 40/40 | 0.860 | 2.9 | 0.00 | 0.39 | - | - | - | - |
| uf100-430 | all_false | 40 | 0.2912 | 40/40 | 0.852 | 2.9 | 0.00 | 0.40 | - | - | - | - |
| uf100-430 | mu | 40 | 0.3358 | 40/40 | 1.904 | 5.7 | 0.49 | 0.40 | - | - | - | - |
| uf100-430 | tilted | 40 | 0.3211 | 40/40 | 80.502 | 250.7 | 39.43 | 0.39 | 12.8 | 0.233 | 2/40 | metropolis |
| uf250-1065 | uniform | 40 | 0.0859 | 36/40 | 2.350 | 27.3 | 0.00 | 1.14 | - | - | - | - |
| uf250-1065 | all_false | 40 | 0.0857 | 35/40 | 2.349 | 27.4 | 0.00 | 1.16 | - | - | - | - |
| uf250-1065 | mu | 40 | 0.1125 | 38/40 | 5.107 | 45.4 | 1.29 | 1.16 | - | - | - | - |
| uf250-1065 | tilted | 40 | 0.0955 | 35/40 | 191.045 | 2000.3 | 95.48 | 1.14 | 6.8 | 0.147 | 0/40 | metropolis |
| uf250-1065 | tilted_walk | 40 | 0.3543 | 35/40 | 169.150 | 477.4 | 87.11 | 0.84 | 20.7 | 0.232 | 37/40 | walk |

Throughput: the kernel's polish runs at a median 2,976 flips per second per chain (1.5 M per second over the 512 chains) on the cuda against 6.26 M flips per second for probSAT on one CPU core (measured on uuf250-01, 20 M flips, seeds 1 and 2). One chain of the kernel is 2103x slower than probSAT; the batch is what the GPU buys.

Every run is in seed_comparison.jsonl with its seed, instance, commit and timestamps.
