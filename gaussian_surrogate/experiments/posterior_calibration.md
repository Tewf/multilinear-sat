# Posterior calibration: uf250-1065 against uuf250-1065

- Date 2026-08-29T17:21:11; commit f40864cb4d; device cuda (NVIDIA GeForce RTX 4060 Laptop GPU); cap 60.0 s; 16 groups of 32 slots, rigorous fraction 0.5, walk mode walk with 10.0 n flips per restart (the seed comparison's polish), prior P(SAT) = 0.5.
- Beta prior of a satisfiable instance's per-restart success: Beta(0.4546, 0.8283), moments of 40 tilted_walk fractions on uf250-1065 (mean 0.3543).
- Instances: 20 satisfiable (20 solved under the cap) and 20 unsatisfiable. A satisfiable instance that is solved stops reporting; its last posterior is the one binned.
- The rigorous posterior stays at the prior throughout: Schöning's bound is (3/4)^250 / 2253 per try.

## Reliability of the final Beta-mixture posterior

| posterior bin | instances | actually UNSAT |
|---|---|---|
| [0.9, 0.99) | 22 | 2/22 = 0.09 |
| [0.99, 0.999) | 18 | 18/18 = 1.00 |

## The same at 1 s

| posterior bin | instances | actually UNSAT |
|---|---|---|
| [0.9, 0.99) | 38 | 18/38 = 0.47 |

## The same at 5 s

| posterior bin | instances | actually UNSAT |
|---|---|---|
| [0.9, 0.99) | 40 | 20/40 = 0.50 |

## The same at 20 s

| posterior bin | instances | actually UNSAT |
|---|---|---|
| [0.9, 0.99) | 40 | 20/40 = 0.50 |

## Time to a 0.99 posterior against kissat's refutation (uuf250-1065)

| instance | seconds to 0.99 | steps at cap | heuristic failures | kissat fastest of 3 (s) |
|---|---|---|---|---|
| uuf250-01.cnf | 45.4214 | 77 | 19712 | 1.9775 |
| uuf250-010.cnf | 45.0566 | 78 | 19968 | 2.4713 |
| uuf250-0100.cnf | 45.1586 | 77 | 19712 | 3.6235 |
| uuf250-011.cnf | 45.3357 | 77 | 19712 | 2.913 |
| uuf250-012.cnf | 45.308 | 76 | 19456 | 2.6411 |
| uuf250-013.cnf | never | 57 | 14592 | 2.4716 |
| uuf250-014.cnf | never | 53 | 13568 | 3.4361 |
| uuf250-015.cnf | 51.4812 | 69 | 17664 | 2.5628 |
| uuf250-016.cnf | 45.8145 | 76 | 19456 | 1.9647 |
| uuf250-017.cnf | 45.3676 | 78 | 19968 | 2.3595 |
| uuf250-018.cnf | 45.4342 | 77 | 19712 | 2.6655 |
| uuf250-019.cnf | 45.5751 | 77 | 19712 | 1.8317 |
| uuf250-02.cnf | 45.5 | 77 | 19712 | 3.1427 |
| uuf250-020.cnf | 44.9363 | 78 | 19968 | 3.2997 |
| uuf250-021.cnf | 45.0195 | 78 | 19968 | 4.233 |
| uuf250-022.cnf | 45.0284 | 78 | 19968 | 3.7977 |
| uuf250-023.cnf | 44.5523 | 78 | 19968 | 1.1619 |
| uuf250-024.cnf | 45.1357 | 78 | 19968 | 1.7793 |
| uuf250-025.cnf | 45.2172 | 78 | 19968 | 2.4275 |
| uuf250-026.cnf | 45.3163 | 77 | 19712 | 1.1962 |

Median ratio (time to 0.99) / (kissat refutation): 18.43; kissat median 2.517 s, posterior median 45.312 s.

Satisfiable instances unsolved under the cap whose posterior reached 0.99 (false alarms): 0 of 20.

Every run is in posterior_calibration.jsonl with its timeline, seed 0, commit and timestamps.
