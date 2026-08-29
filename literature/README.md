# Literature

One folder per question, the steps of a thesis as files (naming, review, state of the
art, positioning, plan, queries, references), each at most about 80 lines or a folder that
reads in order. Every review was written to one contract (kept outside this repository): a
review is finished when its README names the baseline to compare against and what "better"
is measured by. Every `references.bib` entry says how it was verified.

| Folder or file | Question | Status |
|---|---|---|
| [`review.md`](review.md), [`references.bib`](references.bib) | the multilinear-relaxation line: FourierSAT, GradSAT, FastFourierSAT, the discrete baselines, the bounding theorems, this library's positioning | done 2026-08-28 |
| [`gaussian-like-objectives/`](gaussian-like-objectives/README.md) | second-moment or normal-approximation objectives for SAT and CSP relaxations: has anyone ascended P(all satisfied) from the mean and variance of the count; the sampling version (cross-entropy method, estimation of distribution algorithms) | done 2026-08-29 |
| [`fft-walksat-las-vegas/`](fft-walksat-las-vegas/README.md) | the FFT of constraints plus WalkSAT as an efficient Las Vegas solver, and for the tensor-rank toolkit's GF(2) parity instances | done 2026-08-29 |
| [`fft-for-relaxations/`](fft-for-relaxations/README.md) | Fourier and Walsh analysis as a tool to study SAT relaxations: spectra, influences, landscape correlation, low-degree approximation | done 2026-08-29 |
| [`tanh-parametrisation.md`](tanh-parametrisation.md) | the smaller question: mirror descent, exponentiated gradient, Ising-machine nonlinearities as the geometry of the relaxation | done 2026-08-29 |
| [`anytime-unsat-confidence/`](anytime-unsat-confidence/README.md) | an anytime Las Vegas solver with a calibrated UNSAT posterior: the bounding theorem (SAT in RP implies NP = RP), typical-case algorithms, run-length distributions, incomplete UNSAT methods, the relaxation-seeded walk (occupied in 2017) | done 2026-08-29 |
| [`tilted-sampling-loop/`](tilted-sampling-loop/README.md) | gradient and sampling as one tilted-objective loop: natural evolution strategies, cross-entropy, control variates, annealed and population sampling, sample-guided decimation, and whether GPU parallelism compensates slow mixing | done 2026-08-29 |
| [`covariance-structure/`](covariance-structure/README.md) | the covariance of the clause vector: null space, spectrum, collinearity, for literal and clause reduction | done 2026-08-29; the question closed by measurement, see [`../gaussian_surrogate/covariance/`](../gaussian_surrogate/covariance/README.md) |

What the reviews settled, and the design notes and measurements they led to:
[`../method/`](../method/README.md) (the algorithm as proposed, as built and as measured) and
[`../benchmark/findings-walk/`](../benchmark/findings-walk/README.md).

`review.md` was produced by condensing six internal reviews and the prototype benchmark
written on 2026-08-26 (unpublished working notes), then independently re-verifying the
FastFourierSAT and FourierSAT GitHub repositories and about twenty citations against
DBLP, arXiv and Crossref on 2026-08-27/28.
