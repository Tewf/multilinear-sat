# Posterior calibration in C++: uf250-1065 against uuf250-1065

- Loop phase 2026-08-29T20:21:41; commit 26a0ddbe45; binary sha256 c3a97ba6bb8be97e; backend cuda; cap 20.0 s; 4096 slots, rigorous fraction 0.5, uniform starts, 10 n SKC flips per run, prior P(SAT) = 0.5.
- Beta prior of a satisfiable instance's per-restart success: Beta(0.4698, 5.021), moments of 40 uniform-arm fractions on uf250-1065 (mean 0.0856).
- Instances: 20 satisfiable (20 solved under the cap) and 20 unsatisfiable. A solved instance's posterior is the one after its last failed run.
- The rigorous posterior stays at the prior throughout: Schoening's bound is (3/4)^250 / 2253 per try.

## Reliability of the final Beta-mixture posterior

| posterior bin | instances | actually UNSAT |
|---|---|---|
| [0.5, 0.9) | 20 | 0/20 = 0.00 |
| [0.99, 0.999) | 20 | 20/20 = 1.00 |

## The same at 0.5 s

| posterior bin | instances | actually UNSAT |
|---|---|---|
| [0.9, 0.99) | 20 | 20/20 = 1.00 |

## The same at 2 s

| posterior bin | instances | actually UNSAT |
|---|---|---|
| [0.9, 0.99) | 20 | 20/20 = 1.00 |

## The same at 5 s

| posterior bin | instances | actually UNSAT |
|---|---|---|
| [0.9, 0.99) | 20 | 20/20 = 1.00 |

## Time to a 0.99 posterior against kissat's refutation (uuf250-1065)

| instance | seconds to 0.99 | runs at cap | heuristic failures | kissat fastest (s) |
|---|---|---|---|---|
| uuf250-01.cnf | 8.089 | 89 | 182272 | 2.0515 |
| uuf250-010.cnf | 7.947 | 91 | 186368 | 2.5473 |
| uuf250-0100.cnf | 8.116 | 88 | 180224 | 3.7237 |
| uuf250-011.cnf | 7.888 | 91 | 186368 | 2.9296 |
| uuf250-012.cnf | 8.021 | 90 | 184320 | 2.7756 |
| uuf250-013.cnf | 8.043 | 90 | 184320 | 2.4184 |
| uuf250-014.cnf | 7.927 | 77 | 157696 | 3.5021 |
| uuf250-015.cnf | 14.58 | 59 | 120832 | 2.535 |
| uuf250-016.cnf | 14.747 | 56 | 114688 | 1.9628 |
| uuf250-017.cnf | 14.002 | 60 | 122880 | 2.3609 |
| uuf250-018.cnf | 14.772 | 54 | 110592 | 2.7674 |
| uuf250-019.cnf | 14.241 | 59 | 120832 | 1.9422 |
| uuf250-02.cnf | 14.917 | 59 | 120832 | 3.1558 |
| uuf250-020.cnf | 14.626 | 57 | 116736 | 3.3016 |
| uuf250-021.cnf | 14.958 | 58 | 118784 | 4.172 |
| uuf250-022.cnf | 14.717 | 57 | 116736 | 3.7576 |
| uuf250-023.cnf | 15.36 | 56 | 114688 | 1.1611 |
| uuf250-024.cnf | 14.783 | 58 | 118784 | 1.6747 |
| uuf250-025.cnf | 15.774 | 52 | 106496 | 2.3075 |
| uuf250-026.cnf | 14.001 | 55 | 112640 | 1.1304 |

Median ratio (time to 0.99) / (kissat refutation): 4.578; kissat median 2.541 s, posterior median 14.410 s.

Satisfiable instances whose posterior reached 0.99 before a solution (false alarms): 0 of 20, of which 0 were still unsolved at the cap.

Every run is in posterior_calibration.jsonl with its timeline, seed 0, command, commit and binary hash.
