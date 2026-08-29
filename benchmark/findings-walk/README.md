# Findings: the walk in the library, measured

The Python record ([../../gaussian_surrogate/findings-tilted/](../../gaussian_surrogate/findings-tilted/README.md))
priced the seeded walk with a launch-bound PyTorch kernel at 3.2 k flips/s per chain. This
is the same algorithm inside the C++20/CUDA library, measured on 2026-08-29 on one RTX 4060
Laptop GPU (24 SMs, 8 GB) and an i5-12450H, CUDA 12.9, the card free of other processes
(checked with nvidia-smi before each stage), one GPU job at a time. Every number below is in
a JSONL record in [../](../README.md) with the command that made it, the seed, the commit and
the sha256 of the frozen binary; the tables beside each record are generated from it by the
script of the same name.

| File | What it prices |
|---|---|
| [throughput.md](throughput.md) | flips per second of the batched walk against probSAT on one core, both rules, five batch sizes |
| [seeds.md](seeds.md) | per-restart success and cost of a uniform start, all false, the ascent at 50, 200 and 500 steps, and the tilted seed, probSAT beside them |
| [posterior.md](posterior.md) | the Beta-mixture posterior on uf250 against uuf250, its reliability curve, its time to 0.99 against kissat |
| [parities.md](parities.md) | the native parity rows on MM-Challenge-1 and matmul_3x3x3 at 23, and the verification route through the toolkit |
| [caveats.md](caveats.md) | what each number does and does not carry |
| [departures.md](departures.md) | where the port departed from its brief, with the reason |

The variants of the walk priced against each other on one protocol, with the dominated ones
rejected and the survivor written as the algorithm: [../arms/](../arms/README.md).

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
