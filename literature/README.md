# Literature

One folder per question, the steps of a thesis as files (naming, review, state of the
art, positioning, plan, queries, references), each at most about 80 lines. The contract
every review is written to: `2026-08-28_gaussian-surrogate-sat/review-contract.md`
(not in this repository). A review is finished when its README names the baseline to
compare against and what "better" is measured by.

| Folder or file | Question | Branch | Status |
|---|---|---|---|
| `review.md`, `references.bib` | the multilinear-relaxation line: FourierSAT, GradSAT, FastFourierSAT, the discrete baselines, the bounding theorems, this library's positioning | main | done 2026-08-28 |
| `gaussian-like-objectives/` | second-moment or normal-approximation objectives for SAT and CSP relaxations: has anyone ascended P(all satisfied) from the mean and variance of the count; the sampling version (cross-entropy method, estimation of distribution algorithms) | gaussian-surrogate | done 2026-08-29 |
| `fft-walksat-las-vegas/` | the FFT of constraints plus WalkSAT as an efficient Las Vegas solver, and for the tensor-rank toolkit's GF(2) parity instances | gaussian-surrogate | done 2026-08-29 |
| `fft-for-relaxations/` | Fourier and Walsh analysis as a tool to study SAT relaxations: spectra, influences, landscape correlation, low-degree approximation | gaussian-surrogate | done 2026-08-29 |
| `tanh-parametrisation.md` | the smaller question: mirror descent, exponentiated gradient, Ising-machine nonlinearities as the geometry of the relaxation | gaussian-surrogate | done 2026-08-29 |
| `anytime-unsat-confidence/` | an anytime Las Vegas solver with a calibrated UNSAT posterior: the bounding theorem (SAT in RP implies NP = RP), typical-case algorithms, run-length distributions, incomplete UNSAT methods, the relaxation-seeded walk (occupied in 2017) | gaussian-surrogate | done 2026-08-29 |
| `tilted-sampling-loop/` | gradient and sampling as one tilted-objective loop: natural evolution strategies, cross-entropy, control variates, annealed and population sampling, sample-guided decimation, and whether GPU parallelism compensates slow mixing | gaussian-surrogate | in progress 2026-08-29 |
| `covariance-structure/` | the covariance of the clause vector: null space, spectrum, collinearity, for literal and clause reduction | covariance-reduction | done 2026-08-29; the question closed, see that branch's `gaussian_surrogate/covariance/README.md` |

`review.md` was produced by condensing six internal reviews and the prototype benchmark
written on 2026-08-26 (unpublished working notes), then independently re-verifying the
FastFourierSAT and FourierSAT GitHub repositories and about twenty citations against
DBLP, arXiv and Crossref on 2026-08-27/28.
