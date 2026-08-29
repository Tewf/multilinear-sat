# FFT plus WalkSAT as a Las Vegas SAT algorithm, and the toolkit's GF(2) instances

**The question.** Is "Fourier transform plus WalkSAT" an efficient Las Vegas algorithm
for SAT, and is it the right route for the tensor-rank toolkit's GF(2) encodings, which
are Tseitin AND gates plus one parity of width `r` per tensor entry?

## Verdict

1. **No FFT to run here.** A parity's Walsh vector is `[1 0 ... 0]` and its gradient costs
   O(k) with no transform [cen2025fastfouriersat, Cor. 2]; the rest is 2- and 3-clauses.
2. **The FFT is not FourierSAT's** (it expands `prod_i (a_i + t)` in O(k^2)
   [kyrillidis2020fouriersat]) but FastFourierSAT's, and it is a DFT, not a product tree.
3. **The WalkSAT half is done.** `xnfSAT`, YalSAT with native XOR, holds the record on the
   ⟨3,3,3⟩ rank-23 Brent instances, beating every CNF encoding [nawrocki2021xnf].
4. **CNF-encoded parity is SLS's documented failure**, 79 of 300 against FourierSAT's 300
   [kyrillidis2020fouriersat]; our `--plain-cnf` is the worst encoding measured there.
5. **No Las Vegas theory in this line:** neither FourierSAT nor FastFourierSAT contains
   "Luby" or "Las Vegas" (grep of both full texts, 0 hits). Details in section 4.

## The baselines

**(1) A hybrid continuous-plus-WalkSAT Las Vegas solver.** On uniform random 3-SAT:
`probSAT` [balint2012probsat, adrianopolus_probsat] and `kissat`, whose rephasing already
runs a WalkSAT walk [biere_kissat, `src/walk.c` called from `rephase_walking`], measured
by solve rate under a fixed wall-clock cap and median time on uf100-430 and uf250-1065,
and by expected time = restart cost divided by per-restart success probability. On parity:
FourierSAT's own 300 parity-learning-with-error instances, where the published numbers to
beat are WalkSAT 79, CryptoMiniSat with Gauss-Jordan roughly tied with FourierSAT's 300
[kyrillidis2020fouriersat], and FastFourierSAT solving all of them at a 60 s cap on an
A100 [cen2025fastfouriersat].

**(2) An SLS route on the toolkit's GF(2) encodings.** `xnfSAT` [vtec234_xnfsat] with
`cnf2xnf` [arminbiere_cnf2xnf] on `marijnheule/matrix-challenges` MM-Challenge-1
[heule_matrixchallenges], against its published Table 1: per instance, fraction of 192
runs solved within 1000 s, megaflips and mean time to solution on a Xeon E5-2690
[nawrocki2021xnf]. Best row 4-4-4-4-1: 100 % in 0.1 s on extracted XNF against 76.6 % in
67.4 s on linear 6-cut CNF. "Better" is that fraction and that time at fixed `r`.

Both baselines are public code with published numbers on a public benchmark, so this
review is finished.

## The files

[1-naming.md](1-naming.md) the names the field uses ·
[2-review.md](2-review.md) the map, by line ·
[3-state-of-the-art.md](3-state-of-the-art.md) records, measures, hardware ·
[4-positioning.md](4-positioning.md) what is undone, and our corrected sentences ·
[5-plan.md](5-plan.md) what to build, what to reject on paper ·
[queries.md](queries.md) every query · [references.bib](references.bib) every citation
with its verification note.
