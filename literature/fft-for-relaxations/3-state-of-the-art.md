# Etat de l'art: records, method, measure, hardware

Upper bounds (an algorithm achieves this) are kept apart from lower bounds (no algorithm in
a class can do better).

## Exact spectrum of a CNF: the record is the input size, and it was set in 1998

[rana1998walsh] computes every nonzero Walsh coefficient of a MAX-SAT function in
O(2^K C) time, K the largest clause width, C the clause count. For fixed K that is linear
in the formula, "the same complexity as the time required to simply write down the SAT
expression" (full text). Nothing can beat it and nothing has tried; the later literature
uses the formula rather than improving it. Measured by: nothing, it is a closed form.
Hardware: irrelevant.

Sparse transform algorithms are a separate record for a separate problem. [cheraghchi2016sparse]
computes a k-sparse Walsh-Hadamard transform of a length-N vector in k^{1+alpha}(log N)^{O(1)}
deterministic time from non-adaptive queries; [li2015spright] does it by sparse-graph
decoding. Both take query access to an unknown function. For a CNF the answer is already
written down, so neither is the state of the art *for us*: they are the state of the art
for the case where the formula is not given.

## Exact landscape statistics: [sutton2009correlation], 2009

Record: exact autocorrelation function and correlation length of any k-SAT instance in
polynomial time, from the Walsh decomposition, plus the closed-form ensemble expectation
over uniformly random instances. Measure: the autocorrelation of the evaluation function
along a one-bit-flip random walk, and the correlation length derived from it. Published
finding used here as a prediction: the expectation "is invariant to the constrainedness of
the problem as measured by the ratio of clauses to variables" (abstract). Extended to any
Hamming radius by [sutton2012moments]. No public implementation was found: `gh search
repos` returned zero on "Walsh analysis SAT landscape", "fitness landscape analysis MAXSAT
Walsh" and "gray box optimization MAXSAT" (see `queries.md`). Not found, not absent.

## Gray-box search on MAX-SAT: the Whitley group, 2018 to 2025

Upper bound of the practical kind: [chen2018pxsat] reports PXSAT (partition crossover plus
AdaptG2WSAT) outperforming CCLS, winner of several MAXSAT evaluations, on application
instances; [dunton2022pxpre] speeds partition crossover up by one to two orders of
magnitude on 478 SAT Competition 2014 instances. Measure: solution quality on application
benchmarks, wall clock on a CPU; no GPU anywhere in this line. The structural record is
[whitley2023lattices] and [whitley2025fractal]: for every k-bounded pseudo-Boolean
function, including MAX-kSAT, the offspring of partition crossover form lattices whose
evaluations satisfy a linear equation, exactly when the child is a local optimum and as an
upper bound otherwise.

## Continuous relaxation on a GPU: AFSAT, June 2026

[christopher2026afsat] is the current engineered endpoint of the FourierSAT line and is
newer than anything in `../review.md`: a full JAX solver over heterogeneous symmetric
constraint types, with a tailored discrete Fourier transform for numerical stability and
near-linear scaling across accelerators, reporting improved stability, runtime and memory
over FastFourierSAT. Measure: its own comparison against FastFourierSAT, on GPUs; the
abstract gives no competitor solver and no benchmark suite name. [cen2025fouriercsp]
extends the same expansion to finite-domain CSP with convergence rates.

## Lower bounds, none of which is about our dynamics

- Approximation: 7/8 is achieved by an SDP [karloff1997sdp] and is tight, since 7/8 + eps
  is NP-hard (Hastad, cited in `../review.md`). Under the unique games conjecture the SDP
  integrality gap is the hardness threshold for every CSP [raghavendra2008every], with the
  invariance principle of [mossel2010noise] as the analytic engine. These bound the value a
  relaxation can certify, not where an ascent lands.
- Algorithmic phase transition: low-degree polynomial algorithms fail above clause density
  (1 + o_k(1)) kappa* 2^k log k / k, kappa* about 4.911 [bresler2022lowdegree]. The class
  is defined by degree in the random instance and is stated asymptotically in k. A batched
  Adam ascent is not shown to be in it, and k = 3 is not covered.
- Search difficulty from the spectrum: [rana1998walsh] proves the low-order schema averages
  of a MAX-SAT function are nearly all equal to w_0 = 7C/8, hence uninformative;
  [heckendorn2002embedded] proves that having all the epistatic interactions and the
  hyperplane moments in polynomial time still leaves an NP-complete problem. These are the
  strongest published statements against expecting the spectrum alone to guide a search,
  and they are about the discrete landscape, not about a gradient flow on the cube.

## The gap in the state of the art

Nobody found here computes the spectrum of a *relaxation* and uses it to predict a
continuous trajectory. The 1998 to 2012 line computes the spectrum and stops at the
discrete landscape; the 2020 to 2026 line evaluates the multilinear extension by FFT and
never looks at its spectrum. `4-positioning.md` states what follows.
