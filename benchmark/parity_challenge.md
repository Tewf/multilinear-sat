# Parity constraints natively: MM-Challenge-1 and matmul_3x3x3 at 23

- First record 2026-08-29T17:55:47; commit 26a0ddbe45; binary sha256 c3a97ba6bb8be97e; backend cuda; 1024 slots; 50 n SKC flips per run on the Luby schedule; cap 20.0 s per (instance, arm, seed); seeds [0, 1, 2, 3, 4].
- Today's numbers to beat (toolkit branch las-vegas-sat, one seed, 5 s cap): xnfsat 3 of 10 (4-4-4-4-1 in 0.03 s, 2-2-2-2-A in 2.39 s, 2-2-2-2-D in 0.83 s), kissat none; on matmul_3x3x3 at 23 xnfsat 0 of 5 in 60 s.

| instance | arm | solved / seeds | seconds of the solved | best violated of the rest |
|---|---|---|---|---|
| MM-23-2-2-2-2-3 | all_false | 0/5 | - | 27-30 |
| MM-23-2-2-2-2-3 | ascent200 | 0/5 | - | 543-562 |
| MM-23-2-2-2-2-3 | xnf_all_false | 0/5 | - | 10-15 |
| MM-23-2-2-2-2-3 | xnf_ascent200 | 0/5 | - | 230-255 |
| MM-23-2-2-2-2-A | all_false | 0/5 | - | 18-21 |
| MM-23-2-2-2-2-A | ascent200 | 0/5 | - | 545-569 |
| MM-23-2-2-2-2-A | xnf_all_false | 0/5 | - | 7-11 |
| MM-23-2-2-2-2-A | xnf_ascent200 | 0/5 | - | 246-253 |
| MM-23-2-2-2-2-B | all_false | 0/5 | - | 20-22 |
| MM-23-2-2-2-2-B | ascent200 | 0/5 | - | 547-568 |
| MM-23-2-2-2-2-B | xnf_all_false | 0/5 | - | 9-12 |
| MM-23-2-2-2-2-B | xnf_ascent200 | 0/5 | - | 237-263 |
| MM-23-2-2-2-2-C | all_false | 0/5 | - | 19-22 |
| MM-23-2-2-2-2-C | ascent200 | 0/5 | - | 544-799 |
| MM-23-2-2-2-2-C | xnf_all_false | 0/5 | - | 8-12 |
| MM-23-2-2-2-2-C | xnf_ascent200 | 0/5 | - | 216-262 |
| MM-23-2-2-2-2-D | all_false | 0/5 | - | 19-23 |
| MM-23-2-2-2-2-D | ascent200 | 0/5 | - | 772-805 |
| MM-23-2-2-2-2-D | xnf_all_false | 0/5 | - | 5-10 |
| MM-23-2-2-2-2-D | xnf_ascent200 | 0/5 | - | 235-261 |
| MM-23-2-2-2-2-M | all_false | 0/5 | - | 16-21 |
| MM-23-2-2-2-2-M | ascent200 | 0/5 | - | 774-798 |
| MM-23-2-2-2-2-M | xnf_all_false | 0/5 | - | 11-12 |
| MM-23-2-2-2-2-M | xnf_ascent200 | 0/5 | - | 222-253 |
| MM-23-2-2-2-3-4 | all_false | 0/5 | - | 29-35 |
| MM-23-2-2-2-3-4 | ascent200 | 0/5 | - | 781-807 |
| MM-23-2-2-2-3-4 | xnf_all_false | 0/5 | - | 19-23 |
| MM-23-2-2-2-3-4 | xnf_ascent200 | 0/5 | - | 245-252 |
| MM-23-2-2-2-4-A | all_false | 0/5 | - | 23-27 |
| MM-23-2-2-2-4-A | ascent200 | 0/5 | - | 780-801 |
| MM-23-2-2-2-4-A | xnf_all_false | 0/5 | - | 15-19 |
| MM-23-2-2-2-4-A | xnf_ascent200 | 0/5 | - | 234-256 |
| MM-23-2-2-2-4-B | all_false | 0/5 | - | 25-27 |
| MM-23-2-2-2-4-B | ascent200 | 0/5 | - | 777-812 |
| MM-23-2-2-2-4-B | xnf_all_false | 0/5 | - | 14-19 |
| MM-23-2-2-2-4-B | xnf_ascent200 | 0/5 | - | 243-266 |
| MM-23-4-4-4-4-1 | all_false | 0/5 | - | 37-44 |
| MM-23-4-4-4-4-1 | ascent200 | 0/5 | - | 785-804 |
| MM-23-4-4-4-4-1 | xnf_all_false | 0/5 | - | 27-31 |
| MM-23-4-4-4-4-1 | xnf_ascent200 | 0/5 | - | 234-254 |
| matmul_3x3x3 at 23 (toolkit --emit-xnf) | all_false | 0/5 | - | 6-7 |
| matmul_3x3x3 at 23 (toolkit --emit-xnf) | ascent200 | 0/5 | - | 767-790 |
| matmul_3x3x3 at 23 (toolkit --emit-xnf) | xnf_all_false | 0/5 | - | 4-5 |
| matmul_3x3x3 at 23 (toolkit --emit-xnf) | xnf_ascent200 | 0/5 | - | 224-253 |

Verification, matmul_2x2x2 at 7 through decide-rank-by-sat --solver: 3-cut CNF, the ascent alone (the toolkit's multilinear-sat line) (the toolkit's own line, 0.1 defaults, one thread): exit code 1.

```
lower bound: rank is at least 6
  k = 7 [multilinear-sat-26a0ddbe45-20260829-171313]: NO, rank is more than 7  (60.1416 s)
```

Verification, matmul_2x2x2 at 7 through decide-rank-by-sat --solver: XNF through the as-xnfsat adapter, the walk from all false (--backend cuda --seed-kind all-false --polish-flips 32200 --batch-size 4096 --time-limit 120): exit code 3.

```
lower bound: rank is at least 6
  k = 7 [xnfsat]: no answer, gave up after 120.159 s
```

Every run is in parity_challenge.jsonl with its seed, commit and binary hash; the instance files are not committed.
