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
3. [baselines.md](baselines.md), the two controls, why the search loop is shared byte for
   byte, and the cost asymmetry between a step of F and a step of mu.
4. [open-directions.md](open-directions.md), the ladder of objectives that would separate the
   ingredients, and the author's further directions; none of it is built.
5. [references.md](references.md).

The measurements are in [../benchmark/results.md](../benchmark/results.md); their reading, once
the table is complete, is [../findings.md](../findings.md). The code is described in
[../README.md](../README.md).
