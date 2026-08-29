# Queries, 2026-08-29

A log, not prose. "hit" means the intended work was returned; Crossref totals are meaningless
for `query.bibliographic`, so the verdict is whether the target appeared in the top four.

## Crossref (`api.crossref.org/works?query.bibliographic=`)

Target found: `Effective Preprocessing in SAT through Variable and Clause Elimination`;
`Automated Reencoding of Boolean Formulas bounded variable addition`; `Blocked Clause
Elimination Jarvisalo Biere Heule`; `Clause Elimination Procedures for CNF Formulas`;
`Preprocessing in SAT Solving Handbook of Satisfiability chapter`; `The exact correlation
structure of k-satisfiability landscapes`; `Understanding elementary landscapes Whitley
Sutton`; `elementary landscape decomposition Chicano Whitley Alba`; `A methodology to find the
elementary landscape decomposition of combinatorial optimization problems`; `Efficient
recognition of random unsatisfiable k-SAT instances by spectral methods`; `Easily refutable
subformulas of large random 3CNF formulas`; `Strong refutation heuristics for random k-SAT`;
`A spectral technique for random satisfiable 3CNF formulas`; `The Community Structure of SAT
Formulas`; `Impact of Community Structure on SAT Solver Performance`; `Using Community
Structure to Detect Relevant Learnt Clauses`; `Community structure in industrial SAT instances
Ansotegui Giraldez-Cru Levy Simon`; `Linear Response Algorithms for Approximate Inference in
Graphical Models Welling Teh`; `On the properties of the Bethe approximation and loopy belief
propagation on binary networks`; `Linear dependencies represented by chain graphs Cox
Wermuth`; `Estimation of a covariance matrix with zeros Chaudhuri Drton Richardson`; `Finding
Structure with Randomness Probabilistic Algorithms for Constructing Approximate Matrix
Decompositions`; `A hierarchy of relaxations between the continuous and convex hull
representations for zero-one programming problems Sherali Adams`; `Lower bounds on Hilbert's
Nullstellensatz and propositional proofs`; `Statistical physics of inference thresholds and
algorithms Zdeborova Krzakala`; `On the solution-space geometry of random constraint
satisfaction problems Achlioptas Ricci-Tersenghi`; `Determining computational complexity from
characteristic phase transitions Monasson Zecchina Kirkpatrick Selman Troyansky`; `Optimal
Sherali-Adams gaps from pairwise independence`; `Integrality gaps for Sherali-Adams relaxations
Charikar Makarychev`; `Random CNF's are hard for the polynomial calculus Ben-Sasson
Impagliazzo`; `Gibbs states and the set of solutions of random constraint satisfaction
problems Krzakala Montanari Ricci-Tersenghi Semerjian Zdeborova`; `Vivifying propositional
clausal formulae Piette Hamadi Sais`; `Inprocessing rules Jarvisalo Heule Biere`; `clause
weighting local search satisfiability`; `The asymptotic order of the random k-SAT threshold
second moment`; `Stability of the Sherrington-Kirkpatrick solution of a spin glass model de
Almeida Thouless`; `Convergence condition of the TAP equation for the infinite-ranged Ising
spin glass model Plefka`; `Probabilistic principal component analysis Tipping Bishop`;
`Gaussian Markov Random Fields Theory and Applications Rue Held`; `Analysis of Boolean
Functions O'Donnell` (book chapter record only); `Walsh analysis of MAXSAT landscapes Rana
Heckendorn Whitley` (returned Rana and Whitley 1998, second hit); `Constraint satisfaction
problems with isolated solutions are hard` (returned it, but by Zdeborova and Mezard, not
Zdeborova and Krzakala as the brief says).

Not found (query: ...): `elementary landscapes an introduction`; `Flaxman spectral technique
random satisfiable 3CNF formulas SODA 2003` (only the 2008 journal version is indexed); `Loop
corrections for approximate inference on factor graphs Mooij Kappen`; `Efficient perturbation
analysis susceptibility belief propagation`; `Novel inference algorithm loop corrected belief
propagation Mooij Wemmenhove Kappen`; `Using the Nystrom method to speed up kernel machines
Williams Seeger`; `Integrating equivalency reasoning into Davis-Putnam procedure`; `Backbones
in optimization and approximation Slaney Walsh`; `Backbone fragility and the local search cost
Kilby Slaney Thiebaux Walsh` (returned Singer, Gent and Smaill 2000, different authors);
`Phase transitions in the coloring of random graphs Zdeborova Krzakala`; `backbone guided local
search maximum satisfiability` (only weighted variants); `principal component analysis SAT
instance clause matrix`; `spectral clustering conjunctive normal form formula decomposition`;
`singular value decomposition clause variable incidence matrix satisfiability`; `low rank
approximation Boolean satisfiability clause matrix`.

## DBLP (`dblp.org/search/publ/api`), title search only

- 1 hit: `exact correlation structure k-satisfiability landscapes`.
- 2 hits, both irrelevant (temporal-network centrality): `eigenvector clause`.
- 0 hits, so not found (query: ...): `clause covariance`; `spectral clause elimination`;
  `principal component analysis satisfiability instance`; `spectral SAT solver`; `eigenvalue
  satisfiability`; `covariance SAT solver`; `clause redundancy spectral`.
- Service failure, no result returned (repeated timeouts on 2026-08-29 morning): `Effective
  Preprocessing in SAT through Variable and Clause Elimination`; `Blocked Clause Elimination`;
  `Automated Reencoding of Boolean Formulas`; `matrix factorization SAT instances`; `clause
  clustering`; `equivalency reasoning Davis-Putnam`; `Vivifying propositional clausal
  formulae`; `Inprocessing rules`; `Bounded Variable Addition`; `The Community Structure of SAT
  Formulas`. All of these were covered by Crossref instead.

## arXiv (`export.arxiv.org/api/query`)

- 7 hits, four relevant: `abs:"SAT solver" AND abs:"community structure"` (1606.03329,
  1602.08620, 1706.08611, 2103.14992).
- 336 hits, none relevant, so not found: `abs:"susceptibility" AND abs:"satisfiability"`.
- 94 hits, none relevant, so not found: `abs:"satisfiability" AND abs:"principal component"`.
- 6 hits, none relevant, so not found: `abs:"CNF" AND abs:"spectral"`.
- 4 hits, none relevant, so not found: `abs:"clause" AND abs:"covariance"`.
- 1 hit, irrelevant, so not found: `abs:"co-occurrence" AND abs:"SAT"`.
- 0 hits, not found: `abs:"CNF formula" AND abs:"eigenvalue"`; `abs:"p-biased" AND abs:"clause"`.
- Empty response, service flaky earlier in the session: `all:"random k-SAT" AND all:spectral`;
  `au:Ofek_E AND all:refut`; `abs:"random k-SAT" AND abs:spectral`.

## Semantic Scholar (`api.semanticscholar.org/graph/v1`)

- `search?query=blocked+clause+elimination`: HTTP 429, rate limited, abandoned.
- `paper/DOI:` on fourteen DOIs: abstracts returned for 10.1145/1569901.1569952,
  10.1613/jair.1.11741, 10.1145/1132516.1132537; "no abstract" for the Springer and ACM records
  of 10.1007/978-3-642-12002-2_10, 10.1007/978-3-642-16242-8_26, 10.1007/11499107_5,
  10.1007/978-3-642-39611-3_14, 10.1007/3-540-44693-1_26, 10.1017/s096354830600784x,
  10.1002/rsa.20213, 10.1007/978-3-642-03685-9_10, 10.1007/s00037-010-0293-1,
  10.1145/2576768.2598304, 10.1007/978-3-319-09284-3_20; "paper not found" for
  10.1007/978-3-540-27836-8_45.

## GitHub (`gh`)

- `gh repo view`, all three exist: `arminbiere/kissat`, `arminbiere/cadical`, `ekuiter/SATGraf`.
- `gh search repos "elementary landscape"`: 6, none is a k-SAT Walsh computation.
- `gh search repos "SATGraf"`: 3, one relevant.
- `gh search repos "SAT solver"`: 3, used only to confirm the search works.
- 0 results, not found (query: ...): `walsh MAXSAT`; `gray box optimization pseudo-boolean`;
  `walsh coefficients pseudo-boolean`; `MAXSAT landscape analysis`; `hill climber pseudo
  boolean`; `clause covariance SAT`; `SAT preprocessing spectral clustering`; `CNF principal
  component analysis`; `SAT instance community detection`; `modularity SAT instances`.
- `gh search users chicano` and `gh search repos --owner=jfrchicano`: unsupported flag and
  non-existent user; Chicano's code was not located by any route tried.

## Direct fetches

- Fetched and read: `fmv.jku.at/papers/EenBiere-SAT05.pdf`;
  `fmv.jku.at/papers/JarvisaloBiereHeule-TACAS10.pdf`;
  `cca.informatik.uni-freiburg.de/papers/BiereJarvisaloKiesl-SAT-Handbook-2021-Preprocessing-Chapter-Manuscript.pdf`;
  `.../MantheyHeuleBiere-HVC12.pdf`; `.../BiereFazekasFleuryFroleyks-SAT24.pdf`;
  `theoryofcomputing.org/articles/v003a002/` and its PDF; `jmlr.org/papers/v8/mooij07a.html`.
- Failed: `dl.acm.org/doi/10.1145/1569901.1569952` (403); `link.springer.com/chapter/...` (303
  to an authentication endpoint, twice); `wisdom.weizmann.ac.il/~feige/mypapers/randomcnf.pdf`
  (connection reset); `tu-chemnitz.de/.../CGL04.pdf` (404); `math.cmu.edu/~adf/research/3sat.pdf`
  (404); `jair.org/index.php/jair/article/view/10983` (returned an unrelated article).
- Web search, nothing relevant, so not found (query: ...): `principal component analysis
  spectrum of clause co-occurrence matrix SAT instance reduction`; `covariance matrix of clause
  indicators SAT relaxation null space linear dependencies`. A third, `Feige Ofek "Easily
  refutable subformulas of large random 3CNF formulas" pdf spectral eigenvalue matrix`, located
  the open-access Theory of Computing version.
