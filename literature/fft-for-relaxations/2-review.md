# Revue de litterature: the Fourier spectrum of CNF and of its relaxation

"Full text" means the PDF was fetched and read on 2026-08-29; "abstract" names the service
the abstract came from that day. Works already in `../review.md` are extended, not restated.

## A. The exact spectrum of a CNF, in closed form

- **[rana1998walsh]** Rana, Heckendorn, Whitley, AAAI 1998, full text. Theorem 1: for a
  clause on K distinct variables with mask m and negation pattern neg(f),
  w_0 = (2^K - 1)/2^K, w_j = -2^{-K} psi_j(neg(f)) for non-empty j inside m, 0 outside.
  Every coefficient of a MAX-SAT function follows in O(2^K C) time, C the clause count, the
  size of the input. On MAX-3-SAT at n = 100 the nonzero coefficients are bounded by 100 at
  order 1, 3C at order 2 and C at order 3, all multiples of 1/8, with w_0 = 7C/8; low-order
  schema averages therefore sit near w_0 and a simple genetic algorithm has almost no
  signal. No relaxation, no gradient, uniform measure only.
- **[heckendorn1999summary]** Heckendorn, Rana, Whitley, GECCO 1999. PDF fetched from the
  authors' site (HTTP 200, 224 KB), font encoding broken, abstract only: Walsh analysis of
  "embedded landscapes" yields several summary statistics in polynomial time.
- **[heckendorn2002embedded]** Heckendorn, Evolutionary Computation 10(4), 2002, abstract
  from PubMed. Computes "the statistical moments of hyperplanes about the function mean and
  hyperplane mean" in polynomial time, then concludes that "knowing the epistasis and many
  of the hyperplane statistics is not enough to solve the exponentially difficult part of
  these general problems".
- **[odonnell2014abf]** O'Donnell 2014, Crossref: the vocabulary, no k-SAT computation.
  **[bernasconi1999spectral]** Bernasconi and Codenotti, IEEE TC 1999, Crossref: the same
  coefficients as a Cayley-graph eigenvalue problem; no SAT application.

## B. Landscape statistics of k-SAT computed from that spectrum

- **[sutton2009correlation]** Sutton, Whitley, Howe, GECCO 2009, abstract from Semantic
  Scholar. A polynomial-time Walsh decomposition gives "the exact autocorrelation function
  and correlation length for any given k-satisfiability instance", plus an ensemble
  expectation that "is invariant to the constrainedness of the problem as measured by the
  ratio of clauses to variables"; filtered instances deviate. No relaxation, no gradient.
- **[sutton2012moments]** (TCS 2012, Crossref) extends those moments to Hamming spheres of
  arbitrary radius; **[sutton2009theoretical]** (SLS 2009, Crossref) is title and venue only,
  with no abstract on Crossref or Semantic Scholar; **[whitley2008elementary]**,
  **[chicano2011eld]**, **[klemm2014rugged]** and **[stadler1996landscapes]** are the
  elementary-landscape and autocorrelation machinery they use, none of it SAT-specific.

## C. Gray-box exploitation of the same coefficients

- **[chen2018pxsat]** Chen, Whitley, Tinos, Chicano, GECCO 2018, abstract from Semantic
  Scholar: partition crossover decomposes the evaluation function into independent
  components and returns the best of exponentially many offspring in O(n); PXSAT beats CCLS
  on application instances. **[dunton2022pxpre]** (GECCO 2022, abstract from Semantic
  Scholar): restricting it to unsatisfied clauses speeds it up one to two orders of
  magnitude on 478 SAT Competition 2014 instances. Discrete throughout.
- **[whitley2023lattices]**, **[whitley2025fractal]**, **[whitley2024reduction]**, abstracts
  from Semantic Scholar and records from Crossref and DBLP: local optima of any k-bounded
  pseudo-Boolean function, MAX-kSAT included, lie on fractal lattices whose evaluations obey
  a linear equation, which explains the big valley. **[przewozniczek2025wdvig]**,
  **[unanue2021walshframework]** and **[chicano2016hillclimber]**, records fetched: the same
  coefficients as a dependency strength, a surrogate model, and a constant-time hill climber.

## D. The Fourier lens on random k-SAT itself

- **[friedgut1999sharp]** Friedgut with an appendix by Bourgain, JAMS 1999, Crossref: the
  sharp threshold for k-SAT is a Fourier-analytic theorem, with nothing algorithmic in it.
- **[bresler2022lowdegree]** Bresler and Huang, FOCS 2021, abstract from Semantic Scholar:
  low-degree polynomial algorithms fail above density (1 + o_k(1)) kappa* 2^k log k / k with
  kappa* about 4.911, covering Fix, belief and survey propagation guided decimation with
  bounded or mildly growing rounds, and local algorithms. The degree is in the instance, not
  in the relaxation variable p. **[gamarnik2020lowdegree]** and **[jones2022randomcsp]**
  carry the same overlap-gap machinery to circuits, Langevin dynamics and random Max-CSP.

## E. Spectral bounds on relaxations

- **[karloff1997sdp]** (7/8 SDP for MAX-3-SAT), **[mossel2010noise]** (noise stability of
  low-influence functions, the invariance principle) and **[raghavendra2008every]** (the SDP
  integrality gap as the hardness threshold for every CSP under the unique games
  conjecture), all three verified through Crossref. None is specialised to CNF or tied to a
  gradient method; `3-state-of-the-art.md` says what they do and do not bound.

## F. FFT evaluation of the multilinear extension

- **[bjorklund2007subset]** STOC 2007, abstract from Semantic Scholar: subset convolution in
  O(n^2 2^n) by Moebius transform and inversion, which is what the transform domain costs.
- **[cheraghchi2016sparse]** Cheraghchi and Indyk, SODA 2016, abstract from Semantic
  Scholar: deterministic k-sparse Walsh-Hadamard transform in k^{1+alpha}(log N)^{O(1)};
  **[li2015spright]** does the same by sparse-graph decoding. Both need query access to the
  function, not a formula, so neither applies when the spectrum is known.
- **[kyrillidis2020fouriersat]** and **[cen2025fastfouriersat]**, abstracts refetched from
  arXiv: the FFT in this line computes elementary symmetric polynomials, "the major
  computational task in previous CLS methods", that is, the multilinear extension of
  *symmetric* constraints. Plain 3-CNF contains none.
- **[christopher2026afsat]** Christopher and Gretton, arXiv:2606.06641, abstract from arXiv:
  AFSAT turns FastFourierSAT into a full JAX solver over mixed symmetric constraint types,
  with "a tailored discrete Fourier transform implementation" for floating-point stability.
- **[cen2025fouriercsp]** Cen, Wang, Zhang, Zhang, Fong, arXiv:2510.04480, v2 HTML read: the
  Walsh-Fourier transform generalised to finite-domain CSP, projected gradient and
  negative-entropy mirror descent on products of simplices with stated rates, and no
  interior local maximum. No sparsity analysis, no basin analysis, no code URL.
