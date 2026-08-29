# Positioning

## Not done in the world

No paper and no repository was found that **ascends a moment-based approximation of
`P(all constraints satisfied)`** for SAT or CSP. Specifically:

- The twenty-one works citing FourierSAT were listed from Semantic Scholar and every
  SAT-solving one among them was checked by title, and where the title was ambiguous by
  abstract: all of them keep the **sum** of clause polynomials or a variant of it. None
  replaces it by a probability-of-satisfaction objective.
- Four GitHub code searches returned zero repositories ([queries.md](queries.md)). Following
  the rule of this house, that is **not found**, not "does not exist".
- The closest published thing is a *dynamics* correction, not an objective correction
  [foos2025beyondmeanfield], and a *free energy* correction for k-SAT annealing from 2001
  [jonsson2001informationcsp], which is the real ancestor and which our notes do not cite.

## Done in the world, and not by us

- **The exact objective is descended by gradient, routinely.** Semantic loss
  [xu2018semanticloss] is the negative logarithm of exactly our target under exactly our
  measure, computed exactly. We approximate what other people compute; we should say so, and
  we should measure the gap.
- **The sampled skeleton is the cross-entropy method** [rubinstein1999ce], including for
  counting satisfying assignments [rubinsteinkroese2007satcount], and its neural form is
  variational classical annealing [hibatallah2021vna]. Both have public implementations.
- **The pair closure has a published name and a better relative**: the cluster expansion of the
  polymer gas [bissacot2011clusterlll], and the Bethe functional with a convergent minimiser
  [yuille2002cccp].
- **The rejection of the product objective is in print** [kim2026galoissat]. Its stated reason
  is that one unsatisfied clause zeroes the product. That argument holds for a *sampled Boolean
  assignment*, where each clause value is in `{0, 1}`. It does not hold for the mean-field
  product, whose factors are strictly inside `(0, 1)` and whose logarithm is a sum. Our
  `log Phi` trick and the `logsum` objective are the answer to a published objection, which is
  a better position than an unexamined idea.

## Corrections to our notes, quoted

1. `method/open-directions.md` says: "`pair` is the pair (Kirkwood, or Bethe) approximation of
   `P(all satisfied)`". **Wrong as written.** The Kirkwood pair closure over clause pairs and
   the Bethe free energy over variable and clause beliefs are different functionals;
   `pair-expansion.md` says so two files away ("The exact object on a tree-shaped factor graph
   is the Bethe free energy over variable and clause beliefs ... a different functional"). The
   published name of the pair closure is a cluster expansion truncated at pairs
   [bissacot2011clusterlll]; Bethe belongs to [yuille2002cccp, bapst2016bethe].

2. `method/open-directions.md` says: "Comparing its `P[N = m]` ... with the Gaussian `F` and
   with the truth by enumeration on small instances would put a number on what the normal
   approximation costs." **Too weak.** Enumeration caps at about twenty-five variables. The
   truth is a weighted model count [chavira2008wmc] and a public counter computes it on
   uf50-218 and probably uf100-430 [ganak_repo], so the comparison can be made where the
   benchmark actually runs.

3. `method/objective.md` says: "`F` is not multilinear ... so the theorem that a multilinear
   polynomial attains its maximum at a vertex does not apply." **Incomplete.** A second
   guarantee is lost with it: if the relaxed objective is entry-wise concave, a low loss
   certifies the rounded solution [wang2022principledrelaxation]. `mu` is entry-wise affine and
   satisfies that condition; `F` satisfies neither it nor the vertex theorem. Every claim for
   `F` is therefore empirical by construction, and the benchmark is not a convenience, it is
   the only available argument.

4. `method/origin.md` says: "Two salvage directions were named: the log-sum objective
   `sum_j log f_j(p)`, and correlated parameterisations where sampling earns its place."
   **The second is not a direction, it is a field.** Correlated parameterisations sampled and
   updated by gradient are the cross-entropy method [rubinstein1999ce], estimation of
   distribution algorithms, probability collectives [wolpert2006probabilitycollectives] and
   variational neural annealing [hibatallah2021vna, vna_repo]. Any work there starts from their
   baselines, not from ours.

5. `method/references.md` lists Plefka and Yedidia, Freeman and Weiss but never names the
   objective's own family. **Add** [chavira2008wmc] and [xu2018semanticloss]: the target is a
   weighted model count and the loss already has a name.

6. `brief.md`, question 1, lists "second-moment method (Achlioptas, Moore, Peres)" among the
   names for our method. **They are a different probability space** ([1-naming.md](1-naming.md)),
   and citing them as precedent for the objective would be an error.

## Where our objective sits

One sentence: `F` is a **second-order mean-field surrogate for a weighted model count**,
ascended by gradient, on a line whose published members all ascend the first-order surrogate
instead, and whose only exact member compiles the count instead of approximating it.
