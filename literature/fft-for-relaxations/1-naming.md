# Encadrer le sujet: what the field calls this

## The problem in one sentence

Given a CNF formula, we want to know what the Fourier (Walsh-Hadamard) spectrum of its
multilinear relaxation says about the relaxation: how sparse it is, how cheaply it is
computed, what statistics of the landscape it yields, and whether any of that predicts
where batched gradient ascent on the cube lands.

## The names, by community

**Analysis of Boolean functions.** Fourier expansion, Fourier coefficient, Fourier weight
at degree d, influence, total influence, noise stability, noise sensitivity,
hypercontractivity, junta, low-degree approximation [odonnell2014abf]. A clause indicator
is a k-junta and the field would say so.

**Evolutionary computation, from 1989 on.** Walsh transform, Walsh coefficient, Walsh
polynomial, order-k interaction, epistasis, nonlinearity, schema average, hyperplane
average [rana1998walsh, heckendorn1997nk]. The same object, a different word, a different decade,
and almost none of it on arXiv. Later: embedded landscape [heckendorn2002embedded],
k-bounded pseudo-Boolean function, elementary landscape and elementary landscape
decomposition (ELD) [chicano2011eld, whitley2008elementary], autocorrelation function,
correlation length, ruggedness [sutton2009correlation, stadler1996landscapes], variable
interaction graph (VIG), linkage, gray-box optimisation [przewozniczek2025wdvig],
local optima network (LON), partition crossover (PX) [chen2018pxsat].

**Approximation algorithms and hardness.** Multilinear extension, integrality gap,
semidefinite programming relaxation [karloff1997sdp], invariance principle and Majority Is
Stablest [mossel2010noise], the unique games reduction to every CSP [raghavendra2008every],
sharp threshold [friedgut1999sharp], low-degree polynomial algorithm and low-degree
hardness [bresler2022lowdegree, gamarnik2020lowdegree].

**Transform algorithmics.** Fast Walsh-Hadamard transform (FWHT), Yates's algorithm,
Moebius transform and zeta transform on the subset lattice, subset convolution
[bjorklund2007subset], sparse Walsh-Hadamard transform [cheraghchi2016sparse,
li2015spright], elementary symmetric polynomial (ESP) evaluation by FFT
[kyrillidis2020fouriersat, cen2025fastfouriersat].

## Acronyms worth searching by

FWHT, ELD, VIG, LON, PX, ESP, OGP (overlap gap property), UGC (unique games conjecture),
CLS (continuous local search), SLS, EDA (estimation of distribution algorithm).

## Why our name differs

Our notes call the objects "the moments of the satisfied-clause count", "the pair
expansion", "the Gaussian surrogate". The field, for the same computations on the same
function class, says "polynomial-time summary statistics of an embedded landscape"
[heckendorn1999summary, heckendorn2002embedded] and "the exact correlation structure of
k-satisfiability landscapes" [sutton2009correlation]. Our word for the method is the name
of the method; theirs is the name of the object. Two consequences.

First, `mu` is the MAX-SAT evaluation function's multilinear extension, so its Walsh
spectrum is the one Rana, Heckendorn and Whitley wrote down in closed form in 1998
[rana1998walsh]; a hyperplane (schema) average in their sense is exactly `mu(p)` at
p in {-1, 0, +1}^n, and our continuous p interpolates it.

Second, searching arXiv for this line returns nothing. `all:"Walsh" AND
all:"satisfiability"` gives 89 hits, none of them the 1998 paper; `abs:"Walsh" AND
abs:"MAX-SAT"` gives 0, and DBLP's `Walsh MAXSAT` gives 0 because the title says "SAT".
The line lives in AAAI, GECCO, FOGA, EvoCOP and Springer LNCS. See `queries.md`.
