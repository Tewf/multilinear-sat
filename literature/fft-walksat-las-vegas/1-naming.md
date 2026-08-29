# 1. Encadrer le sujet: what the field calls each half

**The problem in one sentence.** Run a differentiable relaxation of a Boolean formula to
produce a starting point, hand that point to a flip-based local search, restart, and
report only certificate-checked satisfying assignments, so that the algorithm is never
wrong and its running time is random.

Our name for it, "FFT plus WalkSAT as a Las Vegas algorithm", names three things the
field names separately, and one of the three does not exist under that description.

## The continuous half

- **Continuous local search (CLS)** is the field's term for the whole line, used as a
  category name by every paper in it [cen2025fastfouriersat, christopher2026parallelcls].
  It is distinguished from **discrete local search (DLS)** or **stochastic local search
  (SLS)**, which flips bits, and from **CDCL**.
- **Walsh expansion**, **Walsh-Fourier expansion** and **multilinear extension** name the
  same polynomial. FastFourierSAT reserves "Walsh transform" for it explicitly, "to
  distinguish it from the Fourier transform" [cen2025fastfouriersat, footnote 1].
- **The FFT is over the constraint's width, not over assignments.** What the transform
  computes is the **elementary symmetric polynomials (ESPs)** of the literals of one
  symmetric constraint, by the **convolution theorem** applied to the `k` length-2
  sequences `[x_i, 1]` [cen2025fastfouriersat, Def. 1 and Alg. 2]. The object Mohamed's
  notes call "the product tree over prod_j (1 + y_j z)" is the ESP generating function.
  The field's word for the whole family is **symmetric constraint** or **pseudo-Boolean
  constraint**; AFSAT titles itself "symmetric pseudo-Boolean" [christopher2026afsat].
- **Hybrid constraints** means CNF plus XOR plus cardinality plus NAE in one formula
  [kyrillidis2020fouriersat]. It is the niche this line claims.

## The discrete half

- **WalkSAT** is one solver [selman1994walksat]; the family is **SLS**, and the modern
  members are **probSAT** [balint2012probsat], **YalSAT** [biere2017yalsat], **CCAnr**,
  **SATLike**, **NuWLS**. YalSAT is a probSAT-based, WalkSAT-derived solver
  [nawrocki2021xnf, section 4].
- Parity inside SLS has a name: **XNF**, a DIMACS extension carrying clauses and XORs
  side by side, with the solver `xnfSAT` and the extractor `cnf2xnf` [nawrocki2021xnf].
- Parity inside CDCL has two: **DPLL(XOR)** and **parity reasoning** [laitinen2012parity],
  and **Gauss-Jordan elimination** as CryptoMiniSat implements it [soos2009cryptominisat,
  soos2019bird, soos2023proofgauss].

## The Las Vegas half

- **Las Vegas algorithm**: "always produces the correct answer but whose running time is a
  random variable" [luby1993]. A CLS or SLS solver is Las Vegas only on satisfiable
  instances and only because its answer is certificate-checkable; on unsatisfiable ones
  it is **incomplete** and says nothing, which is the word the field uses
  [kyrillidis2020fouriersat, "an incomplete SAT solver"].
- **Universal restart schedule** and **run-length distribution** [luby1993];
  **heavy-tailed runtime distribution** [gomes2000heavytails]; and for SLS specifically,
  **long-tailed** and **Johnson SB** [lorenz2022longtailed].

## Our instances

The toolkit's GF(2) encoding of `rank(T) <= r` is the field's **Brent equations**
[heule2019localsearch, nawrocki2021xnf]. Searching for the words "tensor rank by SAT"
finds our own framing; searching for "Boolean Brent equations" finds the benchmark, the
solver and the record. This is the same naming failure as in
`memory/literature-review-before-building.md`, in the same repository.
