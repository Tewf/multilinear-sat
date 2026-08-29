# Table 3: the UNSAT posterior against kissat

Part of [the findings of the tilted loop](README.md); the sections read in that file's order.

## Table 3: the UNSAT posterior against kissat (uf250-1065 against uuf250-1065, 20 + 20 instances)

Loop in walk mode at the polish's budget (one heuristic restart = one tilted_walk restart), half
the groups rigorous, cap 60 s, prior P(SAT) = 0.5, Beta(0.455, 0.828) fitted by moments on the 40
tilted_walk fractions above (mean 0.354). The Beta-mixture posterior after k failed heuristic
restarts, and where the instances were:

| time | posterior on every uuf instance | uf instances still running | uuf instances | actually UNSAT among those reporting |
|---|---|---|---|---|
| 1 s (step 1, k = 256) | 0.940 | 3 of 20 (17 solved in step 1 at 0.78 s) | 20 | 18 of 38 = 0.47 |
| 5 s | 0.973 | 1 of 20 | 20 | 20 of 40 = 0.50 at each instance's last value |
| 45 s | 0.990 | 1 of 20 (solved at 42.6 s, posterior 0.990) | 20 | 18 of 18 above 0.99 |
| 60 s (cap) | 0.991 | 0 of 20 | 20 | 18 of 18 above 0.99; 2 below (53 and 57 steps) |

The posterior is the same number on every instance at a given step: it is a function of k alone,
0.93 to 0.94 after the first step on satisfiable and unsatisfiable instances alike, 0.99 after
17,700 to 20,000 failures. Time to 0.99: 18 of 20 uuf instances at 44.6 to 51.5 s (median 45.3 s),
2 never within the cap; kissat refutes the same instances in 1.16 to 4.23 s (median 2.52 s,
fastest of three, exit 20): median ratio 18.4. Satisfiable side: 17 solved in step 1, 2 in step 2,
1 at step 55 with the posterior at 0.990 when its solution arrived; posteriors at the moment of
solution 0.93 to 0.99. The rigorous posterior stayed at 0.5 throughout (Schöning's bound at
n = 250 is (3/4)^250 / 2253 = 2.7e-35 per try).
