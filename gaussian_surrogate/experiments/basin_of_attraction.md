# Basin of attraction: fraction of restarts that reach a satisfying assignment

No WalkSAT polish. 512 restarts per instance, 500 Adam steps, rounding every 25 steps; a restart counts if any of its rounded points satisfies the formula. Fractions are means over instances; device cuda, seed 0.

| point | method | instances | fraction of restarts | instances with a success | mean #unsat at the end |
|---|---|---|---|---|---|
| n=100 ratio=3.0 | F | 20 | 0.3827 | 20/20 | 1.0 |
| n=100 ratio=3.0 | mu | 20 | 0.1942 | 20/20 | 1.6 |
| n=100 ratio=3.0 | fourier | 20 | 0.1458 | 20/20 | 1.9 |
| n=100 ratio=3.5 | F | 20 | 0.1062 | 20/20 | 2.2 |
| n=100 ratio=3.5 | mu | 20 | 0.0498 | 17/20 | 3.1 |
| n=100 ratio=3.5 | fourier | 20 | 0.0316 | 15/20 | 3.4 |
| n=100 ratio=4.0 | F | 20 | 0.0237 | 13/20 | 3.5 |
| n=100 ratio=4.0 | mu | 20 | 0.0110 | 5/20 | 4.6 |
| n=100 ratio=4.0 | fourier | 20 | 0.0064 | 4/20 | 5.0 |
| n=100 ratio=4.2 | F | 20 | 0.0121 | 10/20 | 3.9 |
| n=100 ratio=4.2 | mu | 20 | 0.0042 | 5/20 | 5.0 |
| n=100 ratio=4.2 | fourier | 20 | 0.0022 | 4/20 | 5.5 |
| n=100 ratio=4.26 | F | 20 | 0.0078 | 8/20 | 4.2 |
| n=100 ratio=4.26 | mu | 20 | 0.0039 | 6/20 | 5.3 |
| n=100 ratio=4.26 | fourier | 20 | 0.0021 | 4/20 | 5.8 |
| uf100-430 (ratio 4.26) | F | 20 | 0.0016 | 7/20 | 4.4 |
| uf100-430 (ratio 4.26) | mu | 20 | 0.0003 | 3/20 | 5.6 |
| uf100-430 (ratio 4.26) | fourier | 20 | 0.0003 | 3/20 | 6.0 |
| uf250-1065 (ratio 4.26) | F | 20 | 0.0000 | 0/20 | 10.7 |
| uf250-1065 (ratio 4.26) | mu | 20 | 0.0000 | 0/20 | 13.6 |
| uf250-1065 (ratio 4.26) | fourier | 20 | 0.0000 | 0/20 | 14.6 |
| uf50-218 (ratio 4.26) | F | 20 | 0.0553 | 20/20 | 2.2 |
| uf50-218 (ratio 4.26) | mu | 20 | 0.0261 | 17/20 | 2.7 |
| uf50-218 (ratio 4.26) | fourier | 20 | 0.0204 | 17/20 | 3.0 |
