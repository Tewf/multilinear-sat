"""P(UNSAT | the search has failed so far) from a prior on satisfiability and a model of the
failures: the rigorous one from Schöning's one-try bound, and the Beta-mixture one, where a
satisfiable instance's per-restart success probability p has a Beta(a, b) prior fitted on the
family, so that k failed restarts have marginal likelihood E[(1 - p)^k] = B(a, b + k) / B(a, b).
Both are posteriors relative to their model, not proofs."""
import math


def schoening_polynomial_factor(num_variables):
    """q(n) = 3 (3n + 1). Schöning (FOCS 1999) proves the success probability of one try, a uniform
    start and 3n flips of a uniformly chosen literal of a violated clause, is within a polynomial
    factor of (3/4)^n, and leaves the polynomial unwritten. His own inequality, from the ballot
    theorem with j / (j + 2i) >= 1/3 for i <= j, is q_j >= (1/3) sum_i C(j + 2i, i) (2/3)^i (1/3)^(i+j)
    for a start at Hamming distance j from a solution; keeping the i = j term and bounding
    C(3j, j) >= (27/4)^j / (3j + 1) (Cover and Thomas, Elements of Information Theory, theorem
    11.1.3) gives q_j >= (1/2)^j / (3 (3j + 1)), and the binomial sum over j gives
    p >= (3/4)^n / (3 (3n + 1)). PPSZ (base 1.307) would be a tighter rigorous engine; not built."""
    return 3 * (3 * num_variables + 1)


def schoening_success_bound(num_variables):
    """A lower bound on the probability that one try satisfies a satisfiable 3-CNF."""
    return 0.75 ** num_variables / schoening_polynomial_factor(num_variables)


def posterior_from_log_survival(log_survival, prior_satisfiable):
    """(1 - pi) / ((1 - pi) + pi S), S the probability of the observed failures given SAT."""
    unsatisfiable = 1.0 - prior_satisfiable
    return unsatisfiable / (unsatisfiable + prior_satisfiable * math.exp(log_survival))


def rigorous_posterior(num_variables, failures, prior_satisfiable):
    """After K failed Schöning tries: S = (1 - p_n)^K with p_n the bound above, one-sided and
    valid for every instance; at n = 250 it moves only after about 10^35 tries."""
    return posterior_from_log_survival(failures * math.log1p(-schoening_success_bound(num_variables)),
                                       prior_satisfiable)


def beta_mixture_log_likelihood(failures, a, b):
    """log E[(1 - p)^k] under p ~ Beta(a, b): log B(a, b + k) - log B(a, b)."""
    return math.lgamma(b + failures) - math.lgamma(a + b + failures) + math.lgamma(a + b) - math.lgamma(b)


def beta_mixture_posterior(failures, a, b, prior_satisfiable):
    """After k failed heuristic restarts, with the family's per-restart success fraction as the
    Beta(a, b) prior of a satisfiable instance: instance-adaptive, and exact for the mixture."""
    return posterior_from_log_survival(beta_mixture_log_likelihood(failures, a, b), prior_satisfiable)


def fit_beta_by_moments(fractions):
    """(a, b) of the Beta law with the sample mean and variance of the fractions in (0, 1)."""
    count = len(fractions)
    mean = sum(fractions) / count
    variance = sum((value - mean) ** 2 for value in fractions) / (count - 1)
    if not 0.0 < mean < 1.0 or variance <= 0.0 or variance >= mean * (1.0 - mean):
        raise ValueError("the fractions have no Beta fit by moments: need 0 < mean < 1 and variance < mean (1 - mean)")
    common = mean * (1.0 - mean) / variance - 1.0
    return mean * common, (1.0 - mean) * common
