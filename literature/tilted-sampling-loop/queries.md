# Every query, with its service and hit count

Run 2026-08-29. The arXiv API (`export.arxiv.org`) returned an empty body from this machine all
day, so arXiv was reached through its abstract pages with WebFetch. DBLP answers but rate-limits
hard (HTTP 429) when several agents query it. Crossref was the workhorse; its corpus-wide
`total-results` is meaningless for a fuzzy bibliographic query, so what is recorded is whether the
target appeared in the returned top three.

## Crossref, `query.bibliographic=...&rows=3`, run here

**Target in the top three:** Convergence properties of the cross-entropy method for discrete
optimization (Costa, Jones, Kroese) · Natural gradient works efficiently in learning (Amari) ·
Towards the geometry of estimation of distribution algorithms based on the exponential family
(Malago) · Theory of Estimation-of-Distribution Algorithms (Krejca, Witt) · Schemata,
distributions and graphical models in evolutionary optimization · From recombination of genes to
the estimation of distributions, binary parameters · Hierarchical BOA solves Ising spin glasses
and MAXSAT · Reinforcement learning by reward-weighted regression · Aggressive driving with model
predictive path integral control · A learning algorithm for Boltzmann machines · Simple
statistical gradient-following algorithms · Simplified runtime analysis of estimation of
distribution algorithms · Upper bounds on the running time of the UMDA on OneMax · Lower bounds on
the run time of the UMDA on OneMax · On the limitations of the UMDA to deception · Likelihood
ratio gradient estimation for stochastic systems · SampleSearch, importance sampling in presence
of determinism · Sequential Monte Carlo samplers.

**Target absent** (all are venues Crossref does not index: JMLR, AISTATS, ICLR, or a technical
report): Natural Evolution Strategies · Information-Geometric Optimization Algorithms · Variance
Reduction Techniques for Gradient Estimates in Reinforcement Learning · Black Box Variational
Inference · Monte Carlo gradient estimation in machine learning · Q-Prop · Population-Based
Incremental Learning (Baluja) · Evolutionary algorithms and the Boltzmann distribution · Model
Predictive Path Integral Control (first phrasing) · Importance sampling exponential change of
measure (Siegmund).

## DBLP, `search/publ/api`, run here

Population-Based Incremental Learning, 79 · Removing the genetics from the standard genetic
algorithm, 1 · cross-entropy method satisfiability, 0 · cross entropy method SAT solver, 0 ·
cross-entropy counting satisfiability assignments, 0 · estimation of distribution algorithm SAT,
HTTP 429 · natural evolution strategy combinatorial satisfiability, HTTP 429 · Baluja
Population-Based Incremental Learning method integrating genetic search, HTTP 429.

## Everything else run here

Semantic Scholar by DOI, four lookups: all resolved the identity and all had the abstract elided
by the publisher. arXiv abstract pages fetched and matched: 1106.4487, 1106.3708, 1511.05176,
2111.05300, 1906.10652, 1401.0118, 1503.01494, 1810.04777, 1806.01710, 1704.00026, 1806.05392,
1511.01437, 1511.06196, 1906.08868, 2007.14634, 1812.11948, 2511.07737, 1604.04153, 1004.4230,
0802.3627, 2504.06757, 2110.13017. Full text read now: `CEconv.pdf` from Dirk Kroese's page,
through `pdftotext`. Publisher pages refused (HTTP 403 or a login redirect): ScienceDirect, the
ACM Digital Library, SpringerLink; `medal-lab.org` has an invalid certificate. Claims about those
works are limited to what the fetched record states. GitHub, through `gh repo view` and `gh api`:
`Evolutionary-Intelligence/pypop`, `VicentePerezSoloviev/EDAspy`, `MatthiasNickles/diff-SAT`,
`omargup/Policy-Gradient-MaxSAT-Solver` (spot-checked by reading `src/utils.py:218` and
`src/train.py`), `jostien/MarchSAT`, `arashardakani/High-Throughput-SAT-Sampler`.

## Zero-hit groups run here, each phrased three ways

- **A cross-entropy method as a SAT solver.** not found (query: Crossref "cross-entropy method for
  the max-cut and satisfiability problems" | Crossref "cross entropy method solving the
  satisfiability problem" | the three DBLP queries above, 0 each). The *counting* application
  exists and is already cited in `gaussian-like-objectives`.
- **An annealed or tempered estimation-of-distribution algorithm for SAT.** not found (query:
  Crossref "annealed estimation of distribution algorithm satisfiability temperature schedule" |
  "tempering estimation of distribution algorithm binary optimization" | "runtime analysis
  estimation of distribution algorithm satisfiability").
- **A closed-form mean-field gradient as the control variate of a sampled gradient, for SAT.** not
  found (query: WebSearch "mean-field gradient as control variate for score function estimator" |
  WebSearch "closed-form mean-field gradient control variate SAT satisfiability sampled gradient" |
  WebSearch "control variate" with "evolution strategies" or "estimation of distribution
  algorithm"). The construction exists for neural networks [gu2016muprop, titsias2022doublecv].

## The four delegated sweeps

Sections (c), (d), (e) and (f) were swept by four subagents under the same rules, then
spot-checked here by re-fetching arXiv:1004.4230, arXiv:0802.3627, arXiv:2504.06757,
arXiv:2110.13017 and the `omargup` and `jostien` repositories. Counts: 25 Crossref and 7 DBLP
queries for the sampling line; 15 Crossref, 17 DBLP, 6 full texts and 11 `gh` queries for the
decimation line; 8 Crossref, 9 DBLP, 19 arXiv pages and about 60 `gh` queries for the neural line;
13 Crossref, 21 DBLP, 14 arXiv pages, 7 full texts and 13 `gh` queries for the GPU line.

**Their zero-hit groups, each phrased at least three ways.**

- **Parallel tempering applied to SAT, in the computer science index.** not found (query: DBLP
  "parallel tempering satisfiability", 0 | DBLP "TemperSAT", 0 | DBLP "replica exchange Monte
  Carlo SAT", 1 unrelated hit). It exists in the physics literature: [mann2010solutionspace].
- **A peer-reviewed hardness-of-sampling theorem for random k-SAT above clustering.** not found
  (three WebSearch phrasings; the only k-SAT-adjacent candidate is an unpublished 2026 bachelor's
  thesis on k-NAE-SAT, not cited).
- **Decimation on empirical marginals from a pool of local-search samples.** not found (query:
  DBLP "WalkSAT guided decimation", 0 | "local search guided decimation satisfiability", 0 |
  "sampling guided decimation SAT", 0 | "sample based decimation satisfiability", 0). The broad
  sweeps that do return ("decimation satisfiability", 2; "decimation SAT", 13) are all
  message-passing.
- **Backbone-guided local search code.** not found (seven `gh search repos` phrasings).
- **A GFlowNet for SAT**, paper or code. not found (three WebSearch phrasings, five `gh` queries).
- **A cross-entropy or evolution-strategy loop on DIMACS, in public code.** not found. Zero-hit
  `gh search repos` queries: cross-entropy method SAT, cross entropy SAT CNF, CEM SAT solver,
  evolutionary algorithm SAT DIMACS, GFlowNet SAT, GFlowNet maxsat, GFlowNet CNF, GFlowNet
  satisfiability, variational autoregressive SAT, autoregressive neural network SAT solver, neural
  annealing SAT, variational neural annealing SAT, autoregressive sampler DIMACS, neural network
  SAT sampler DIMACS, CMA-ES SAT solver, natural evolution strategies SAT, evolution strategies
  satisfiability solver, cross entropy method binary optimization, evolution strategies discrete
  binary optimization, boltzmann machine SAT solver.
- **A GPU WalkSAT paper reporting flips per second.** not found (query: DBLP "GPU WalkSAT", 0 |
  DBLP "GPU4SAT", 0 | DBLP "local search SAT GPU", 3 hits, none a discrete local search; `gh`
  "CUDA WalkSAT", 0 and "WalkSAT GPU", 0). A web snippet attributes 570000 flips per second on a
  GeForce 8800 to a 2008 workshop paper; no primary source was retrievable, so it is not cited.
- **A SAT sampler reporting sample quality against throughput on a GPU.** not found (DBLP "GPU SAT
  sampling", 0; `gh` "uniform sampling SAT witnesses", 0; one WebSearch phrasing). The three GPU
  samplers found report throughput only; the samplers with quality measurements are on the CPU.

`gh search code` was found to be non-functional here: it returned zero for `dimacs2list`, a string
read directly out of a repository in the same session. No code-search result was used.
