# Throughput against probSAT on one core

Part of [the findings of the walk](README.md); the sections read in that file's order.

## 1. Throughput (`../walk_throughput.md`, commit 0d98518)

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
