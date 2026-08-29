# State of the art

Upper bounds (what an algorithm achieves) are kept apart from lower bounds (what no algorithm
can achieve). Where a paper's own numbers are quoted, the text was fetched; where none was
obtainable, that is said.

## Clause and literal reduction: who holds the record and by what measure

The record holder is not a paper, it is a preprocessor inside a competition CDCL solver.
Chapter 9 [biere2021preprocessing], full text fetched, states that bounded variable elimination
as implemented in SatELite and then MiniSat 2.0 "contributed to the largest improvement of
solver performance witnessed in the history of the SAT competitions" in 2005 and 2006 and that
it "is still arguably the most important practical preprocessing technique". The measure used
throughout the line is two-part: how many variables, clauses and literals remain after
simplification, and how the downstream solver's running time or solved count moves.

Eén and Biere's own numbers, read from the fetched full text, calibrate both parts.
Simplification: their combination of variable elimination, subsumption, self-subsumption and
definitional substitution reduces size by roughly a further factor of two over NiVER's variable
elimination alone on their Industrial Mix. Solving: on the IBM benchmarks "MiniSat requires a
timeout of about 250 seconds to solve 275 problems with full preprocessing, but a timeout of
more than 600 seconds with no preprocessing". The same paper reports the negative case in the
same voice: on CNFs already clausified well, "reduction rates of less than 5% were achieved,
and no measurable speedup". That sentence is the honest bar any new reduction has to clear.

The current implementations are `arminbiere/cadical` and `arminbiere/kissat`, both verified by
`gh repo view` on 2026-08-29 (MIT). Kissat has been the reference winner of recent SAT
competitions; no competition result was fetched during this review, so that statement is
carried from the repository's existing `literature/review.md` and is not re-verified here.

**Nothing in this line uses the covariance of clause indicators, or any spectral quantity.**

## Refutation of random 3-CNF: the algorithmic frontier

Upper bound. Feige and Ofek [feige2007easily], abstract fetched verbatim, give a polynomial
time algorithm that for most 3-CNF formulas with c n^{3/2} clauses finds a subformula with
Theta(c^2 n) clauses and refutes it by spectral techniques, improving on the previous
poly(log n) times n^{3/2}. They report an implementation and experiments. No hardware or
running time was obtainable. Coja-Oghlan, Goerdt and Lanka [cojaoghlan2006strong] extend strong
refutation to k-SAT; the density they achieve was not verified during this review, so no number
is stated here. Flaxman [flaxman2008spectral] solves *planted* satisfiable 3-CNF, a different
problem from refutation.

Lower bound. Random CNFs require polynomial calculus refutation degree Omega(n)
[bensasson2010pc], hence Nullstellensatz degree Omega(n), so no certificate that is a fixed
linear combination of clause polynomials exists for them. Sherali-Adams needs Omega(n) levels
for random constraint satisfaction optimisation [georgiou2009sagaps, charikar2009sagaps]. The
existence of a polynomial-time refutation at constant clause density remains open; nothing in
this review changes that.

**These spectral algorithms take the spectrum of an n by n matrix indexed by variables
[feige2007easily, Definition 5.1], not of an m by m clause covariance.**

## Exact correlation structure: the record is an exact computation, and it is a scalar

Sutton, Whitley and Howe [suttonwhitleyhowe2009] hold the record for computing landscape
correlation of k-SAT: exact, in polynomial time, from the Walsh decomposition, rather than
estimated by sampling a random walk. The abstract reports the ensemble expectation is invariant
to the clause-to-variable ratio, and that filtered benchmark sets deviate from it. No running
time, instance size or hardware appears in the abstract; the full text was not obtained. The
line that turns the same Walsh coefficients into search is Chicano, Whitley and collaborators
[chicano2014ball, tinos2015partitioncrossover, chicano2017million], whose headline is a
million-variable NK landscape. **Public code for either: not found**, on three `gh search
repos` phrasings.

## Community structure: a strong descriptive result and a weak predictive one

Upper bound on what it buys. [ansotegui2015relevant] uses communities to select relevant
learned clauses and reports an improvement; no number was fetched. Descriptive record:
application benchmarks have high modularity, random instances do not [ansotegui2019community],
abstract fetched. Lower bound on the explanation: instances with good community structure by
any metric with a natural property are still NP-hard [mull2016hardness], and across about 7000
formulas the structural parameters "only weakly correlate with CDCL solving time"
[zulkoski2017parameters]. Tooling: `ekuiter/SATGraf` (Java, MIT), `gh repo view` verified.

## Linear response and frozen variables

Best correction to a product-measure or Bethe covariance: loop correction, whose reported
accuracy is that "the loop-corrected error is approximately the square of the error of the
uncorrected approximate inference method" [mooijkappen2007loopcorrections], abstract fetched
from JMLR. Structural record for zero-variance directions in the solution space: Achlioptas and
Ricci-Tersenghi [achlioptas2006geometry], abstract fetched, prove that clusters appear well
below the satisfiability threshold and that inside each cluster most variables are frozen. That
is a theorem about the uniform measure on solutions, not about a product measure at an interior
point p, and no algorithm follows from it directly.
