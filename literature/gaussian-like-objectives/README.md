# Gaussian-like objectives for SAT: has anyone ascended P(all clauses satisfied)?

**The question.** Our objective is `F = Phi((mu - m + 1/2) / sigma)`, a normal-tail
surrogate for the probability that the satisfied-clause count reaches `m` under a product
(mean-field) measure on the variables. Has anyone optimised that probability, or any
closed-form approximation of it, as a continuous objective for SAT or CSP?

## Verdict

1. The object has a name we were not using: `P(all clauses satisfied)` under a literal-weighted
   product measure is the **weighted model count** of the formula [chavira2008wmc]. Ascending
   its *exact* value by gradient is established practice, called **semantic loss**, with
   knowledge compilation giving value and gradient [xu2018semanticloss].
2. Ascending it through the **mean and variance** of the satisfied-clause count, with the
   covariance that shared variables induce, was **not found**: no paper and no public
   repository (four GitHub code searches, zero hits each; queries in [queries.md](queries.md)).
3. The sampling version of the original skeleton is the **cross-entropy method**
   [rubinstein1999ce, deboer2005cetutorial], applied to counting satisfying assignments since
   2007 [rubinsteinkroese2007satcount]; its neural form is variational classical annealing
   [wu2019van, hibatallah2021vna]. That branch is forty years old and is not open ground.
4. The continuous SAT line rejects the product objective **in print**, for vanishing gradients
   [kim2026galoissat]. The objection is stated for a sampled Boolean assignment, not for the
   logarithm of a mean-field product, which is the gap we sit in.
5. `Phi` is cosmetic: `F` is strictly monotone in `z = (1/2 - lambda)/sigma`, which the field
   calls the safety-first ratio [roy1952safetyfirst] and the probability of improvement
   [kushner1964pi]. The tilted form is a mean-variance, entropic-risk objective.
6. "Second-moment method" in random k-SAT is a **different probability space** (the random
   formula, not our fixed `p`) and must not be cited as precedent [achlioptas2006twomoments].
7. `mu` satisfies the entry-wise concavity condition under which a low relaxed loss certifies
   the rounded solution; `F` does not [wang2022principledrelaxation].

## The baseline

**Fidelity baseline: exact `log P(all clauses satisfied)` under the same product measure,
computed by weighted model counting with Ganak** (C++, MIT, public, weighted and projected
counting) [ganak_repo], on instances up to a few hundred variables, with `PySDD` as the
knowledge-compilation alternative when a gradient through the circuit is wanted [pysdd_repo].
**Algorithmic baselines: probSAT** [probsat_repo] and the repository's own `mu` ablation, on
the existing scaffolding.

**"Better" is measured by** (a) fidelity: Spearman rank correlation between each surrogate
(`mu`, `logsum`, `pair`, `F`) and the exact `log P` over points sampled along a trajectory, and
the cosine between the surrogate gradient and the exact gradient at those points; (b)
algorithmic: expected time to solution, that is median restart cost divided by restart success
probability, at fixed hardware and seeds.

## Files

[1-naming.md](1-naming.md) · [2-review.md](2-review.md) ·
[3-state-of-the-art.md](3-state-of-the-art.md) · [4-positioning.md](4-positioning.md) ·
[5-plan.md](5-plan.md) · [queries.md](queries.md) · [references.bib](references.bib)
