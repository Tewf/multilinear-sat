# Positionnement

## Where our objective sits in the spectrum

`mu` is the MAX-SAT evaluation function's multilinear extension, so its Walsh spectrum is
[rana1998walsh]'s Theorem 1 exactly: at most 7m + 1 nonzero coefficients on 3-CNF, every
one a multiple of 1/8, degree at most 3, support inside the clause variable sets. Two
consequences. Its Fourier spectrum is already sparse and already low degree, so "low-degree
Fourier approximation of the objective" is a question with no content for `mu`. And
`mu(0) = w_0 = 7m/8`, which `method/regimes.md` derives independently as "At p = 0 every
factor 1 - s p_i is 1, so U_j = 1/8 and lambda = m/8"; that constant is published.

`F` and `L_pair` are not polynomials (a normal tail of a ratio, and sums of logarithms), so
they have no finite Walsh expansion in the sense above. Any Fourier statement about them is
a statement about a truncation we would have to choose.

## Not done in the world

After four services and GitHub (see `queries.md`), nothing was found that:

1. computes the Walsh spectrum of a *relaxed* SAT objective and uses it to predict where a
   gradient method lands, or to bound a basin of attraction;
2. connects the correlation length of the discrete k-SAT landscape [sutton2009correlation]
   to the success probability of a continuous restart;
3. publishes code for the exact Walsh or landscape analysis of SAT instances. `gh search
   repos` returned zero on five phrasings. Not found, not "does not exist".

## Not done here

We have never computed a Walsh coefficient. `dimacs.py`'s `Formula` already holds exactly
the data Theorem 1 needs, `variable_index` and `sign`, both [m, 3], and `moments.py`
evaluates the polynomial; nothing in the package looks at its coefficients. That is a gap in
our work, not in the field's.

## Corrections to our notes, quoted

**1.** `../review.md` writes: "**FourierSAT** (Kyrillidis, Shrivastava, Vardi, Zhang, AAAI
2020, arXiv:1912.01032) converts Boolean constraints to multilinear/Fourier polynomials".
True, but for CNF specifically that conversion, its closed form and its linear-time bound
are Rana, Heckendorn and Whitley, AAAI 1998 [rana1998walsh], twenty-two years earlier and
not cited anywhere in our notes.

**2.** `../review.md` writes: "Separately, no paper was found, after several rephrasings
against arXiv full text, measuring the fraction of random starts that reach a satisfying
assignment under gradient or Newton dynamics on random 3-SAT." The conclusion holds after
DBLP, Crossref, Semantic Scholar and GitHub, but the stated method was wrong: the phrasings
were not the problem, the service was. arXiv indexes almost none of this line, and
`abs:"Walsh" AND abs:"MAX-SAT"` returns 0 there while the field has published continuously
since 1997. Zero on arXiv is a statement about arXiv.

**3.** `../review.md` writes: "**FastFourierSAT** ... is the real GPU implementation of
this line". As of June 2026 it is the prototype: AFSAT's own abstract says it "realises the
proof-of-concept approach, FastFourierSAT, into a fully-engineered solver"
[christopher2026afsat], with a tailored discrete Fourier transform for the floating-point
instability of the elementary-symmetric-polynomial step, which a native port would inherit.

**4.** `../review.md` writes: "FourierSAT and its successors write the same polynomial as a
sum of Fourier or Walsh characters, so 'Fourier expansion' and 'multilinear extension' name
the same object." A third name belongs in that sentence: the Walsh polynomial of an
embedded landscape [heckendorn2002embedded], with its own literature from 1997 to 2025.

**5.** `brief.md` writes: "The Gaussian surrogate is a second-moment correction of the
independence surrogate; the question is whether the covariance term changes where gradient
ascent lands." The second half stands. The first half needs a date: computing moments of
this function class in polynomial time from the Walsh coefficients is
[heckendorn1999summary] in 1999 and [heckendorn2002embedded] in 2002, and Heckendorn's own
conclusion is the warning we should carry, that "knowing the epistasis and many of the
hyperplane statistics is not enough to solve the exponentially difficult part of these
general problems". What is new here is the measure and the use: a general product measure p
in (-1,1)^n rather than uniform or a schema, and the moments as a gradient objective rather
than as a difficulty predictor. A schema average in [rana1998walsh]'s sense is exactly
`mu(p)` at p in {-1, 0, +1}^n, so our relaxation is the continuous interpolation of the
object whose flatness that paper proves.

**6.** `method/open-directions.md` writes: "the product-tree FFT of FastFourierSAT is
needed; the C++ library in `../../solver` is where that would go." Correct, and narrower
than it sounds: FastFourierSAT's abstract says the FFT computes elementary symmetric
polynomials, "the major computational task in previous CLS methods"
[cen2025fastfouriersat]. Plain 3-CNF has no symmetric constraint, so the FFT buys nothing
on the families we benchmark; it is an XOR and cardinality feature only.

## What this does not change

Nothing found refutes any measured number in `findings.md`. The corrections are to
attribution, to the search method behind one "not found", and to the currency of one claim.
