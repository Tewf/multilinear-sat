# Method note: the Gaussian-surrogate relaxation

The branch asks one question: does the *variance* of the satisfied-clause count help gradient
ascent find a satisfying assignment, or is its *mean* enough? Everything here is written so
that the question can be answered by a table, and nothing here claims what the table does not
show.

Reading order:

1. [origin.md](origin.md), where the objective came from: Las Vegas algorithms, the random
   walks, FourierSAT, and a Bernoulli reformulation whose surviving piece is a generating
   function in a counting variable.
2. [objective.md](objective.md), the objective as built: the one- and two-clause unsatisfied
   probabilities, mean and variance of the count, the Gaussian surrogate, and what the
   function says about itself before any benchmark.
3. [regimes.md](regimes.md), which law approximates P(N = 0) where: large deviation, Poisson,
   central limit, with the indicator of each, and what the Gaussian was implicitly doing.
4. [tilted-objective.md](tilted-objective.md), the cumulant-generating function behind the three
   laws, and the mean-variance objective the Gaussian implicitly ascends, with its beta.
5. [pair-expansion.md](pair-expansion.md), the cluster expansion of log P(N = 0), the pair
   closure, where it is exact and where it is not, its gradient and its cost.
6. [baselines.md](baselines.md), the two controls, why the search loop is shared byte for
   byte, and the cost asymmetry between a step of F and a step of mu.
7. [open-directions.md](open-directions.md), the ladder of objectives that would separate the
   ingredients, and the author's further directions; none of it is built.
8. [anytime-las-vegas.md](anytime-las-vegas.md), the Las Vegas hybrid with an UNSAT posterior: seed,
   polish, restarts, a rigorous half and what can and cannot be claimed.
9. [sampling-gradient-loop.md](sampling-gradient-loop.md), the tilted objective whose gradient is
   the tilted mean minus p, estimated by annealed samples and corrected by a control variate;
   built as `--obj tilted`.
10. [not-built.md](not-built.md), what the loop leaves out (decimation) and what it builds in two
    forms, one of them labelled biased.
11. [references.md](references.md).

The measurements are in [../benchmark/results.md](../benchmark/results.md); their reading, once
the table is complete, is [../findings.md](../findings.md). The code is described in
[../README.md](../README.md).
