# Every query tried, 2026-08-29

Direct network access from the shell was unavailable (curl timed out on every host, with and
without the sandbox), so `gh` could not be used; GitHub was queried through its public REST
search interface and through repository pages.

## DBLP (`dblp.org/search/publ/api?q=...&format=json`)

| query | hits |
|---|---|
| `cross-entropy method satisfiability` | 0. **not found** |
| `Rubinstein counting satisfiability` | 0. **not found** |
| `cross-entropy method combinatorial optimization` | HTTP 429, no result |
| `Rubinstein cross entropy` | timed out at 60 s, no result |
| `estimation of distribution algorithm satisfiability` | connection reset, no result |

DBLP refused or dropped three of five requests; every one of them was rerun on Crossref or the
open web below.

## arXiv application programming interface (`export.arxiv.org/api/query`)

| query | hits |
|---|---|
| `all:"cross-entropy method" AND all:"satisfiability"` | 1, unrelated. **not found** |
| `ti:"A Semantic Loss Function for Deep Learning with Symbolic Knowledge"` | HTTP 429 |
| `ti:"Erdos Goes Neural"` | HTTP 429 |
| `ti:"Semantic Loss Function"` | HTTP 429 |

Rate-limited after the first request, so verification moved to the abstract pages.

## arXiv abstract pages (`arxiv.org/abs/<id>`), one record each

`1711.11157`, `2504.01173`, `2402.03640`, `2603.28796`, `2006.10643`, `2510.04480`,
`2506.00674`, `0709.1667`, `0910.1824`, `2101.10154`, `1809.10606`, `2207.05984`,
`2107.01188`, `1610.04317`, `cond-mat/0105319`, `2507.10360`, `1604.04153`, `2606.06641`,
`2212.04016`, `2510.25962`. Full text of `2603.28796` fetched as a portable document and read
with `pdftotext`. Two guessed identifiers were wrong: `1312.6156` returned a paper on CP-logic,
`1206.1122` one on terahertz conductivity; both intended works were found by title on Crossref.

## Crossref (`api.crossref.org/works?query.bibliographic=...`)

Exact top hit, used for the bibliography: Achlioptas and Moore two moments; Achlioptas and
Peres threshold; Chen and Shao local dependence; Arratia, Goldstein and Gordon Poisson; Roy
safety first; Hong Poisson binomial and the `poibin` package; Rubinstein 1999 and 2008; de Boer,
Kroese, Mannor and Rubinstein tutorial; Kushner 1964 (429 on the first attempt, answered on the
second); Wolpert, Strauss and Rajnarayan; Chavira and Darwiche; Coja-Oghlan decimation failure;
Charnes and Cooper; Yuille CCCP; Bapst and Coja-Oghlan Bethe.

| query | outcome |
|---|---|
| `estimation of distribution algorithm satisfiability SAT` | fuzzy hits only, none on the subject. **not found** |
| `CCCP algorithms to minimize the Bethe free energy of 3-SAT problem` | that item **not found**; returned Yuille 2002 and Bapst 2016 |

## Semantic Scholar (`api.semanticscholar.org/graph/v1`)

`paper/search?query=cross-entropy method satisfiability SAT`: HTTP 429.
`paper/arXiv:1912.01032/citations?limit=100`: 21 citing works listed, chased by title.

## GitHub code search (`api.github.com/search/repositories?q=...`)

| query | `total_count` |
|---|---|
| `SAT solver probability satisfied clauses gradient` | 0. **not found** |
| `Gaussian surrogate SAT moment objective` | 0. **not found** |
| `continuous local search SAT variance mean field` | 0. **not found** |
| `weighted model counting gradient literal weights differentiable` | 0. **not found** |

Repository pages fetched and confirmed to exist: `UCLA-StarAI/Semantic-Loss`,
`ML-KULeuven/PySDD` (reached through `wannesm/PySDD`), `meelgroup/ganak`,
`vardigroup/FourierSAT`, `adrianopolus/probSAT`, `VectorInstitute/VariationalNeuralAnnealing`.

## Open-web searches, for discovery only

Thirteen queries, each keeper then verified above: semantic loss and weighted model counting;
estimation of distribution algorithms with Bernoulli marginals for SAT; gradient ascent on the
probability that all clauses are satisfied; the cross-entropy method for satisfiability;
variational neural annealing and mean-field free energy for SAT; the product objection in
differentiable MaxSAT; the second moment as an objective for the satisfied count; the Local
Lemma, Shearer and cluster expansion; mean-field annealing and Hopfield networks for
satisfiability; Bethe minimisation, TAP and Plefka for constraint satisfaction; the univariate
marginal distribution algorithm and population-based incremental learning on MaxSAT; a normal
or Gaussian approximation of the satisfied count as a differentiable objective; covariance
between clause indicators as a second-order correction. The last two returned nothing on the
intended sense and are recorded as **not found**.

## Pages fetched directly

`people.smp.uq.edu.au/DirkKroese/publications.html`, five matching entries, the only place the
2007 cross-entropy counting manuscript was confirmed. `inspirehep.net/literature/1300704`
rendered empty without JavaScript: **not verified**, and therefore not cited.
