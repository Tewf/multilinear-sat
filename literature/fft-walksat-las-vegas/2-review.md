# 2. Revue de littérature

Verification per work is in `references.bib`; "full text" below means the PDF was fetched
and read this session, "abstract" means the arXiv or publisher record was fetched.

## (a) Where the Fourier expansion needs an FFT, and where it does not

- **FourierSAT** [kyrillidis2020fouriersat] relaxes hybrid constraints to their Walsh
  expansion and runs projected gradient descent. It evaluates a symmetric constraint of
  width `k` by expanding `prod_i (a_i + t)` and reading the coefficients, "in O(k_c^2)
  time"; the paper contains no FFT and no product tree. Full text.
- **GradSAT** [kyrillidis2021gradsat] replaces the polynomial by a BDD and belief
  propagation, O(k^2) per symmetric constraint. CPU only. Abstract, plus the summary of
  its complexity given in [cen2025fastfouriersat, Fact 2].
- **FastFourierSAT** [cen2025fastfouriersat] is where the FFT enters: the ESPs of a
  constraint are the convolution of the `k` sequences `[x_i, 1]`, so a batched DFT,
  pointwise multiply, inverse transform. Sequential complexity stays O(k^2); the gain is
  ideal parallel time O*(log k) and a GPU mapping. Full text.
- **The parity exception, verbatim** [cen2025fastfouriersat, appendix B]: "the Walsh
  coefficient of an XOR constraint is f_XOR = [1 0 ... 0], i.e., the Walsh expansion only
  has the highest order term and all other entries are 0", and "Corollary 2 (Reduction)
  For XOR constraints, the complexity of running Autodiff for Alg. 2 can be reduced to
  O(k)." No transform is used or needed. Full text.
- **AFSAT** [christopher2026afsat] and **A Study of Parallel CLS**
  [christopher2026parallelcls] engineer the prototype into a solver: JAX, heterogeneous
  constraint widths, array sharding, "a tailored discrete Fourier transform" for numerical
  stability. The second reports that CLS "shows promise as a sub-solver in hybridised
  settings, quickly completing partial assignments" and that objectives are saddle-dense.
  Abstracts; no code found.
- **Out of the box** [zhang2025outofthebox] drops the box constraint for penalty terms so
  that unconstrained optimisers such as Adam apply. Abstract. **MatSat**
  [sato2021matsat] is an unrelated differentiable formulation as matrix cost minimisation.
  Abstract.

## (b) Relaxation as the generator for a discrete search

- **NLocalSAT** [zhang2020nlocalsat] trains a network to predict an assignment and seeds
  five unmodified SLS solvers with it; only the seed changes. Code public
  [myxxxsquared_nlocalsat]. The predictor is a graph network, not a relaxation. Abstract.
- **TurboSAT** [dai2025turbosat] encodes SAT as a binarised matrix product, optimises it
  on GPUs, and post-processes "promising partial assignments" with CDCL on many CPU
  threads: up to 200x over a state-of-the-art CPU solver on a DGX GB200. Abstract; no
  code found.
- **GaloisSAT** [kim2026galoissat] is the same shape over finite-field algebra, and reports
  8.41x PAR-2 in the satisfiable category of SAT Competition 2024 against Kissat and
  CaDiCaL. Abstract; no code found. Unrelated to `galoissat` [hofstadler_galoissat], a
  solver for polynomial systems over small finite fields.
- **Deep cooperation of CDCL and local search** [cai2021deepcoop] and kissat's own
  rephasing walk [biere_kissat] are the discrete-discrete version of the same idea, and
  they are what "beating CDCL" already includes.
- **Backbone-guided local search** [zhang2003backbone] pools WalkSAT optima into per
  literal frequencies; **SP-guided decimation** [braunstein2005survey] and **SP
  reinforcement** [chavas2005reinforcement] are the message-passing analogues. Records.

## (c) Las Vegas theory

- **Luby, Sinclair, Zuckerman** [luby1993]: the universal schedule is optimal to within a
  constant for an unknown run-length distribution. **Scaman** [scaman2023lasvegas] gives
  the modern reverse-Jensen restatement. **Gomes, Selman, Crato, Kautz**
  [gomes2000heavytails, gomes1997heavytails]: the distributions really are heavy-tailed.
- **Schöning** [schoning1999] (4/3)^n and **PPSZ** [paturi1998ppsz, paturi2005ppsz] are
  proven bounds for specific discrete algorithms. **Lorenz and Wörz**
  [lorenz2022longtailed] prove Schöning's runtime is approximately Johnson SB and that
  restarts help long-tailed distributions. **Istrate, Bonchis, Marin**
  [istrate2019walksat] bound WalkSAT's expected running time on satisfiable k-XORSAT by a
  drift argument. All abstracts; the last three are the only Las Vegas results this review
  found that touch parity or SLS directly.
- **Continuous dynamics** [ercseyravasz2011ctds]: a deterministic continuous-time system
  whose attractors are the solution clusters, which "finds solutions in polynomial
  continuous-time, however, at the expense of exponential fluctuations in its energy
  function", by "analytical arguments and simulations". Successors: an analog MaxSAT
  solver [molnar2018maxsat] and its GPU port [molnar2020gpu].

## (d) and (e)

Parity handling and matrix multiplication carry the answer to the toolkit question and
are set out with their numbers in [3-state-of-the-art.md](3-state-of-the-art.md).
