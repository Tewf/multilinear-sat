# Every query, with its service and hit count

The arXiv API (`export.arxiv.org`) timed out on every attempt from this machine's shell all
day, so arXiv was reached through `arxiv.org/abs` and `arxiv.org/pdf` pages instead. DBLP
rate-limited two batches and was retried. Semantic Scholar returned HTTP 429 on every call and
was abandoned; OpenAlex replaced it, since it serves reconstructible abstracts.

## Complexity and one-sided error

| Service | Query | Hits |
|---|---|---|
| DBLP | Some observations on the probabilistic algorithms and NP-hard problems | 1 |
| OpenAlex | doi 10.1016/0020-0190(82)90139-9 | 1, no abstract |
| ScienceDirect | article page and PDF for the same DOI | **HTTP 403 both** |
| Complexity Zoo | `/Complexity_Zoo:B` and `/Complexity_Zoo:R` | **HTTP 403 both** |
| OpenAlex | Probabilistic quantifiers and games Zachos | 2, no abstract |
| DBLP | Schoning probabilistic algorithm for k-SAT and constraint satisfaction problems | 1 |
| OpenAlex | doi 10.1109/SFFCS.1999.814612 | 1, full abstract |
| DBLP | On the complexity of k-SAT Impagliazzo Paturi | 1 |
| DBLP | Which problems have strongly exponential complexity | 2 |
| DBLP | An improved exponential-time algorithm for k-SAT | 2 |
| DBLP | Faster algorithms for 3-SAT PPSZ | **0 (query wrong: the field says "PPSZ analysis")** |
| WebSearch | PPSZ 3-SAT record 2026 "1.307" Jiang Cai | arXiv 2607.10697 |
| arXiv abs | 2607.10697 | abstract fetched |
| WebSearch, three phrasings | "NP in BPP implies NP = RP" Ko 1982 attribution | statement found only in secondary web text, **not in any fetchable primary source** |
| Berkeley CS278 | lecture08.pdf | fetched, RP/ZPP definitions |
| Harvard CS225 | lec2.pdf | fetched, Las Vegas and ZPP definitions |
| Crossref | Short proofs are narrow resolution made simple Ben-Sasson Wigderson | 3 |

## Typical-case algorithms for random k-SAT

| Service | Query | Hits |
|---|---|---|
| Crossref | A better algorithm for random k-SAT Coja-Oghlan | LNCS 2009 and SICOMP 2010 |
| Crossref | Walksat stalls well below satisfiability Coja-Oghlan Frieze | SICOMP 2014, SIDMA 2017 |
| Crossref | Linear upper bounds random walk small density random 3-CNF | SICOMP 2006, FOCS 2003 |
| OpenAlex | On belief propagation guided decimation for random k-SAT | full abstract |
| OpenAlex | Survey propagation an algorithm for satisfiability | full abstract (cs/0212002) |
| OpenAlex | doi 10.1109/focs.2008.11 | full abstract |
| arXiv abs | 2109.14409 (Gamarnik) | abstract fetched |
| arXiv abs | 2309.09913 (Kizildag) | abstract fetched |
| WebSearch | Bresler Huang algorithmic phase transition low degree polynomials | arXiv 2106.02129 |
| arXiv pdf | 1508.05117 (backtracking survey propagation) | full text extracted |
| arXiv abs | cond-mat/0501707 (Seitz, Alava, Orponen) | abstract fetched |
| arXiv abs | 2504.11174 (algorithmic thresholds and time scaling) | abstract fetched |
| Crossref | Proof of the satisfiability conjecture for large k | Annals 2022, STOC 2015 |
| Crossref | 3-SAT threshold upper bound 4.4898 Diaz Kirousis Mitsche | Diaz et al. TCS 2009, Dubois-Boufkhad 1997 |

## Run lengths, restarts, runtime prediction

| Service | Query | Hits |
|---|---|---|
| Crossref | Optimal speedup of Las Vegas algorithms Luby Sinclair Zuckerman | ISTCS 1993 and IPL 1993 |
| UT Austin | authors' PDF of the same | full text extracted, Theorems 5, 6, 7 |
| DBLP | Hoos on the run-time behaviour of stochastic local search algorithms for SAT | 1 |
| AAAI cdn | AAAI99-094.pdf | full text extracted (PAC) |
| UBC | hoos/Publ/aij99.pdf | full text extracted (exponential RLDs) |
| Crossref | Heavy-tailed phenomena in satisfiability Gomes Selman Crato Kautz | JAR 2000 |
| DBLP | Boosting combinatorial search through randomization | 1 |
| WebSearch | Lorenz Woerz "Johnson SB" Schoening runtime | arXiv 2210.13159 |
| arXiv abs and pdf | 2210.13159 | abstract and full text |
| Crossref | Runtime distributions and criteria for restarts Lorenz | SOFSEM 2017 |
| DBLP | Istrate satisfiability local search | **0** |
| DBLP | Istrate phase transition random satisfiability | 3, all on random Horn SAT, **not run-length distributions** |
| Crossref | Sequential tests of statistical hypotheses Wald | Ann. Math. Statist. 1945 |
| Crossref | Algorithm runtime prediction methods and evaluation | AIJ 2014 |
| Crossref | Understanding the empirical hardness of NP-complete problems | JACM 2009, CACM 2014 |
| arXiv abs | 0903.0695 (Haim and Walsh) | abstract fetched |

## An UNSAT posterior: nine phrasings, all "not found"

| Service | Query | Hits |
|---|---|---|
| OpenAlex | probabilistic certificate of unsatisfiability from failed local search restarts | **not found** (3 unrelated) |
| OpenAlex | Bayesian estimate probability instance unsatisfiable incomplete solver | **not found** (SATzilla, Markov logic) |
| OpenAlex | sequential probability ratio test SAT solver restart strategy | **not found** (SATzilla, Hoos) |
| Crossref | anytime confidence unsatisfiability stochastic local search posterior | **not found** |
| Crossref | statistical test unsatisfiability incomplete SAT solver confidence | **not found** |
| Crossref | predicting satisfiability of a formula machine learning classifier probability | **not found** at that phrasing; the right one is below |
| Crossref | stopping rule for incomplete SAT solver when to conclude unsatisfiable Bayesian | **not found** |
| Crossref | how long to run a randomized algorithm before concluding no solution exists confidence | **not found** |
| WebSearch | "calibrated" probability unsatisfiable formula anytime solver "reliability curve" | **not found** |
| WebSearch | "probability of unsatisfiability" posterior from failed SAT solver restarts Bayesian | **not found**; returned runtime estimation instead |
| gh search repos | unsat posterior probability | **0** |
| gh search repos | bayesian unsatisfiability confidence solver | **0** |
| gh search repos | anytime probability unsatisfiable SAT solver | **0** |
| Crossref | Predicting satisfiability at the phase transition Xu Hoos Leyton-Brown | **1, and this is the nearest prior art** |

## Incomplete methods that aim at UNSAT

| Service | Query | Hits |
|---|---|---|
| Crossref | Local search for unsatisfiability Prestwich Lynce | LNCS 2006, plus a 2009 follow-up |
| INESC-ID | prestwich+lynce-sat06.pdf | full text extracted |
| WebSearch | "Ranger" SAT solver Prestwich local search unsatisfiability | Ranger and GUNSAT named |
| DBLP, Crossref | GUNSAT greedy local search algorithm for unsatisfiability | DBLP rate-limited, Crossref **0 relevant**; found only via WebSearch and the ACM DL record |
| Crossref, arXiv | A scalable approximate model counter | CP 2013, arXiv 1306.5726 fetched |
| DBLP | Model counting: A new strategy for obtaining good bounds | 1 |
| AAAI | the MBound paper page | abstract fetched |
| DBLP | Ten challenges in propositional reasoning and search | 2 |
| DBLP | Deep cooperation of CDCL and local search for SAT | 2 |
| DBLP | hybridGM combining CDCL and local search | **0** |
| DBLP | CCAnr configuration checking local search structured SAT | **0** |

## Relaxation as the seed of local search: Q2's "not found", overturned

| Service | Query | Hits |
|---|---|---|
| Crossref | continuous relaxation initial assignment for stochastic local search SAT solver seeding | **3, and the second is the hit: Putikhin and Kascheev 2017** |
| Crossref | rounding a continuous optimisation solution to warm start WalkSAT satisfiability | Seitz et al., Coja-Oghlan et al. |
| OpenAlex | doi 10.1109/ewdts.2017.8110119 | full abstract |
| OpenAlex | doi 10.1111/coin.12438 | full abstract (Fu et al. 2021) |
| IEEE Xplore | document/8110119 | page empty to the fetcher |
| gh search repos | putikhin | **0** |
| gh search repos | continuous extension boolean formula probsat | **0** |
| gh search repos | continuous relaxation seed local search SAT solver | **0** |
| gh search repos | gradient initialization walksat assignment | **0** |
| gh search repos | GaloisSAT | 1 (ClemensHofstadler/galoissat) |
| gh search repos | TurboSAT | **0** |
| DBLP | AFSAT continuous local search SAT Christopher Gretton | **0** |
| DBLP | GaloisSAT Kim continuous SAT solver | **0** |
| DBLP | gradient descent initialisation for stochastic local search SAT | **0** |

## Benchmarks and code

| Service | Query | Hits |
|---|---|---|
| UBC | SATLIB benchm.html | fetched; uf/uuf families confirmed |
| DBLP | SATLIB an online resource for research on SAT | **0** (the paper is a book chapter DBLP does not index under that phrasing) |
| gh repo view | arminbiere/kissat, adrianopolus/probSAT, myxxxsquared/NLocalSAT, meelgroup/approxmc | 4 of 4 |
| gh api | kissat src/rephase.c, src/walk.c | both present, rephase_walking calls kissat_walk |
