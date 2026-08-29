# The map, by line

"Crossref" or "DBLP" means metadata only; "abstract" and "full text" mean the text was fetched
on 2026-08-29. Per-work detail and verification notes in `references.bib`.

## A. Clause and literal reduction, the baseline line

- Chapter 9 of the Handbook of Satisfiability [biere2021preprocessing], full text fetched,
  surveys unit propagation, failed literals, subsumption, self-subsuming resolution, connected
  components, bounded variable elimination, implication graphs, probing, blocked clauses,
  parity and circuit reasoning. No linear-algebraic or spectral criterion appears anywhere in
  it, and it calls explicit component decomposition "obsolete, at least for sequential plain
  CDCL solving", since phase saving already gets the effect.
- Eén and Biere [een2005satelite], full text, combine variable elimination with subsumption and
  self-subsuming resolution in SatELite; measured on industrial circuit verification only.
- Blocked clause elimination [jarvisalo2010bce], full text, matches circuit-level
  simplification without seeing the circuit; the eliminations form a lattice
  [heule2010clauseelim, heule2015clauseelim]. Bounded variable addition [manthey2012bva], full
  text, trades clauses for new variables to lower the sum of the two, re-deriving compact
  cardinality encodings (conference 2012, proceedings volume 2013).
- Equivalent-literal substitution, section 9.3.2 of [biere2021preprocessing], replaces each
  strongly connected component of the *binary* implication graph by a representative, so it
  consumes binary clauses; clausal congruence closure [biere2024congruence], full text, extends
  this by extracting gates and merging isomorphic ones, and does act on longer clauses.
- Vivification [piette2008vivify], inprocessing [jarvisalo2012inprocessing]: Crossref. Code,
  `gh repo view` verified: `arminbiere/cadical` (C++, MIT), `arminbiere/kissat` (C, MIT).

## B. Linear certificates

- Sherali and Adams [sheraliadams1990] define the hierarchy whose level 0 is the plain linear
  program; Nullstellensatz degree lower bounds start at [beame1996nullstellensatz]. Crossref.
- Ben-Sasson and Impagliazzo [bensasson2010pc]: random CNFs need polynomial calculus degree
  Omega(n), which is at most Nullstellensatz degree, so no constant-degree Nullstellensatz
  refutation exists for them. Sherali-Adams integrality gaps for random constraint satisfaction
  survive Omega(n) levels [georgiou2009sagaps, charikar2009sagaps], an adjacent and not
  identical statement. Crossref.

## C. Spectral methods on clause-derived matrices

- Goerdt and Krivelevich [goerdt2001spectral] open the line: recognise unsatisfiable random
  k-SAT by eigenvalue computations on matrices derived from the formula. Crossref only.
- Feige and Ofek [feige2007easily], abstract and full text fetched from the open-access Theory
  of Computing version, refute random 3-CNF with c n^{3/2} clauses. Their Definition 5.1
  settles the question for this whole line: the matrix is **n by n, indexed by variables**,
  built by adding +1 or -1 at position (x, y) per derived 2XOR clause. Not clause-clause, not
  a covariance.
- Coja-Oghlan, Goerdt and Lanka [cojaoghlan2006strong] give strong refutation heuristics by the
  same style of argument; Flaxman [flaxman2008spectral] works on *planted* satisfiable 3-CNF
  (SODA 2003, journal 2008). Crossref. None of the four uses a covariance under a product
  measure.

## D. Exact correlation structure by Walsh analysis

- Sutton, Whitley and Howe [suttonwhitleyhowe2009] is the closest published work; abstract
  fetched: "a polynomial-time Walsh decomposition of the k-satisfiability evaluation function
  allows us to compute the exact autocorrelation function and correlation length for any given
  k-satisfiability instance", with an ensemble expectation "invariant to the constrainedness of
  the problem as measured by the ratio of clauses to variables", and a warning that filtered
  benchmark sets are biased away from it. It is a scalar autocorrelation along a hypercube
  random walk, not an m by m matrix under a p-biased measure.
- Elementary landscapes [whitley2008elementary] and the decomposition methodology
  [chicano2011methodology] supply the algebra, with MAX-SAT a standing example [rana1998maxsat];
  gray-box use of the same coefficients gives improving moves in a Hamming ball in constant time
  [chicano2014ball], partition crossover [tinos2015partitioncrossover] and a million-variable
  hybrid [chicano2017million]. Crossref. Public code: **not found**.

## E. Community structure and modularity

- [ansotegui2012community] finds high modularity in application benchmarks; the journal version
  [ansotegui2019community], abstract fetched, adds what matters here: "random SAT instances are
  closer to the classical Erdos-Renyi random graph model, where no structure can be observed",
  and learned clauses destroy the original structure. [newsham2014impact] reports the
  modularity-to-runtime correlation (Crossref metadata only); the one place the line changes a
  solver is [ansotegui2015relevant].
- Three corrections, abstracts fetched from arXiv: instances with good community structure are
  still NP-hard [mull2016hardness]; over about 7000 formulas, backdoors, treewidth, backbones
  and community structure "only weakly correlate with CDCL solving time"
  [zulkoski2017parameters]; no parameter to date is both correlative and rigorous
  [li2021hierarchical]. Code: `ekuiter/SATGraf` (Java, MIT), `gh repo view` verified.

## F. Linear response, TAP, frozen variables

- [wellingteh2004linearresponse] gets pairwise covariances of the *variables* by
  differentiating belief-propagation marginals with respect to the fields; Mooij and Kappen
  analyse the Bethe approximation [mooijkappen2005bethe] and correct it by cavity distributions
  [mooijkappen2007loopcorrections], abstract fetched from JMLR.
- Plefka [plefka1982] is the expansion whose zeroth order is our product measure; the
  Almeida-Thouless condition [almeidathouless1978] is the eigenvalue criterion for instability.
- Achlioptas and Ricci-Tersenghi [achlioptas2006geometry], abstract fetched, prove solutions
  organise into exponentially many clusters in which "most variables are frozen, i.e., take
  only one value"; companions [krzakala2007gibbs, zdeborova2008isolated, zdeborova2016statphys]
  and the solver-facing backbone [monasson1999nature]. Crossref.

## G. Structured covariance in statistics, and H, the specific question

- Zeros in the covariance are a covariance graph model [coxwermuth1993, chaudhuri2007zeros],
  whose likelihood is not concave; zeros in the precision are the tractable Gaussian Markov
  random field case [rueheld2005]. Low rank plus diagonal [tippingbishop1999ppca] and
  randomised low rank [halko2011randomness] assume a matrix costly to touch or only sampled.
- **H. PCA or the spectrum of a clause covariance used to reduce a SAT instance: not found**,
  on nine queries across three services and four `gh search repos` phrasings (`queries.md`).
  Nearest neighbours are D (a scalar) and E (a graph). Clause weighting
  [thornton2006clauseweighting] adjusts weights during local search, with no spectral content.
