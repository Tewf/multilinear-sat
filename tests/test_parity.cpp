// Parity rows against brute force on tiny XNFs: the checker and the walk's counts on every
// assignment, the energy at every vertex, the gradient against exact central differences,
// and a solve of each kind with its certificate.
#include <cmath>
#include <sstream>

#include "backend.hpp"
#include "doctest.h"
#include "energy_math.hpp"
#include "planted_instances.hpp"
#include "solver.hpp"
#include "walk_bookkeeping.hpp"
#include "walk_rules.hpp"
#include "walk_tables.hpp"

using namespace multilinear_sat;

namespace {
Formula parse(const std::string& text) {
    std::istringstream input(text);
    return parse_dimacs(input);
}

int brute_force_violated(const Formula& f, const std::vector<int8_t>& assignment) {
    int violated = 0;
    for (int c = 0; c < f.clause_count(); ++c) {
        int true_literals = 0;
        for (int p = f.clause_offsets[c]; p < f.clause_offsets[c + 1]; ++p) true_literals += testing::literal_holds(f.literals[p], assignment);
        violated += f.clause_is_parity[c] ? (true_literals % 2 == 0) : (true_literals == 0);
    }
    return violated;
}

double total_energy(const Formula& f, const std::vector<float>& point) {
    double total = 0.0;
    for (int c = 0; c < f.clause_count(); ++c) {
        total += row_energy(f.clause_is_parity[c] != 0, f.literals.data() + f.clause_offsets[c], f.clause_length(c), point.data());
    }
    return total;
}
}  // namespace

TEST_CASE("on every assignment of a tiny XNF the checker, the walk's counts and the vertex energies agree with brute force") {
    const Formula f = parse("p xnf 4 5\n1 2 0\n-2 3 0\nx 1 -3 4 0\nx 2 4 0\nx 1 0\n");
    REQUIRE(f.clause_count() == 5);
    REQUIRE(f.parity_count() == 3);
    const WalkFormula wf = walk_formula_of(f);
    std::vector<uint8_t> assignment(4), true_count(5);
    std::vector<int32_t> list(5), position(5);
    int32_t count = 0;
    WalkSlot slot{assignment.data(), true_count.data(), list.data(), position.data(), &count};
    int satisfying = 0;
    for (int bits = 0; bits < 16; ++bits) {
        std::vector<int8_t> signs(4);
        std::vector<float> vertex(4);
        for (int v = 0; v < 4; ++v) {
            assignment[v] = (bits >> v) & 1;
            signs[v] = assignment[v] ? 1 : -1;
            vertex[v] = static_cast<float>(signs[v]);
        }
        const int expected = brute_force_violated(f, signs);
        CHECK(count_violated(f, signs) == expected);
        recount_slot(wf, slot);
        CHECK(count == expected);
        double energy = 0.0;
        for (int c = 0; c < 5; ++c) {
            const bool violated = violated_by_count(f.clause_is_parity[c] != 0, true_count[c]);
            const float row = row_energy(f.clause_is_parity[c] != 0, f.literals.data() + f.clause_offsets[c], f.clause_length(c), vertex.data());
            CHECK(row == doctest::Approx(violated ? 1.0f : -1.0f));
            CHECK(row_violated_by_rounding(f.clause_is_parity[c] != 0, f.literals.data() + f.clause_offsets[c], f.clause_length(c), vertex.data()) == violated);
            energy += row;
        }
        CHECK(energy == doctest::Approx(2.0 * expected - 5.0));
        satisfying += (expected == 0);
    }
    CHECK(satisfying == 2);   // x1 true; then x4 = not x3 (parity 1) and x2 = x3 (parity 2), x3 free
}

TEST_CASE("the parity gradient matches exact central differences") {
    auto planted = testing::planted_xnf(24, 3.0, 12, 4, 8);
    const Formula& f = planted.formula;
    REQUIRE(f.parity_count() == 12);
    std::vector<float> point(f.variable_count);
    uint64_t state = 19;
    for (float& x : point) x = 1.6f * (static_cast<float>(testing::next_random(state) % 10000) / 10000.0f) - 0.8f;
    for (int v = 0; v < f.variable_count; ++v) {
        float analytic = 0.0f;
        for (int o = f.occurrence_offsets[v]; o < f.occurrence_offsets[v + 1]; ++o) {
            const int c = f.occurrence_clauses[o];
            analytic += row_gradient_at(f.clause_is_parity[c] != 0, f.literals.data() + f.clause_offsets[c], f.clause_length(c), point.data(), f.occurrence_positions[o]);
        }
        const float h = 0.25f;   // exact for a multilinear function, whatever h
        std::vector<float> plus = point, minus = point;
        plus[v] += h;
        minus[v] -= h;
        const double numeric = (total_energy(f, plus) - total_energy(f, minus)) / (2.0 * h);
        CHECK(analytic == doctest::Approx(numeric).epsilon(1e-4).scale(1.0));
    }
}

TEST_CASE("the walk and the ascent solve a planted XNF with a certificate, and an unsatisfiable one stays Unknown") {
    auto planted = testing::planted_xnf(40, 3.5, 15, 3, 9);
    SolverConfiguration c;
    c.backend = BackendKind::Cpu;
    c.batch_size = 64;
    c.seed = 2;
    SUBCASE("walk from uniform starts") { c.seed_kind = SeedKind::Uniform; c.polish_flips = 400; }
    SUBCASE("walk from all false") { c.seed_kind = SeedKind::AllFalse; c.polish_flips = 400; }
    SUBCASE("ascent then walk") { c.seed_steps = 50; c.polish_flips = 400; }
    SUBCASE("ascent alone") { c.seed_steps = 200; }
    const SolveResult result = solve(planted.formula, c);
    REQUIRE(result.status == Status::Satisfiable);
    CHECK(satisfies(planted.formula, result.assignment));

    const Formula contradiction = parse("p xnf 2 3\nx 1 2 0\nx -1 2 0\n1 0\n");   // x1 xor x2 and not x1 xor x2 cannot both hold
    SolverConfiguration u = c;
    u.run_limit = 3;
    const SolveResult unknown = solve(contradiction, u);
    CHECK(unknown.status == Status::Unknown);
    CHECK(unknown.best_violated == 1);
    CHECK(unknown.runs == 3);
}

TEST_CASE("the xnf rule's integer weight is cb^-wb within table quantisation, split counts summing to the break count") {
    auto planted = testing::planted_xnf(40, 3.0, 12, 4, 21);
    const Formula& f = planted.formula;
    const WalkFormula wf = walk_formula_of(f);
    const WalkParameters walk;   // xnfSAT's defaults: cb 2.5, weights 2 / 3 / 5
    const int length = f.max_occurrence_count() + 1;
    const auto binary = xnf_weight_table(length, walk.xnf_cb, walk.xnf_binary_clause_weight);
    const auto longer = xnf_weight_table(length, walk.xnf_cb, walk.xnf_clause_weight);
    const auto parity = xnf_weight_table(length, walk.xnf_cb, walk.xnf_parity_weight);
    const WalkTables tables{nullptr, nullptr, binary.data(), longer.data(), parity.data()};
    std::vector<uint8_t> assignment(f.variable_count), true_count(f.clause_count());
    std::vector<int32_t> list(f.clause_count()), position(f.clause_count());
    int32_t count = 0;
    WalkSlot slot{assignment.data(), true_count.data(), list.data(), position.data(), &count};
    uint64_t state = 9;
    for (int trial = 0; trial < 3; ++trial) {
        for (int v = 0; v < f.variable_count; ++v) assignment[v] = testing::next_random(state) & 1;
        count = 0;
        recount_slot(wf, slot);
        for (int v = 0; v < f.variable_count; ++v) {
            int binary_clauses, longer_clauses, parities;
            split_break_count(wf, slot, v, binary_clauses, longer_clauses, parities);
            CHECK(binary_clauses + longer_clauses + parities == break_count(wf, slot, v));
            if (binary[binary_clauses] > 1 && longer[longer_clauses] > 1 && parity[parities] > 1) {
                const double weighted_break = 2.0 * binary_clauses + 3.0 * longer_clauses + 5.0 * parities;
                const double score = static_cast<double>(xnf_weight_of(wf, slot, tables, v)) / 65536.0 / 65536.0 / 65536.0;
                CHECK(score == doctest::Approx(std::pow(2.5, -weighted_break)).epsilon(1e-3));
            }
        }
    }
}

TEST_CASE("the xnf rule walks a planted xnf to a certificate") {
    auto planted = testing::planted_xnf(60, 2.5, 15, 4, 3);
    SolverConfiguration c;
    c.backend = BackendKind::Cpu;
    c.batch_size = 32;
    c.seed = 2;
    c.seed_kind = SeedKind::Uniform;
    c.polish_flips = 20000;
    c.walk.walk_rule = WalkRule::Xnf;
    c.time_limit_seconds = 30.0;
    const SolveResult result = solve(planted.formula, c);
    CHECK(result.status == Status::Satisfiable);
    CHECK(result.best_violated == 0);
}
