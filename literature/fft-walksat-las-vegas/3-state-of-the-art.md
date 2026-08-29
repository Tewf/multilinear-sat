# 3. État de l'art: who holds what record, measured how

## (d) Parity: the failure of SLS on CNF-encoded XOR, and its two fixes

| claim | number | source |
|---|---|---|
| WalkSAT on CNF-encoded parity learning with error | 79 of 300 solved | [kyrillidis2020fouriersat] |
| FourierSAT, same 300 instances | 300 of 300 | [kyrillidis2020fouriersat] |
| CryptoMiniSat with CNF+XOR, same benchmark | "roughly a tie" with FourierSAT | [kyrillidis2020fouriersat] |
| PalSAT (parallel YalSAT) on the 2023 parity benchmark | 102 problems | [cen2025fastfouriersat] |
| GradSAT / virtual best without CLS, same | 300 / 438 | [cen2025fastfouriersat] |
| FastFourierSAT, same | all instances, 60 s cap, A100 | [cen2025fastfouriersat] |
| WalkSAT on ordered spin-glass 3-SAT | "harder than any other known generator of satisfiable instances" | [jia2005spinglass] |
| Survey propagation on the same | fails at 25 variables | [jia2005spinglass] |
| Regular-graph parity instances, all solvers | "state-of-the-art solvers scale exponentially in the instance size" | [haanpaa2006] |

The physics reading of why parity is glassy yet easy for the right method is
[riccitersenghi2010glassy]. The two fixes are algebraic, not stochastic: Gauss-Jordan
elimination inside CDCL [soos2009cryptominisat], engineered as BIRD [soos2019bird], then
lazily [soos2020tinted], with proofs [soos2023proofgauss]; and the DPLL(XOR) parity module
[laitinen2012parity], extended in 2026 to disjunctions of parities [beame2026resoplus].
The third fix, and the only one on the SLS side, is native XOR inside the flip loop
[nawrocki2021xnf]. Public code: [msoos_cryptominisat], [vtec234_xnfsat],
[arminbiere_cnf2xnf].

**Does a Fourier solver handle XOR natively?** Yes, and without any transform. Only
GradSAT and FastFourierSAT "can natively accept XOR and cardinality constraints"; for the
others the paper CNF-encodes them [cen2025fastfouriersat, appendix D]. FourierSAT accepts
XOR natively too, its Fourier expansion being closed form
[kyrillidis2020fouriersat, Prop. 2]. Both are public Python
[vardigroup_fouriersat, seeder_fastfouriersat].

## (e) Matrix multiplication over GF(2): two different "local searches"

**SAT local search.** [heule2019localsearch] encodes the Brent equations "over Z_2 as
coefficient domain, so that multiplication translates into 'and' and addition translates
into 'xor'", 729 cubic equations in 621 base variables for ⟨3,3,3⟩, and reports that
"local search SAT solvers outperform CDCL solvers consistently in this application",
blaming CDCL's backtrack levels above 100. The benchmark is public
[heule_matrixchallenges]; its README states that of ten satisfiable rank-23 formulas
with hardcoded type-3 pairings, "Five of these formulas can be solved using yalsat in a
few minutes. All of these formulas appear hard for CDCL solvers (and many local search
solvers)." Streamlining "reduced the runtime from minutes to seconds". YalSAT is public
[arminbiere_yalsat, biere2017yalsat]; the schemes the method produced are in
[heule2021newways].

**The record on those instances is xnfSAT** [nawrocki2021xnf]: YalSAT plus native XOR,
plus a weight `w_X` for XOR constraints and a `break` extended over XORs. Measured on
MM-Challenge-1, 192 runs per instance, 1000 s timeout, Xeon E5-2690. Extracted XNF beats
every CNF encoding on every instance; the reported extremes are 100 % of runs in 0.1 s
against 76.6 % in 67.4 s (instance 4-4-4-4-1, linear 6-cut CNF), and 2.1 % against 0 % on
the hardest (2-2-2-4-A). Among CNF encodings, performance rises with the cutting number
up to 6, and the 3-cut encoding is the worst. Two further findings: `cnf2xnf` recovers
the XORs from CNF at 0.3 s per formula with no loss, and the all-zero initial assignment
"performed much better than random initialization" on these instances.

**Flip-graph local search is a different thing and holds the actual rank records**: random
walks on a graph of schemes over Z_2, no SAT solver [kauers2023flipgraphs], improved
adaptively to ⟨4,5,5⟩ = 73 and ⟨5,5,5⟩ = 94 in characteristic two [arai2024adaptiveflip],
by symmetry to ⟨5,5,5⟩ = 93 and ⟨6,6,6⟩ = 153 over arbitrary fields
[moosbauer2025symmetry], across about thirty formats [kauers2025metaflip], and now with
an open-source C++ framework covering 680 formats [perminov2026flipframework]. The
reinforcement-learning entry in the same race is AlphaTensor [fawzi2022alphatensor].

**Upper and lower bounds are not the same claim here.** Everything above is an upper bound
on rank. The lower-bound side by SAT is thin: [yang2024rulingout] rules out rank at most
21 for ⟨3,3,3⟩ over Z/2Z only under imposed symmetries, and Challenge 2 of
[heule_matrixchallenges] asks for unsatisfiability proofs that nobody has produced. A 2026
audit found those ten "expected UNSAT" formulas are in fact satisfiable, because their
hardcoded pairings are positive unit clauses that require but do not forbid incidences
[palladinos2026certificates]. Whether ⟨3,3,3⟩ has a rank-22 scheme is open.
