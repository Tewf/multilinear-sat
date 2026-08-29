# The tanh parametrisation, and what the field calls it

Question 4 of `work/2026-08-28_gaussian-surrogate-sat/brief.md`: our ascent sets
p = tanh(theta) and runs Adam on theta. What is that, against mirror descent, natural
gradient and the Ising-machine nonlinearities, and does anything published say which
geometry gives a larger basin on a multilinear objective on the cube? Each reference carries
a bib key, an identifier and how it was verified on 2026-08-29.

## What our parametrisation is, exactly

For x in {-1, 1} with mean p the variance is 1 - p^2 and atanh(p) is half the log odds, the
canonical parameter of the family, so theta is the natural parameter and dp/dtheta = 1 - p^2
is the variance. A gradient flow on theta therefore moves p by dp/dt = (1 - p^2)^2 dF/dp,
the chain rule applying 1 - p^2 twice, once to the gradient and once to the motion. A mirror
flow with map psi obeys psi''(p) dp/dt = dF/dp, so our parametrisation is the mirror
geometry **psi''(p) = (1 - p^2)^{-2}**.

Compare the standard choices. Natural gradient ascent [amari1998natural,
DOI 10.1162/089976698300017746, Crossref] uses the Fisher information I(p) = 1/(1 - p^2),
giving psi''(p) = (1 - p^2)^{-1}; exponentiated gradient [kivinen1997eg,
DOI 10.1006/inco.1996.2612, Crossref], that is, entropic mirror descent [beck2003mirror,
DOI 10.1016/S0167-6377(02)00231-6, Crossref], uses the binary entropy in q = (1 + p)/2,
whose second derivative in p is also (1 - p^2)^{-1}. **Derived here, not found stated
anywhere:** the two are the same geometry for a product of Bernoullis, and tanh is that
geometry applied twice, slowing quadratically rather than linearly near a vertex, so it
commits later than either. The clipped Euclidean box (our `fourier` baseline) is psi'' = 1
and commits earliest, matching the observation logged in
`work/2026-08-28_gaussian-surrogate-sat/notes.md` that "the box relaxation puts 96 % of
coordinates at plus or minus 1".

## That a reparametrisation is a mirror descent is a theorem

[amid2020reparam, arXiv:2002.10487, arXiv API, abstract fetched] gives "a general framework
for casting a mirror descent update as a gradient descent update on a different set of
parameters", proved for the continuous-time flows, and says whether the discrete updates
track them "remains an interesting open problem"; [ghai2022equivalence, arXiv:2205.15235,
arXiv API, abstract fetched] answers that for online non-convex gradient descent with an
O(T^{2/3}) regret bound. Our Adam run is a discrete mirror ascent only up to that gap.

## Somebody has already run mirror descent on this objective class

[cen2025fouriercsp, arXiv:2510.04480, v2 HTML read directly] runs negative-entropy mirror
descent, psi(P) = <P, log P>, on products of probability simplices for the Walsh-Fourier
multilinear relaxation of a CSP, with a rate (its Theorem 3.10) and a comparison against
projected gradient: mirror descent needs fewer iterations but more wall-clock time, because
of backtracking line search, and a hybrid is most time-efficient. Its Table 1 was read
through a fetch summary and should be checked before being quoted. Closest published answer
to question 4, and its shape matches ours: the better geometry wins per step, loses per
second.

## Ising-machine nonlinearities, for contrast

[hopfield1985neural, DOI 10.1007/BF00339943, Crossref] is the ancestor: an analog neuron
with a sigmoid of adjustable gain, p = tanh(theta / T) in the symmetric encoding. Ours is
that at fixed gain, with no annealing schedule, the one knob that line always turns.
[goto2019sb, DOI 10.1126/sciadv.aav2372, Crossref, abstract from Semantic Scholar] replaces
the sigmoid with a bifurcating cubic Hamiltonian and reports an all-to-all 2000-node MAX-CUT
in 0.5 ms on an FPGA, about ten times a coherent Ising machine [inagaki2016cim,
DOI 10.1126/science.aah4243, Crossref]; neither is a gradient method and neither reports
basins. [ercseyravasz2011ctds, DOI 10.1038/nphys2105, Crossref, abstract from Semantic
Scholar] is the opposite decision: unbounded, exponentially growing clause weights instead
of a bounded nonlinearity, which removes the local traps at the stated price of "exponential
fluctuations in its energy function", with basin boundaries fractal above the density
threshold; [molnar2018maxsat, DOI 10.1038/s41467-018-07327-2, Crossref] and [molnar2020gpu,
DOI 10.1016/j.cpc.2020.107469, Crossref] carry it to MaxSAT and to GPUs. All of these make
the nonlinearity or the weights time-dependent; our tanh is static.

## Not found, and what to do

No work compares basins between mirror geometries for a non-convex multilinear objective on
the cube: zero hits on arXiv for `all:"mirror descent" AND all:"nonconvex" AND all:"basin of
attraction"` and two rephrasings, three web searches returning convex rates only
(`fft-for-relaxations/queries.md`). The only number is ours: with the objective held at
`mu`, tanh beats the clipped box at every point of
`gaussian_surrogate/experiments/basin_of_attraction.md` (0.1942 against 0.1458 at ratio 3.0,
0.0039 against 0.0021 at 4.26, 0.0261 against 0.0204 on uf50-218), and the box still solves
as much or more under a time cap because its step is cheaper.

One cheap experiment closes question 4 on the existing loop: add `--relax eg`,
psi'' = (1 - p^2)^{-1}, beside tanh and box with the objective fixed, and read the basin
fractions off the same table, isolating the exponent a in psi'' = (1 - p^2)^{-a} for a in
{0, 1, 2}. Baseline: `gaussian_surrogate/experiments/basin_of_attraction.md`. Cheaper still,
a gain schedule on the tanh, which the Ising-machine line says always matters and which we
have never varied.
