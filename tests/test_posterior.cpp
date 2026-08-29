// The two UNSAT posteriors: the prior at zero failures, monotone in the failures, exact
// closed forms, and no movement where the bound is vacuous.
#include <cmath>
#include <initializer_list>

#include "doctest.h"
#include "posterior.hpp"

using namespace multilinear_sat;

TEST_CASE("the Beta(1, 1) mixture posterior is (k + 1) / (k + 2) at an even prior") {
    for (int64_t k : {0, 1, 2, 10, 1000}) {
        CHECK(beta_mixture_posterior(k, 1.0, 1.0, 0.5) == doctest::Approx(static_cast<double>(k + 1) / static_cast<double>(k + 2)));
    }
    CHECK(beta_mixture_posterior(0, 3.0, 7.0, 0.2) == doctest::Approx(0.8));
}

TEST_CASE("the Beta-mixture likelihood is the product of the survival ratios") {
    const double a = 2.5, b = 4.0;
    double product = 1.0;
    for (int64_t k = 0; k < 12; ++k) {
        CHECK(std::exp(beta_mixture_log_likelihood(k, a, b)) == doctest::Approx(product));
        product *= (b + k) / (a + b + k);
    }
}

TEST_CASE("both posteriors start at the prior and rise with every failure") {
    CHECK(rigorous_posterior(3, 0, 0.5) == doctest::Approx(0.5));
    CHECK(beta_mixture_posterior(0, 2.0, 5.0, 0.5) == doctest::Approx(0.5));
    double previous_rigorous = 0.0, previous_beta = 0.0;
    for (int64_t k = 0; k <= 200; ++k) {
        const double rigorous = rigorous_posterior(3, k, 0.5), beta = beta_mixture_posterior(k, 2.0, 5.0, 0.5);
        CHECK(rigorous > previous_rigorous);
        CHECK(beta > previous_beta);
        CHECK(rigorous < 1.0);
        CHECK(beta < 1.0);
        previous_rigorous = rigorous;
        previous_beta = beta;
    }
}

TEST_CASE("Schoening's bound is (3/4)^n / (3 (3n + 1)) and the rigorous posterior follows it exactly") {
    CHECK(schoening_success_bound(3) == doctest::Approx((27.0 / 64.0) / 30.0));
    CHECK(schoening_success_bound(250) == doctest::Approx(2.7e-35).epsilon(0.05));
    const double p = schoening_success_bound(3);
    CHECK(rigorous_posterior(3, 1, 0.5) == doctest::Approx(0.5 / (0.5 + 0.5 * (1.0 - p))));
    CHECK(rigorous_posterior(3, 5, 0.3) == doctest::Approx(0.7 / (0.7 + 0.3 * std::pow(1.0 - p, 5))));
}

TEST_CASE("where the bound is vacuous the rigorous posterior stays at the prior instead of failing") {
    CHECK(rigorous_posterior(250, 1000000, 0.5) == doctest::Approx(0.5).epsilon(1e-12));
    const double huge = rigorous_posterior(19251, 1000000, 0.5);
    CHECK(std::isfinite(huge));
    CHECK(huge == doctest::Approx(0.5));
}
