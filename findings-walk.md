# Findings: the walk in the library, measured

The Python record (`gaussian_surrogate/findings-tilted.md` on branch `gaussian-surrogate`)
priced the seeded walk with a launch-bound PyTorch kernel at 3.2 k flips/s per chain. This
is the same algorithm inside the C++20/CUDA library, measured on 2026-08-29 on one RTX 4060
Laptop GPU (24 SMs, 8 GB) and an i5-12450H, CUDA 12.9, the card free of other processes
(checked with nvidia-smi before each stage), one GPU job at a time. Every number below is in
a JSONL record under `benchmark/` with the command that made it, the seed, the commit and
the sha256 of the frozen binary; the tables in `benchmark/*.md` are generated from those
records by the script beside each.

## 1. Throughput (`benchmark/walk_throughput.md`, commit 0d98518)

uuf250-01 (unsatisfiable, so no chain stops), 20 M flips per run split over the batch,
uniform starts, flips per second from the solver's polish clock; probSAT's printed
flips/sec over the same flips, seeds 1 and 2.

| chains | rule | aggregate M flips/s | per chain k flips/s | against one probSAT core |
|---|---|---|---|---|
| probSAT, one core | probsat | 6.28 | 6280 | 1x |
| cuda 512 | probsat / skc | 11.2 / 16.0 | 21.8 / 31.3 | 1.8x / 2.5x |
| cuda 1024 | probsat / skc | 22.5 / 31.9 | 22.0 / 31.1 | 3.6x / 5.1x |
| cuda 4096 | probsat / skc | 77.1 / 109.3 | 18.8 / 26.7 | 12.3x / 17.4x |
| cuda 16384 | probsat / skc | 125.7 / 137.4 | 7.7 / 8.4 | 20.0x / 21.9x |
| cpu, 4 threads, 4096 | probsat / skc | 9.4 / 12.9 | 2.3 / 3.1 | 1.5x / 2.1x |

The brief's target, ten times one core at 4096 slots, is met by both rules. One chain of the
batch runs 230 to 330x slower than probSAT's one chain (the thread-per-slot kernel is
latency-bound: aggregate throughput doubles with the batch up to 4096 and gains only 1.3 to
1.6x from 4096 to 16384). The probsat rule computes break counts twice per step (its
weighted draw has no stack array on the device), which is the 30 % gap to skc.

## 2. The seeds (`benchmark/seed_comparison.md`, commit 26a0ddb)

The Python record's protocol at 4096 slots: 20 instances of each family, seeds 0 and 1, one
polish of 10n SKC flips (noise 0.5) from each seed; p = fraction of slots satisfied after
the polish, cost = (seed + polish seconds) / slots, expected time = cost / p. The ascent is
the library's projected gradient with its defaults for 50, 200 or 500 iterations, rounded by
sign. probSAT: one run to a solution per instance and seed on one core (process start and
parse included), its mean flips per solution beside the walk's polish flips / p.

| family | seed | p | vs uniform | cost / restart (ms) | expected time (ms) | flips per solution |
|---|---|---|---|---|---|---|
| uf50-218 | uniform | 0.5448 | | 0.0027 | 0.005 | 920 |
| uf50-218 | all false | 0.5581 | +2 % | 0.0026 | 0.005 | 900 |
| uf50-218 | ascent 50 / 200 / 500 | 0.5821 / 0.5865 / 0.5873 | +7 / +8 / +8 % | 0.0045 / 0.0110 / 0.0237 | 0.008 / 0.019 / 0.040 | |
| uf50-218 | probSAT, one core | solved 40/40 | | | mean 3.92, median 4.10 | 700 |
| uf100-430 | uniform | 0.2985 | | 0.0071 | 0.024 | 3350 |
| uf100-430 | all false | 0.2956 | -1 % | 0.0071 | 0.024 | 3380 |
| uf100-430 | ascent 50 / 200 / 500 | 0.3358 / 0.3380 / 0.3399 | +12 / +13 / +14 % | 0.0105 / 0.0211 / 0.0422 | 0.031 / 0.062 / 0.124 | |
| uf100-430 | probSAT, one core | solved 40/40 | | | mean 6.71, median 5.95 | 6.8 k |
| uf250-1065 | uniform | 0.0856 | | 0.0227 | 0.265 | 29 200 |
| uf250-1065 | all false | 0.0884 | +3 % | 0.0227 | 0.257 | 28 300 |
| uf250-1065 | ascent 50 / 200 / 500 | 0.1096 / 0.1125 / 0.1135 | +28 / +31 / +33 % | 0.0311 / 0.0561 / 0.1057 | 0.284 / 0.499 / 0.932 | |
| uf250-1065 | probSAT, one core | solved 40/40 | | | mean 17.93, median 8.15 | 75.6 k |

The per-restart success reproduces the Python record to the third decimal (its uniform
0.549 / 0.298 / 0.086, its mu ascent 0.588 / 0.336 / 0.1125), so the seed's lift is the
algorithm's and not an artefact of either implementation. With the walk at the card's speed
the seed's cost is the algorithm's too: at 50 iterations it costs 1.7 / 1.5 / 1.4x a uniform
restart for +7 / +12 / +28 % in p, and the uniform start still wins on expected time at every
size, by 60 % on uf50, 29 % on uf100 and 7 % on uf250; 200 and 500 iterations widen the gap
(1.9x and 3.5x on uf250). The verdict of the record stands with the artefact removed, and
the margin narrows with n: the seed helps most where p is smallest. What the batch buys is
the other column: the expected time to a solution of 4096 chains on uf250 is 0.27 ms against
probSAT's 8 to 18 ms on one core.

## 3. The posterior (`benchmark/posterior_calibration.md`)

uf250-1065 against uuf250-1065, the first 20 instances of each: the walk from uniform starts,
10n SKC flips at 4096 slots, half the batch rigorous (Schöning's rule from uniform starts for
3n flips), cap 20 s, prior P(SAT) = 0.5, Beta(0.4698, 5.0207) fitted by moments on the 40
uniform-arm fractions of section 2 on uf250 (mean 0.0856, one fraction of zero); kissat's
refutation, fastest of three runs, beside it.

| what | result |
|---|---|
| satisfiable instances solved | 20 of 20, all inside the first run (0.08 to 0.11 s), before any failure is counted |
| their posterior | the prior, 0.5, for all 20: no false alarm at any threshold |
| unsatisfiable instances at the cap | 20 of 20 in [0.99, 0.999) after 86 to 91 runs, 176 000 to 186 000 failed restarts |
| reliability curve | on the diagonal: bin [0.5, 0.9) holds 20 instances, 0 unsatisfiable; bin [0.99, 0.999) holds 20, all unsatisfiable |
| kissat's refutation | 1.13 to 4.17 s, median 2.54 s, exit 20 every time |
| time to a 0.99 posterior | at the 42nd run on all 20 instances (86 016 failed restarts): 7.9 to 8.1 s on the 7 instances run on a cool chassis (0.22 s per run), 14.0 to 15.8 s on the 13 run while the package throttled at 95 C beside a rebuild (0.33 to 0.39 s per run); 3.1x kissat's median at full speed |
| the rigorous posterior | at the prior throughout: (3/4)^250 / 2253 = 2.7e-35 per try |

The Beta-mixture posterior depends on the failure count alone once the prior is fixed, and the
count per run is fixed by the batch, so the crossing falls on the same run everywhere and only
the run's seconds vary. At the card's speed 0.99 comes about 8 s after the start, three times
kissat's refutation, and stays a posterior. The first pass of this experiment put the crossing
at 16 s because the harness kept only the tail of the solver's log (fixed in `walk_runs.py`); the
second pass shares its second half with a rebuild, which is why both bands are reported. The
rigorous half is arithmetic that cannot move at n = 250.

## 4. Parities (`benchmark/parity_challenge.md`)

The ten MM-Challenge-1 XNFs (19 251 variables, 55 983 clauses, 729 parities of length 23)
and the toolkit's own matmul_3x3x3 at rank 23 (`--emit-xnf`: 19 251 variables, 55 890
clauses, 729 parities), 1024 slots, 50n SKC flips per run on the Luby schedule, cap 20 s,
seeds 0 to 4, from all-false starts (xnfSAT's default, which its paper found better than
random) and from the ascent at 200 iterations. Today's numbers to beat (toolkit branch
las-vegas-sat, one seed, 5 s cap): xnfsat 3 of 10 (4-4-4-4-1 in 0.03 s, 2-2-2-2-A in 2.39 s,
2-2-2-2-D in 0.83 s), kissat none; on matmul_3x3x3 at 23 xnfsat 0 of 5 in 60 s.

| instance | all-false walk, solved / 5 | best violated rows at the cap | ascent then walk, solved / 5 | best violated rows |
|---|---|---|---|---|
| MM-23-2-2-2-2-3 | 0 | 27 to 30 | 0 | 543 to 562 |
| MM-23-2-2-2-2-A | 0 | 18 to 21 | 0 | 545 to 569 |
| MM-23-2-2-2-2-B | 0 | 20 to 22 | 0 | 547 to 568 |
| MM-23-2-2-2-2-C | 0 | 19 to 22 | 0 | 544 to 799 |
| MM-23-2-2-2-2-D | 0 | 19 to 23 | 0 | 772 to 805 |
| MM-23-2-2-2-2-M | 0 | 16 to 21 | 0 | 774 to 798 |
| MM-23-2-2-2-3-4 | 0 | 29 to 35 | 0 | 781 to 807 |
| MM-23-2-2-2-4-A | 0 | 23 to 27 | 0 | 780 to 801 |
| MM-23-2-2-2-4-B | 0 | 25 to 27 | 0 | 777 to 812 |
| MM-23-4-4-4-4-1 | 0 | 37 to 44 | 0 | 785 to 804 |
| matmul_3x3x3 at 23 | 0 | 6 to 7 | 0 | 767 to 790 |

None solved, where xnfsat solves three of ten within five seconds. The native parity does
what it should (a parity is one row, its flip a toggle; the walk on the XNF reaches 16 to 44
violated rows of 56 700 from all false, and 6 to 7 on the toolkit's formula) and the SKC
rule at noise 0.5 with 20 s does not close the last rows; xnfSAT is yalsat's probSAT-style
rule with its own constants, and the probsat rule of this walk was not tried on these
instances (caveat). The ascent's rounded point is a far worse start than all false here,
540 to 810 rows against 16 to 44: on Brent equations the relaxation's landscape does not
point at the decompositions, which is the replication's answer to the toolkit's step 3.

Verification on matmul_2x2x2 at rank 7 through the toolkit's `decide-rank-by-sat --solver`
route, which reads the model back and re-multiplies it: given the binary itself the toolkit
names it multilinear-sat, hands it the 3-cut CNF and runs the 0.1 defaults (the ascent alone,
one thread), and reports NO after 60 s (its documented third answer for a solver that can only
find); given the `benchmark/as-xnfsat/xnfsat` adapter it hands the XNF, and the walk from all
false at 4096 slots gives no answer in 120 s. The re-multiplication is what caught the parser
bug on the way (a model of the mutilated formula was refused); the toolkit's own record has
xnfsat at 0 of 5 and yalsat at 1 of 5 in 60 s on this fixture, so no route holds a verified
model of it. On an XNF read correctly the solver's own checker certifies every model it
reports, which the brute-force doctest cases on tiny XNFs cover.

## 5. The tilted seed (`benchmark/seed_comparison.md`, arm tilted500)

The Python record's loop as a seed: 128 groups of 32 slots, 500 steps of draw, annealing
ladder of 2n Metropolis proposals with AIS weights, and a decreasing step on theta, no control
variate; then the same 10n SKC polish. Run on uf250 first, seeds 0 and 1, and stopped by hand
after 7 of its 120 runs when the package reached 97 C under a 30-minute ceiling on the card.

| runs | seed | p | runs above uniform's | cost / restart (ms) | expected time (ms) |
|---|---|---|---|---|---|
| 7 (uf250-01, 010, 0100, 011; seeds 0 and 1) | tilted, 500 steps | 0.0707 | 4/7 | 2.512 | 35.5 |
| the same 7 | uniform | 0.0598 | | 0.0227 | 0.38 |
| the same 7 | ascent 50 | 0.0850 | | 0.0311 | 0.37 |

On uf250-01 the tilted seed lifts p from 0.19 to 0.22 and 0.24; on the three harder instances
it moves p by less than the binomial spread of 4096 draws. Its restart costs 110x a uniform
one (9.1 to 10.2 s of seeding per run against 0.09 s of polish at 4096 slots), so its
expected time is 94x the uniform start's on the same runs. The Python record measured +11 %
in p at 81x the cost on the full 40 runs of uf250 (`gaussian_surrogate/findings-tilted.md`,
its seed table); the C++ verdict is the same and the arm stops here.

## What the tables show

The port removes the one artefact of the Python record and leaves its verdicts standing,
sharper. The walk inside the library runs at 77 to 109 M flips/s at 4096 chains, 12 to 17
times probSAT's one core, so the seed comparison prices the seeds at the algorithm's cost: the
ascent raises the per-restart success by 7, 12 and 28 % at 50 iterations on uf50, uf100 and
uf250 and still loses on expected time at every size, by 7 % on uf250 where it comes closest;
the tilted seed raises it by 18 % on the seven uf250 runs it completed at 110 times the cost
and does not pay, as the record said. The batch is the win the record could not show: 4096
chains from uniform starts reach a solution of uf250 in 0.27 ms of expected time against
probSAT's 8 to 18 ms on one core, at flips per solution within a factor of three of its. The
Beta-mixture posterior sits on the diagonal on uf250 against uuf250 because the walk solves
every satisfiable instance in its first run; it crosses 0.99 at the 42nd failed run, 8 s at
full speed against kissat's 2.5 s refutation, and remains a posterior, while the rigorous half
cannot move at n = 250. The native parity behaves as the theory says and is not enough: from
all false the walk ends 16 to 44 rows short on the ten MM-Challenge-1 instances of which
xnfsat solves three, and the relaxation's rounded point is a far worse start there than all
false, which answers the toolkit's open step in the negative for this relaxation.

## Caveats

- One laptop GPU shared with nothing during the stages (nvidia-smi checked), but a chassis
  that rode 80 to 95 C through the parity stage; the seconds carry that band. Seeds 0 and 1,
  20 instances per family, no confidence intervals: the binomial spread of p at 4096 slots is
  under 0.01, the instance-to-instance spread is 0.1 to 0.25 (section 3's prior fit).
- The walk's polish is this library's SKC at noise 0.5 and 10n flips, the Python record's
  protocol, not probSAT's rule at its own constants; probSAT beside it is one run to a
  solution per instance and seed, process start included, with its flip count as the
  machine-free number.
- The ascent is the library's projected gradient at the 0.1 defaults (step 0.1, momentum
  0.9, kick 0.3), which the 0.1 sweep never found a solving setting for; the Python's mu
  ascent was Adam at 0.05, and the two give the same p at 200 to 500 steps.
- The parities were walked with the skc rule only; probsat's rule, xnfSAT's noise and
  restart constants, and a longer cap were not tried, and 20 s at 1024 slots is neither the
  paper's 1000 s nor the toolkit's 5 s on one seed.
- The posterior's prior is fitted on the family it is then tested on (40 fractions of the
  same 20 instances at seeds 0 and 1); its reliability curve is on the diagonal because the
  satisfiable side is solved inside the first run, which says the walk is good on uf250,
  not that the posterior is calibrated on hard satisfiable instances, where the Q6 plan
  predicts over-confidence. The rigorous posterior cannot move at n = 250, as the record said.
- The CUDA walk is one thread per slot, latency-bound; a warp per slot was not tried.

## Departures from the brief, with the reason

- Runs are batch-synchronous (run k = seed_steps * luby(k) iterations then polish_flips *
  luby(k) flips, every slot restarting together) instead of the 0.1 per-slot Luby index,
  because the walk phase needs one budget per launch; `--luby-unit` stays as the old
  spelling of `--seed-steps` so `benchmark/results.md` and the 0.1 harness still run.
- `walk_flips_per_launch` (32) steps per kernel launch instead of one flip per launch: the
  launch-bound Python kernel was the artefact to remove; the certificate is checked after
  every launch and a satisfied slot idles inside the launch.
- The metropolis rule proposes a uniform variable of the formula (the annealing move of the
  Python record, symmetric, so exp(beta S) is stationary), not a variable of a violated row.
- The tilted seed steps theta plainly with the decreasing rate, not with Adam (the Python's
  default optimiser), because the brief asked for the decreasing step and no control variate.
- Parities are rows of the same formula with a flag, so one occurrence list serves gradient
  and walk; the parser reads both `x 1 2 0` (cnf2xnf) and `x1 2 0` (the toolkit's writer,
  whose glued literal the first version dropped, caught by the toolkit's re-multiplication).
- The verification through `decide-rank-by-sat --solver` needed an adapter named xnfsat
  (`benchmark/as-xnfsat/`), because the toolkit hands x lines by name and runs
  multilinear-sat on its 3-cut CNF; the toolkit itself is not modified. The instance was not
  solved by either route, nor by xnfsat in the toolkit's own record.
- The compiled Beta prior default is the C++ uniform-arm fit on uf250 (0.4698, 5.0207), not
  the Python calibration's (0.4546, 0.8283), which was fitted on its tilted_walk restart
  (mean p 0.354), a different restart from the one this port polishes with.
- The MM-Challenge cap is 20 s at 1024 slots, five seeds; the brief left the cap to me.
- The tilted arm ran on uf250 only, seeds 0 and 1, and was stopped after 7 of its 120 runs when
  the package reached 97 C under the coordinator's 30-minute ceiling on the card; its row says
  so, and the Python record's verdict on all three families stands.
