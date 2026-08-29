# 4. Positionnement

## Corrections to our own notes, each with the sentence it corrects

**1. The FFT is not FourierSAT's, and it is not a product tree.**
`gaussian_surrogate/method/origin.md` says: *"Its strength is hybrid instances (clauses
with XOR and cardinality constraints), where a product tree over prod_j (1 + y_j z)
evaluates symmetric constraints by FFT."* `origin-notes-tewf.md` says the same: *"Its
niche is hybrid CNF + XOR + cardinality, where the FFT-based product tree over ∏_j (1 +
y_j z) evaluates symmetric constraints cheaply."* Both are wrong about FourierSAT.
FourierSAT computes those coefficients by expanding `prod_i (a_i + t)` directly, "in
O(k_c^2) time", and its text contains no transform [kyrillidis2020fouriersat]. The FFT
appears three years later, in FastFourierSAT, and is a batched length-(k+1) DFT of the
sequences `[x_i, 1]` with a pointwise product and an inverse transform; its sequential
complexity is also O(k^2) and the gain is parallel, O*(log k) ideal time
[cen2025fastfouriersat].

**2. XOR needs no FFT at all.** `method/open-directions.md` says: *"Constraints other than
clauses (XOR, cardinality), where continuous methods have their documented wins and where
the product-tree FFT of FastFourierSAT is needed."* Not for XOR: the Walsh coefficient
vector of a parity is `[1 0 ... 0]` and its gradient reduces to O(k)
[cen2025fastfouriersat, Cor. 2]. The FFT earns its place on cardinality-like symmetric
constraints of large width, which the toolkit's GF(2) encoding does not contain.

**3. Our own `--plain-cnf` is the worst measured encoding for SLS.**
`satisfiability/method/gf2-as-cnf.md` says: *"A solver without native XOR expands each
parity into `r−1` fresh variables and `4(r−1)` clauses. That is `--plain-cnf`."* That is
the linear 3-cut encoding, and on exactly these matrix-multiplication instances it is the
worst of the eight CNF encodings measured, while native XNF beats all of them
[nawrocki2021xnf]. The sentence is correct as a description and misleading as a default.

**4. The restart claim in `literature/review.md` survives, sharpened.** It says: *"No
continuous-optimization analogue of a restart schedule specific to this relaxation was
found in the reviewed literature."* Still true, and now measurable: neither
[kyrillidis2020fouriersat] nor [cen2025fastfouriersat] contains the string "Luby" or "Las
Vegas" anywhere in its full text (grep, 0 hits each). What FastFourierSAT does propose is
heuristic, not scheduled: exponential-recency constraint reweighting and a rephasing
policy over original, flipped and random phases.

**5. The claim that nothing is proven for continuous dynamics needs one qualification.**
`literature/review.md` says: *"no source in this review connects either bound to the basin
of attraction of gradient or quasi-Newton dynamics on the multilinear relaxation."* True
for gradient dynamics. But a claim about continuous dynamics does exist and should be
named: the continuous-time system of [ercseyravasz2011ctds] "finds solutions in polynomial
continuous-time, however, at the expense of exponential fluctuations in its energy
function", supported by "analytical arguments and simulations". It is not a theorem about
our relaxation and it moves the exponential into an analog variable, but it is not
nothing. On the discrete side there are now real Las Vegas results next door
[istrate2019walksat, lorenz2022longtailed].

**6. A date.** The brief lists "Jia, Moore, Selman 2005". The paper appeared at SAT 2004;
2005 is the LNCS volume [jia2005spinglass]. The arXiv record says so in its own comment.

## Not done in the world, as far as this review found

- **No continuous relaxation has been used as the initial-assignment generator for an SLS
  solver.** NLocalSAT's generator is a graph network [zhang2020nlocalsat]; TurboSAT and
  GaloisSAT hand their relaxed points to CDCL, not to SLS [dai2025turbosat,
  kim2026galoissat]. Three arXiv phrasings returned nothing (`queries.md`, Q17 to Q19).
  Not found, not "does not exist". [nawrocki2021xnf] names this combination as future
  work: "combining the approach used by NLocalSAT with xnfSAT".
- **No Fourier or continuous solver has been run on Brent equations.** `all:"FourierSAT"
  AND all:"matrix multiplication"` returns 0 on arXiv; `abs:"tensor rank" AND
  abs:"continuous optimization" AND abs:"GF(2)"` returns 0.
- **No Las Vegas restart schedule inside a CLS solver**, per correction 4 above.

## Not done here

- The toolkit has no SLS solver wired in at all. Its README names kissat first, then
  cryptominisat and cadical, all CDCL, on a problem family where the published finding is
  that CDCL is the wrong family [heule2019localsearch].
- The toolkit emits parities separately and only expands them at write time, which is
  exactly what an XNF writer needs; nothing consumes them yet.
- The Gaussian-surrogate branch has never been run on anything but uniform random 3-SAT.
