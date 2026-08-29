# 5. Plan

## Reject on paper

- **"Add the FFT product tree to the solver for the toolkit's GF(2) instances."** Rejected.
  There is nothing symmetric and wide in that encoding: the AND gates are 2-clauses and
  3-clauses, and the one parity per tensor entry is a single Walsh monomial whose gradient
  costs O(r) with no transform [cen2025fastfouriersat, Cor. 2]. The FFT would be for a
  cardinality constraint we do not have.
- **"Port FourierSAT's product tree."** Rejected: it has none [kyrillidis2020fouriersat].
- **"Run the Gaussian surrogate on CNF-encoded parity."** Rejected before measuring. Its
  clause-level mean and pair terms are built from 3-clauses; a Tseitin-expanded parity
  hides the constraint behind auxiliary variables, which is the documented reason SLS
  fails there [nawrocki2021xnf, section 2] and why WalkSAT scores 79 of 300
  [kyrillidis2020fouriersat]. Any parity work must be native.
- **"Claim a Las Vegas guarantee."** Rejected. Nothing in this line has an expected-running
  time bound; the proven bounds belong to Schöning, PPSZ and WalkSAT-on-XORSAT
  [schoning1999, paturi2005ppsz, istrate2019walksat]. What we may claim is a Luby schedule
  over a run-length distribution we measure [luby1993], which is a different sentence.

## Build, smallest first

1. **An XNF writer in the toolkit** (`--emit-xnf`), beside `--emit-cnf`. The parities are
   already kept apart from the clauses until the file is written
   (`satisfiability/method/gf2-as-cnf.md`), so this is a formatter, not a redesign. Check
   it against `cnf2xnf` output on the same instance [arminbiere_cnf2xnf].
2. **Measure the SLS route against its published baseline.** `xnfSAT`
   [vtec234_xnfsat] on MM-Challenge-1 [heule_matrixchallenges], reproducing the
   [nawrocki2021xnf] Table 1 columns we can afford: fraction of runs solved within a cap,
   megaflips, mean time, over the ten instances. Then the same solver on our own ⟨3,3,3⟩
   rank-23 XNF, which is a different formula (19 251 variables and 56 619 clauses per
   `gf2-as-cnf.md`, against 26 541 variables per challenge formula
   [palladinos2026certificates]) because it carries no streamlining and no hardcoded
   pairings. **Better means: a higher solved fraction at the same wall-clock cap, or a
   lower mean time to solution, at the same `r`, on the same instances.**
3. **Only then, the continuous part.** The one gap this review could not fill from the
   literature is whether a relaxation makes a better SLS seed than a constant. Two facts
   frame it: on these instances the all-zero start already beats random
   [nawrocki2021xnf], and CLS "shows promise as a sub-solver in hybridised settings,
   quickly completing partial assignments" [christopher2026parallelcls]. So the experiment
   is a three-way seed comparison into an unmodified `xnfSAT`: all-zero, random, and the
   rounded point of our objective, with everything else fixed. That is NLocalSAT's protocol
   [zhang2020nlocalsat] with a relaxation in place of the network, which is the
   combination nobody was found to have run.
4. **Random 3-SAT stays a separate track**, and its baseline is unchanged: `probSAT`
   [adrianopolus_probsat] and kissat with its own walk [biere_kissat]. The measure that
   matters for a Las Vegas reading is expected time to a solution, that is, cost of one
   restart divided by the probability that one restart succeeds, which
   `gaussian_surrogate/findings.md` already reports both halves of.

## What would change the verdict

- If our objective's rounded point seeds `xnfSAT` better than all-zero on MM-Challenge-1,
  the hybrid is worth a paper-sized claim, because step 3 is unoccupied ground.
- If it does not, the honest conclusion is that on Brent equations the useful ingredient
  was native XOR and not the relaxation, and the branch should say so.
- Neither outcome touches unsatisfiability. Challenge 2 is still open and the ten formulas
  once expected to be unsatisfiable are not [palladinos2026certificates], so any lower
  bound the toolkit reports on these instances needs its own proof route.

## Order

Step 1 is hours. Step 2 needs no GPU and answers the toolkit question by itself. Step 3
needs step 2 to have a baseline at all. Step 4 is already running elsewhere in the branch.
