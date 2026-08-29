# The problem, and what the field calls it

## In one sentence

Given the vector of clause-unsatisfied indicators I = (I_1, ..., I_m) of a CNF formula under
the product measure P_p on {-1, 1}^n, decide what the covariance matrix Sigma(p) of I says
about the formula, and whether its kernel, its small eigenvalues or its leading eigenvectors
justify removing clauses, tying literals, splitting the instance or warm-starting a search.

## What the field calls each piece

**The matrix itself.** Sigma(p) is the Gram matrix of the centred p-biased Fourier
expansions of the clause polynomials. In analysis of Boolean functions the covariance under a
product measure is the inner product of the non-constant parts of the p-biased expansion, and
the block decomposition by degree is the Efron-Stein (or Hoeffding, or ANOVA) decomposition
[odonnell2014]. Nobody in the SAT literature names the m by m clause-clause matrix; the named
object is always the Walsh (Fourier) coefficient matrix of the evaluation function, m by
(n + C(n,2) + C(n,3)) for 3-CNF, which is what Sutton, Whitley and Howe compute exactly in
polynomial time [suttonwhitleyhowe2009]. Sigma is that matrix times its transpose, reweighted
by p.

**Its kernel.** A vector c with c^T I constant is a linear dependence among the clause
polynomials modulo constants. In proof complexity the same object with a constant right hand
side is a Nullstellensatz derivation whose multipliers are constants, so degree 0 in the
multiplier and degree k in the axiom [beame1996nullstellensatz]; with c non-negative it is a
level-0 Sherali-Adams, that is a plain linear-programming, certificate [sheraliadams1990]. In
commutative algebra the same set is the module of linear syzygies of the clause generators.

**Its small eigenvalues, read as redundancy.** SAT calls a clause removable when the formula
without it is equisatisfiable, and the tests are logical, not linear: subsumption,
self-subsuming resolution and bounded variable elimination [een2005satelite], blocked clause
elimination [jarvisalo2010bce], covered and asymmetric variants [heule2010clauseelim,
heule2015clauseelim], vivification [piette2008vivify], the whole family surveyed in chapter 9
of the Handbook of Satisfiability [biere2021preprocessing]. The one identity the maestro's
brief calls "resolution-shaped", I(x or y or z) + I(x or y or not z) = I(x or y), is exactly
resolution on z whose resolvent subsumes both antecedents, so every preprocessor already
removes it.

**Its leading eigenvectors, read as groups.** The graph-side name is community structure or
modularity of the variable-clause, variable-incidence or clause-clause graph
[ansotegui2012community, ansotegui2019community].

**Its role in physics.** The covariance of local observables under a factorised measure is the
zeroth order of the Plefka expansion of the susceptibility [plefka1982]; the systematic
correction is linear response around belief propagation [wellingteh2004linearresponse,
mooijkappen2007loopcorrections].

**Its shape as a statistical model.** Sigma has a known zero pattern (clauses sharing no
variable are uncorrelated), which is a covariance graph model, or bidirected graph model
[coxwermuth1993, chaudhuri2007zeros], the dual of a Gaussian Markov random field, where the
zeros sit in the precision matrix instead [rueheld2005].

## Why our name differs, and where it misleads

"Simplify the multivariate Gaussian by PCA" names a method, not the object. Three consequences.
Principal component analysis is an estimator of a covariance from samples; here Sigma(p) is
known in closed form and exactly, so the word to use is spectral decomposition of a known Gram
matrix, and the sampling literature (Nystrom, randomised range finders [halko2011randomness])
buys nothing. Second, a low-rank plus diagonal model [tippingbishop1999ppca] is a different and
non-nested structure from the sparse covariance we actually have. Third, "collinearity" in the
Jacobian is about the mean map U(p), not about Sigma at all, and belongs to a different
section of the field: gate extraction and equivalent-literal substitution
[biere2021preprocessing, biere2024congruence].
