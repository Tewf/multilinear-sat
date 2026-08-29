# Positioning: the six claims, then what is ours

Each claim gets the field's name for it, who did it, and whether it is true, false or open.

## Claim 1, the null space is combinatorial: TRUE, and elementary

The field has no name for the kernel of the m by m clause covariance; the fact behind it is the
p-biased Fourier expansion [odonnell2014]. For p in the open cube P_p has full support, so
Var_p(c^T I) = 0 exactly when c^T I is constant on the cube, a condition with no p in it. Nobody
needed to prove this and nobody has stated it for clause indicators. It is a one-line
consequence, not a result, and it should be presented that way.

One correction to the test. The brief says the rank should equal m minus the deficiency of
"the m x (1 + n + C(n,2) + C(n,3)) Walsh-coefficient matrix of the I_j". The constant column
must be dropped: c^T I constant, not zero, is the condition, so ker Sigma is the null space of
the m by (n + C(n,2) + C(n,3)) matrix of the **non-constant** Walsh coefficients. With the
constant column kept, the test computes a strictly smaller space. The exact polynomial-time
Walsh decomposition of a k-SAT instance already exists in the literature
[suttonwhitleyhowe2009].

## Claim 2, the dependencies are resolution-shaped: identity TRUE, consequence FALSE

The identity I(x or y or z) + I(x or y or not z) = I(x or y) is resolution on z whose resolvent
subsumes both antecedents, which subsumption and bounded variable elimination already exploit
[een2005satelite, biere2021preprocessing]. So this half of ker Sigma buys nothing a preprocessor
does not already remove, and the corollary that all eight sign patterns on a triple sum to 1
describes a formula any solver refutes as soon as it branches on those three variables.

The brief's expectation is wrong on the facts. It says: "expect ker Sigma = the merge space, and
0 on SATLIB instances (which have no such pairs by construction, to be checked)". The uniform
random 3-SAT generator draws the variable triple and the three signs independently and rejects
only duplicate clauses, so a pair on the same triple differing in one sign is not excluded. Its
expected count under the generator, before the satisfiability filter, is C(m,2) times 1/C(n,3)
times 3/8, which is 0.45 on uf50-218 and 0.083 on uf250-1065: order one on the smallest family,
and Theta(alpha^2 / n), so it vanishes as n grows. Clause merging is therefore a small-instance artefact and cannot be a reduction mechanism
at scale. SATLIB uf sets are additionally filtered to be satisfiable, and filtering is exactly
the bias [suttonwhitleyhowe2009] warns changes the correlation structure of a benchmark set.

## Claim 3, a non-negative null vector is an UNSAT certificate: TRUE, and known empty

The field's names are a Nullstellensatz refutation with constant multipliers
[beame1996nullstellensatz] and a level-0 Sherali-Adams, that is a plain linear programming,
certificate [sheraliadams1990]. It provably does not exist for random CNF: polynomial calculus
degree is Omega(n) [bensasson2010pc] and is at most Nullstellensatz degree. The brief's own
instruction, "State it as such", is the right call and the literature confirms it. The only
family we can name where such a c exists is a variable triple carrying all eight clauses.

## Claim 4, near-null directions and leading modes: OPEN, but the uf50 answer is known

Near-null directions have no name in the field. Leading modes do, on the graph side: community
structure and modularity [ansotegui2012community, ansotegui2019community]. The brief calls the
alignment "a measurable question, not a claim", which is right, but plans to measure it on uf50,
where the answer is already published: [ansotegui2019community] states that "random SAT
instances are closer to the classical Erdos-Renyi random graph model, where no structure can be
observed". The experiment has to run on application instances. Two further cautions from the
same line: good community structure does not make an instance easy [mull2016hardness], and
structural parameters "only weakly correlate with CDCL solving time" [zulkoski2017parameters].
The one genuine structural link worth stating is that at p = 0, on pairs sharing exactly one
variable, the off-diagonal of Sigma is 1/64 times a signed adjacency matrix of the
clause-sharing graph, plus one for a same-sign share and minus one for an opposite-sign share
(the entries are in `method/regimes.md` already). That is the same species of signed matrix the
refutation line takes eigenvalues of, except that theirs is indexed by variables and is n by n
[feige2007easily, Definition 5.1].

## Claim 5, the literal side is the Jacobian: the algebra is right, the identification is FALSE

The brief says: "Two columns collinear at every p iff the two variables occur in the same
clauses with the same sign pattern (equivalent-literal structure)". The condition is correct and
the parenthesis is not. Collinear columns of J = dU/dp require the two variables to occur in
exactly the same clauses, with a constant relative sign in each, which is syntactic duplication,
not logical equivalence. Two logically equivalent literals generally have non-collinear columns,
and duplication is far rarer than equivalence. The brief then says: "The exact case is standard
preprocessing (equivalent literal substitution) and needs 2-clauses, so on pure 3-CNF only the
soft version has content". Wrong twice. Equivalent-literal substitution is the strongly
connected components of the *binary* implication graph, so it does need binary clauses
[biere2021preprocessing, section 9.3.2], but it is not what the Jacobian condition detects; and
the technique that does find non-binary equivalences, gate extraction plus congruence closure
[biere2024congruence], works on longer clauses and is already in CaDiCaL. Separately, J is the
derivative of the mean map, so the whole claim sits outside Sigma.

## Claim 6, where PCA has no content: TRUE, and the literature strengthens it

Sigma(p) is known exactly and is sparse by construction, which makes it a covariance graph model
[coxwermuth1993, chaudhuri2007zeros] and not a low-rank-plus-diagonal one
[tippingbishop1999ppca]; the two are different, non-nested structures. Randomised low-rank
methods [halko2011randomness] presuppose a matrix that is expensive to touch or only sampled,
and neither holds. The scalar the surrogate needs, 1^T Sigma 1, is a sum over sharing pairs that
`moments.py` already computes. "PCA" is in any case the wrong word for the spectral
decomposition of a matrix that is not estimated from samples.

## Not done in the world, against not done here

**Not found anywhere**, on nine queries across arXiv, Crossref and DBLP and four `gh search
repos` phrasings: the spectrum, kernel or principal components of a covariance of clause
indicators under a product measure, for any purpose. This is "not found", not "does not exist".

**Done in the world, not here**: the exact polynomial-time Walsh correlation structure of a
k-SAT instance [suttonwhitleyhowe2009]; modularity of the clause graph
[ansotegui2012community]; the whole standard preprocessing stack [biere2021preprocessing];
loop-corrected linear response [mooijkappen2007loopcorrections]. Where our object sits: Sigma(p)
is the zeroth-order Plefka susceptibility [plefka1982] of the clause observables, the same
quantity belief propagation's linear response corrects [wellingteh2004linearresponse]. Our use
of it so far is one scalar.
