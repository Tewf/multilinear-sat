# The map, by line of work

Every entry was fetched during this review; service and identifier in
[references.bib](../references.bib). "(a)" the abstract was read now, "(f)" the full text. Numbers
and barriers are in [3-state-of-the-art.md](../3-state-of-the-art.md), so these files say only what
each work does and does not do.

**Surveys first.** [krejca2019edatheory] (a) is the runtime theory of univariate
estimation-of-distribution algorithms; its benchmarks are OneMax and LeadingOnes and it names no
combinatorial problem. [mohamed2020mcgrad] (a) is the survey of Monte Carlo gradient estimation.
Between them they cover (a) and (b); neither mentions satisfiability.

Read in order:

1. [update-rule-and-variance.md](update-rule-and-variance.md): (a) the identity as an update
   rule, (b) variance reduction and the control variate the note wants.
2. [annealed-sampling-and-decimation.md](annealed-sampling-and-decimation.md): (c) annealed
   and population sampling for the tilted measure, (d) decimation guided by samples rather
   than messages.
3. [neural-annealing-and-gpu.md](neural-annealing-and-gpu.md): (e) neural annealing,
   autoregressive samplers and policy gradients for SAT, (f) whether GPU parallelism
   compensates for slow mixing.
