# Every query tried, 2026-08-29

Services: arXiv API (A), Crossref `query.bibliographic` (C), DBLP `search/publ/api` (D,
reachable only through the web fetcher; direct requests are reset here), Semantic Scholar
graph API (S), GitHub CLI (G), web search (W). Counts are the service's own total.

## arXiv, search queries

| # | query | hits |
|---|---|---|
| A1 to A6 | `all:"FourierSAT"` 1 · `all:"FastFourierSAT"` 2 · `ti:"continuous local search" AND abs:SAT` 2 · `all:"NLocalSAT"` 1 · `all:"Accelerated Fourier SAT"` 1 · `ti:"A Study of Parallel Continuous Local Search"` 1 | |
| A7 | `all:"matrix multiplication" AND all:"SAT solver"` | 5 |
| A8 | `all:"flip graph" AND all:"matrix multiplication"` | 14 |
| A9 | `all:"CNF-XOR"` | 4 |
| A10 | `all:"XORSAT" AND all:"local search"` | **0, not found** |
| A11 | `all:"Being glassy without being hard to solve"` | **0, not found** (it is a Science perspective; found at C8) |
| A12 | `abs:"WalkSAT" AND abs:"XOR"` | 4 (the rephrasing of A10 that worked) |
| A13 | `all:"3-XORSAT" AND all:"algorithm"` | 8 |
| A14 | `ti:"hiding solutions" AND all:"satisfiability"` | 3 |
| A15 to A19 | `all:"Gauss-Jordan elimination" AND all:"SAT solver"` 2 · `all:"CryptoMiniSat"` 6 · `all:"Luby" AND all:"restart" AND all:"Las Vegas"` 1 · `ti:"restart" AND abs:"Las Vegas algorithm"` 1 · `all:"Ercsey-Ravasz"` 17 | |
| A20 | `abs:"continuous-time dynamical system" AND abs:"satisfiability"` | fetch failed, HTTP 429; replaced by A21 |
| A21 to A24 | `ti:"Optimization hardness as transient chaos"` 1 · `all:"TurboSAT"` 1 · `all:"Interactive Particle Systems on Hypergraphs"` 1 · `all:"GaloisSAT"` 1 | |
| A25 | `all:"FourierSAT" AND all:"matrix multiplication"` | **0, not found** |
| A26 | `abs:"Brent equations"` | 6 |
| A27 | `abs:"continuous relaxation" AND abs:"initial assignment" AND abs:"local search"` | **0, not found** |
| A28 | `abs:"warm start" AND abs:"local search" AND abs:"SAT solver"` | 1, irrelevant (graph colouring) |
| A29 | `abs:"tensor rank" AND abs:"continuous optimization" AND abs:"GF(2)"` | **0, not found** |
| A30 | `all:"multilinear extension" AND all:"SAT solver"` | **0, not found** |
| A31 | `abs:"rounding" AND abs:"local search" AND abs:"satisfiability"` | 5, none on SAT seeding |
| A32 | `abs:"initialization" AND abs:"stochastic local search" AND abs:"SAT"` | 2 |
| A33 | `all:"solution prediction" AND all:"local search" AND all:"SAT"` | 2 |
| A34 | `all:"parity learning" AND all:"SAT solver"` | 1, irrelevant |
| A35 | `abs:"GPU" AND abs:"stochastic local search" AND abs:"SAT"` | **0, not found** |
| A36 | `abs:"analog" AND ti:"SAT solver"` | 5 |

A27, A31, A32 and A33 are the three rephrasings behind the "no continuous relaxation has
been used as an SLS seed" claim in [4-positioning.md](4-positioning.md).

**arXiv by identifier** (`id_list`, all returned): 1909.12353, 1208.0526, 2511.07737,
2606.06641, 2606.06656, 2506.00674, 2603.28796, 2212.01175, 2502.04514, 2510.19787,
2312.16960, 2603.02398, 2402.01011, 2607.29291, 2607.15834, 2210.13159, cond-mat/0408190.

## Crossref, `query.bibliographic` (each returned the work as its first hit unless marked)

C1 Luby Sinclair Zuckerman optimal speedup Las Vegas · C2 Gomes Selman Kautz Crato
heavy-tailed phenomena · C3 Schoning probabilistic algorithm k-SAT · C4 Paturi Pudlak Saks
Zane improved exponential-time k-SAT · C5 Soos Nohl Castelluccia extending SAT solvers to
cryptographic problems · C6 Soos Meel BIRD · C7 Haanpaa Jarvisalo Kaski Niemela hard
satisfiable clause sets · C8 Ricci-Tersenghi being glassy · C9 Heule Kauers Seidl local
search fast matrix multiplication · C10 Kauers Moosbauer flip graphs · C11 Fawzi
discovering faster matrix multiplication with reinforcement learning · C12 Jia Moore Selman
from spin glasses · C13 Nawrocki Liu Frohlich XOR local search Brent equations · C14 Cai
Zhang deep cooperation CDCL local search · C15 Braunstein Mezard Zecchina survey
propagation · C16 Chavas Furtlehner Mezard Zecchina SP decimation distributed · C17 Balint
Schoning probSAT · C18 Molnar Varga Toroczkai continuous-time MaxSAT ·
**C19 Zhang Rangan Looks backbone guided local search: not found, found at D2** ·
**C20 Crawford Kearns Schapire minimal disagreement parity: not found, and D4 returned
HTTP 429; not cited anywhere.**

## DBLP, Semantic Scholar, GitHub, web

D1 "Noise Strategies for Improving Local Search" 1 · D2 "Backbone Guided Local Search for
Maximum Satisfiability" 1 · D3 "CaDiCaL Kissat Plingeling Treengeling YalSAT entering the
SAT Competition" **0** · D4, D5, D6 rate-limited or connection reset.
S1 citations of arXiv:1912.01032, 21 · S2 citations of arXiv:2308.15020, 10; these two are
the forward-citation chase, and they are where AFSAT, TurboSAT, GaloisSAT, FourierCSP and
the XNF paper were found.
G `gh repo view` on the twelve repositories in `references.bib`; `gh api` on kissat
`src/walk.c` and `src/rephase.c`; `gh search repos`: "AFSAT continuous local search"
**0**, "FourierCSP" **0**, "TurboSAT gradient SAT" **0**, "NLocalSAT" 1, "GaloisSAT" 1.
W: Heule Kauers Seidl solver used · Ricci-Tersenghi being glassy · XOR Local Search for
Boolean Brent Equations PDF · Thinking Out of the Box · continuous relaxation initialising
WalkSAT · Kauers Moosbauer flip graph records · Biere SAT Competition 2017 proceedings.
Full texts fetched and read: arXiv 1903.11391 (abstract and HTML), 1912.01032v2 PDF,
2308.15020v1 PDF, `cs.cmu.edu/~mheule/publications/xnfSAT.pdf`, `fmv.jku.at` Biere 2017
PDF, the JSAT `10.3233/SAT190015` record. **Nature Communications `s41467-026-69465-2` on
in-memory XOR-CNF solving: behind an authorisation redirect, not obtained, not cited.**
