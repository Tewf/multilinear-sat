# The algorithm the reviews point to: a Las Vegas hybrid with an anytime UNSAT posterior

Design note, 2026-08-29, written before its literature review (`../../literature/anytime-unsat-confidence/`
when it lands). Nothing here is built. Mohamed's requirement: good performance on satisfiable
instances (polynomial or subexponential where that is possible), and on unsatisfiable ones an
algorithm that never stops but whose probability of "UNSAT" rises with the time spent.

## The pieces, each from a review

1. **Seed.** A short continuous ascent (`mu`, or `F_diag` or `pair` if their basin gain pays
   for their step) from a random start, rounded by sign. Putikhin and Kascheev (EWDTS 2017) already seeded probSAT from a
   continuous extension of the formula, with no public code found; NLocalSAT's protocol with the
   relaxation in place of its network is the replication, and xnfSAT's authors name the same
   combination as future work (Q2, Q6).
2. **Polish.** A stochastic local search from that seed: probSAT on clauses, xnfSAT where
   parities exist (native XOR is the one ingredient the literature shows to matter on Brent
   equations). The polish is where solutions are found on uf250 today (findings.md).
3. **Restarts on the Luby schedule** (Luby, Sinclair, Zuckerman 1993), each restart's outcome
   recorded; the run-length distribution of the restarts is estimated online. On hard random
   3-SAT a well-tuned SLS has an exponential, memoryless run-length distribution (Hoos and
   Stützle 1999), where no schedule helps; Luby is the default only because the seeded walk's
   distribution is unknown until measured.
4. **A rigorous half, interleaved.** Every other restart is Schöning's walk from a uniform
   random start (3n flips), untouched by the seed. On a satisfiable 3-CNF one such try
   succeeds with probability at least (3/4)^n / q(n) for an explicit polynomial q (Schöning 1999:
   within a polynomial factor of (3/4)^n), so after K failed rigorous tries
   P(no solution seen | SAT) <= (1 - (3/4)^n / q(n))^K: a one-sided error bound that holds for
   every instance. PPSZ, at base 1.307, is the better engine for the same role (Q6). The heuristic restarts are free to be biased; the rigorous
   ones carry the certificate.
5. **The posterior.** With a prior pi = P(SAT) for the instance family and S(t) the survival
   function of the time to a solution given SAT,
   P(UNSAT | no solution by t) = (1 - pi) / ((1 - pi) + pi S(t)). Under the rigorous bound
   S(t) is exp(-K(t) (3/4)^n); under an empirical run-length model fitted on the family
   (exponential run lengths for a well-tuned SLS, Johnson SB for Schöning's walk) it decays
   fast. Either way the number is a posterior, not a proof.

## What can be claimed, and what cannot

- **Worst case.** A confidence that grows meaningfully in polynomial time on every instance is
  ruled out short of a collapse: such an algorithm decides SAT with one-sided error in polynomial time,
  which puts SAT in RP, hence NP = RP, and the polynomial hierarchy collapses (Q6 corrected the
  class: RP, not coRP). The rigorous posterior of
  piece 4 reaches constant confidence only after about (4/3)^n tries, which is Schöning's
  running time: the certificate is exact and exponential. Subexponential worst-case time for
  3-SAT contradicts the exponential time hypothesis, and the local reasoning here does nothing
  to escape the resolution-width and degree lower bounds
  (`subexponential-sat-map.md` states the test any candidate must pass).
- **Typical case, satisfiable side.** Polynomial time on random k-SAT below the algorithmic
  barrier is a theorem for other algorithms of this family: WalkSAT in polynomial time up to a
  density of order 2^k / k (Coja-Oghlan and Frieze 2014), Fix up to (1 - epsilon) 2^k ln k / k
  (Coja-Oghlan 2010); in practice probSAT reaches about 4.2 at k = 3 and backtracking survey
  propagation reaches the threshold itself, about 4.268 at N = 10^6 in practically linear time
  (Marino, Parisi, Ricci-Tersenghi 2016). No barrier at fixed k = 3 is a theorem; the overlap
  gap property and the low-degree results are asymptotic in k. The seed can only move the constant in front, unless
  it shifts the per-restart success probability p(n, alpha) in the barrier region, which is the
  measurable question and the only one open to us.
- **Typical case, unsatisfiable side.** The posterior is calibrated only relative to the
  run-length model of the family, so its meaning is "this instance behaves like an
  unsatisfiable one of its family with probability q", a sequential test (Wald) on p, not a
  refutation. SATLIB ships unsatisfiable twins (uuf50-218, uuf250-1065) so the calibration can
  be measured as a reliability curve, and the time to reach 99 % against kissat's refutation
  time is the honest comparison. The industrial answer to "never stops on UNSAT" is a complete solver,
  kissat, which uses a WalkSAT-style walk only as a phase heuristic inside CDCL, not as a
  portfolio half.

## What decides whether it is worth building

The number that decides it (occupied once, in 2017, without public code or a per-restart
measurement): the per-restart success probability of the polish seeded by the
relaxation against the same polish seeded by a random or all-zero assignment, on uf250 and on
MM-Challenge-1 (Q2, 5-plan, step 3). If the seed does not raise p by more than its cost, the
algorithm is probSAT with a Luby schedule and a posterior bolted on, which exists in pieces.
