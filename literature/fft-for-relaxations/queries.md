# Every query tried, 2026-08-29

Covers question 3 of `brief.md` and the smaller question answered in
`../tanh-parametrisation.md`. Counts are what the service returned that day.

## arXiv API (`export.arxiv.org/api/query`)

Field prefixes as written. The API rate-limits with HTTP 429; every query below succeeded
after backoff. A multi-term `all:"a" AND all:"b"` is a conjunction of exact phrases and is
strict, which explains several of the zeros.

| query | hits |
|---|---|
| `all:"Walsh" AND all:"satisfiability"` | 89 |
| `all:"Fourier" AND all:"random k-SAT"` | 0 |
| `all:"low degree polynomial" AND all:"random k-SAT"` | 1 |
| `all:"noise stability" AND all:"satisfiability"` | 13 |
| `all:"Fourier spectrum" AND all:"CNF"` | 0 |
| `all:"fast Walsh-Hadamard transform" AND all:"optimization"` | 11 |
| `all:"sparse Walsh-Hadamard transform"` | 2 |
| `all:"Fourier sparse set functions"` | 2 |
| `all:"subset convolution" AND all:"Moebius transform"` | 1 |
| `all:"integrality gap" AND all:"Fourier analysis"` | 1 |
| `all:"fitness landscape" AND all:"Walsh"` | 3 |
| `all:"elementary landscape"` | 2 |
| `all:"autocorrelation" AND all:"MAX-SAT"` | 1 |
| `all:"gray-box optimization"` | 16 |
| `all:"basin of attraction" AND all:"satisfiability"` | 23 |
| `all:"influence" AND all:"clause" AND all:"Boolean function"` | 0 |
| `abs:"k-SAT" AND abs:"Fourier"` | 0 |
| `abs:"Walsh" AND abs:"MAX-SAT"` | 0 |
| `all:"Walsh coefficients" AND all:"local search"` | 0 |
| `all:"multilinear extension" AND all:"submodular maximization"` | 19 |
| `all:"overlap gap property" AND all:"low-degree"` | 10 |
| `all:"integrality gap" AND all:"MAX-3SAT"` | 2 |
| `abs:"FourierSAT"` | 1 |
| `all:"Walsh transform" AND all:"epistasis"` | 0 |
| `all:"correlation length" AND all:"fitness landscape"` | 3 |
| `all:"mirror descent" AND all:"binary optimization"` | 0 |
| `all:"exponentiated gradient" AND all:"simplex"` | 7 |
| `all:"natural gradient" AND all:"Bernoulli"` | 5 |
| `all:"information geometric optimization"` | 16 |
| `all:"simulated bifurcation" AND all:"Ising"` | 29 |
| `all:"coherent Ising machine"` | 121 |
| `all:"probabilistic bit" AND all:"Ising machine"` | 15 |
| `all:"continuous relaxation" AND all:"SAT solver" AND all:"gradient"` | 0 |
| `all:"analog" AND all:"SAT" AND all:"dynamical system"` | 5 |
| `abs:"AFSAT" OR ti:"Accelerated Fourier SAT"` | 1 |
| `all:"Walsh" AND all:"gradient descent" AND all:"pseudo-Boolean"` | 0 |
| `all:"landscape analysis" AND all:"continuous relaxation" AND all:"SAT"` | 0 |
| `all:"Fourier" AND all:"basin of attraction" AND all:"combinatorial"` | 0 |
| `all:"mirror descent" AND all:"nonconvex" AND all:"basin of attraction"` | 0 |
| `all:"mirror descent" AND all:"escape" AND all:"saddle"` | 0 |
| `all:"tanh" AND all:"reparameterization" AND all:"combinatorial optimization"` | 0 |
| `all:"Hopfield" AND all:"sigmoid gain" AND all:"annealing"` | 0 |
| `all:"probabilistic method" AND all:"gradient" AND all:"MaxSAT" AND all:"relaxation"` | 0 |
| `all:"Gumbel" AND all:"Bernoulli" AND all:"combinatorial optimization"` | 0 |
| `ti:"Reparameterizing Mirror Descent as Gradient Descent"` | 1 |
| `all:"algorithmic equivalence" AND all:"mirror descent"` | 2 |

## DBLP (`dblp.org/search/publ/api`)

| query | hits |
|---|---|
| `tractable Walsh analysis of SAT` | 1 |
| `polynomial time computation exact correlation structure k-satisfiability landscapes` | 1 |
| `elementary landscapes` | 16 |
| `Heckendorn Walsh` | 3 |
| `partition crossover` | 31 |
| `gray-box optimization Walsh decomposition` | 0 |
| `efficient hill climber pseudo-Boolean` | 3 |
| `Walsh MAXSAT` | 0 (the 1998 title says "SAT", not "MAXSAT") |
| `Chicano Whitley partition crossover` | service error, not retried; covered by `partition crossover` |
| `gray-box optimization Walsh` | service error, rephrased above |
| `efficient hill climber pseudo-Boolean Walsh` | timed out, rephrased above |
| `landscape autocorrelation SAT` | service error; covered by the Crossref and arXiv rows |

## Crossref (`api.crossref.org/works?query.bibliographic=`)

Crossref's `total-results` is a loose relevance count and is not reported. Recorded instead
is whether the intended work appeared in the top rows. Found at rank 1 unless noted:
Sutton/Whitley/Howe 2009 correlation structure; O'Donnell 2014 (chapter DOI);
Karloff and Zwick 1997; Ercsey-Ravasz and Toroczkai 2011; Kivinen and Warmuth 1997;
Beck and Teboulle 2003; Amari 1998 (rank 2, the Neural Computation record);
Goto, Tatsumura, Dixon 2019; Hopfield and Tank 1985; Bjoerklund et al. 2007;
Sutton/Whitley/Howe 2012 moments; Chicano/Whitley/Alba 2011; Chen et al. 2018 tunneling;
Heckendorn 2002 embedded landscapes; Friedgut 1999; Mossel/O'Donnell/Oleszkiewicz 2010;
Bernasconi and Codenotti 1999; Molnar et al. 2018; Inagaki et al. 2016 (rank 3);
Molnar/Toroczkai/Ercsey-Ravasz 2012; Unanue/Merino/Lozano 2021; Sutton/Howe/Whitley 2009
theoretical analysis; Whitley/Ochoa/Floyd/Chicano 2024; Raghavendra 2008; Stadler 1996.

Not found in Crossref: `Rana Heckendorn Whitley tractable Walsh analysis SAT genetic
algorithms` (AAAI 1998 is not deposited; found on DBLP and fetched from AAAI);
`Polynomial time summary statistics for a generalization of MAXSAT Heckendorn Rana Whitley`
(GECCO 1999, not deposited; PDF fetched from the authors' site);
`Learning Fourier sparse set functions Amrollahi Kapralov Krause`;
`A Scalable Walsh-Hadamard Regularizer to Overcome the Low-degree Spectral Bias`.

## Semantic Scholar

Twenty identifier lookups (`/graph/v1/paper/{DOI|arXiv|DBLP}`) for abstracts; the service
returns 429 without a key, so each was retried with backoff. No abstract on record for
`DOI:10.1016/j.tcs.2011.02.006`, `10.1007/978-3-642-03751-1_4`,
`10.1007/978-3-031-57712-3_8`, `10.1162/106365602760972758` (obtained from PubMed instead),
`10.1162/evco_a_00039`, `10.1109/sfcs.1997.646129`, `10.1007/BF00339943`,
`10.1006/inco.1996.2612`, `10.1016/S0167-6377(02)00231-6`, `10.1162/089976698300017746`,
`10.1145/1389095.1389208`, `10.1145/1569901.1569954`. Title search
`A Tractable Walsh Analysis of SAT and its Implications for Genetic Algorithms` returned 429
and was not retried; the paper was verified through DBLP and its full text.
`DBLP:conf/aaai/RanaHW98` and `DBLP:conf/icga/HeckendornW97`: not found.

## GitHub (`gh search repos`, `gh repo view`)

| query | hits |
|---|---|
| `AFSAT Fourier SAT` | 0 |
| `FourierCSP` | 0 |
| `Walsh analysis SAT landscape` | 0 |
| `fitness landscape analysis MAXSAT Walsh` | 0 |
| `gray box optimization MAXSAT` | 0 |
| `FastFourierSAT` | 1 (`seeder-research/FastFourierSAT`) |
| `pflacco` | 2 (continuous landscape analysis, not SAT) |
| `local optima network` | 6, none SAT-specific |

`gh repo view vardigroup/FourierSAT`: Python, MIT, last push 2024-09-18.
`gh repo view seeder-research/FastFourierSAT`: Python, CC0-1.0, last push 2025-04-14.
**No public code was found for any exact Walsh or landscape analysis of SAT instances.**
Not found, not "does not exist".

## Direct fetches

`cdn.aaai.org/AAAI/1998/AAAI98-206.pdf` (full text, read); `cs.colostate.edu/~genitor/Pubs.html`
(publication list); `cs.colostate.edu/~genitor/1999/maxsat99.pdf` (HTTP 200, 224 KB, font
encoding broken); `arxiv.org/abs/2510.04480` and `arxiv.org/html/2510.04480v1` and `v2`;
PubMed efetch for PMID 12450455. Three web searches on the Walsh-spectrum-to-basin question
and on mirror descent versus projected gradient basins, all of which returned only
tangential results.
