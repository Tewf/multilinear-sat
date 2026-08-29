// P(UNSAT | the search has failed so far), from a prior on satisfiability and a model of
// the failures. Two models, both posteriors relative to their model and never proofs:
//
// The rigorous one, from Schoning's one-try bound. Schoning (FOCS 1999) proves that one
// try, a uniform start and 3n flips of a uniformly chosen literal of a violated clause,
// satisfies a satisfiable 3-CNF with probability within a polynomial factor of (3/4)^n,
// and leaves the polynomial unwritten. His own inequality, from the ballot theorem with
// j / (j + 2i) >= 1/3 for i <= j, is q_j >= (1/3) sum_i C(j + 2i, i) (2/3)^i (1/3)^(i+j)
// for a start at Hamming distance j from a solution; keeping the i = j term and bounding
// C(3j, j) >= (27/4)^j / (3j + 1) (Cover and Thomas, Elements of Information Theory,
// theorem 11.1.3) gives q_j >= (1/2)^j / (3 (3j + 1)), and the binomial sum over j gives
// p >= (3/4)^n / (3 (3n + 1)). After K failed tries S = (1 - p)^K, one-sided and valid for
// every 3-CNF; at n = 250 it moves only after about 10^35 tries.
//
// The Beta-mixture one: a satisfiable instance's per-restart success probability p has a
// Beta(a, b) prior fitted on the family, so k failed heuristic restarts have marginal
// likelihood E[(1 - p)^k] = B(a, b + k) / B(a, b), instance-adaptive and exact for the
// mixture. Either way P(UNSAT | failures) = (1 - pi) / ((1 - pi) + pi S).
#pragma once
#include <cmath>
#include <cstdint>

namespace multilinear_sat {

inline double schoening_polynomial_factor(int variable_count) { return 3.0 * (3.0 * variable_count + 1.0); }

inline double log_schoening_success_bound(int variable_count) {
    return variable_count * std::log(0.75) - std::log(schoening_polynomial_factor(variable_count));
}

inline double schoening_success_bound(int variable_count) { return std::exp(log_schoening_success_bound(variable_count)); }

inline double posterior_from_log_survival(double log_survival, double prior_satisfiable) {
    const double unsatisfiable = 1.0 - prior_satisfiable;
    return unsatisfiable / (unsatisfiable + prior_satisfiable * std::exp(log_survival));
}

inline double rigorous_posterior(int variable_count, int64_t failures, double prior_satisfiable) {
    return posterior_from_log_survival(static_cast<double>(failures) * std::log1p(-schoening_success_bound(variable_count)), prior_satisfiable);
}

inline double beta_mixture_log_likelihood(int64_t failures, double a, double b) {
    return std::lgamma(b + failures) - std::lgamma(a + b + failures) + std::lgamma(a + b) - std::lgamma(b);
}

inline double beta_mixture_posterior(int64_t failures, double a, double b, double prior_satisfiable) {
    return posterior_from_log_survival(beta_mixture_log_likelihood(failures, a, b), prior_satisfiable);
}

}  // namespace multilinear_sat
