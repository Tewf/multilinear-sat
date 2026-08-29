#include <sstream>

#include "doctest.h"
#include "formula.hpp"

using namespace multilinear_sat;

TEST_CASE("DIMACS parsing builds clauses and occurrence lists") {
    std::istringstream input("c comment\np cnf 3 3\n1 -2 0\n2 3 0\n-1\n-3 0\n");
    Formula f = parse_dimacs(input);
    CHECK(f.variable_count == 3);
    CHECK(f.clause_count() == 3);
    CHECK(f.parity_count() == 0);
    CHECK(f.clause_length(0) == 2);
    CHECK(f.clause_length(2) == 2);
    CHECK(f.max_clause_length() == 2);
    CHECK(f.max_occurrence_count() == 2);
    // variable 1 (index 0) occurs in clause 0 at position 0 and clause 2 at position 0
    CHECK(f.occurrence_offsets[1] - f.occurrence_offsets[0] == 2);
    CHECK(f.occurrence_clauses[f.occurrence_offsets[0]] == 0);
    CHECK(f.occurrence_clauses[f.occurrence_offsets[0] + 1] == 2);
    CHECK(f.occurrence_positions[f.occurrence_offsets[0] + 1] == 0);
    CHECK(f.occurrence_literals[f.occurrence_offsets[0] + 1] == -1);
    for (int v = 0; v < f.variable_count; ++v) {
        for (int o = f.occurrence_offsets[v]; o < f.occurrence_offsets[v + 1]; ++o) {
            const int literal = f.literals[f.clause_offsets[f.occurrence_clauses[o]] + f.occurrence_positions[o]];
            CHECK(std::abs(literal) - 1 == v);
            CHECK(literal == f.occurrence_literals[o]);
        }
    }
}

TEST_CASE("the checker counts violated clauses") {
    Formula f = make_formula(3, {{1, -2}, {2, 3}, {-1, -3}});
    CHECK(satisfies(f, {1, 1, -1}));          // x1 true, x2 true, x3 false
    CHECK(count_violated(f, {1, 1, -1}) == 0);
    CHECK(count_violated(f, {-1, 1, 1}) == 1); // only clause 0 fails
    CHECK_FALSE(satisfies(f, {-1, 1, 1}));
    Formula g = make_formula(2, {{1}, {2}, {1, 2}});
    CHECK(count_violated(g, {-1, -1}) == 3);
    CHECK(count_violated(g, {1, -1}) == 1);
}

TEST_CASE("malformed formulas are rejected") {
    CHECK_THROWS(make_formula(2, {{1, 3}}));
    CHECK_THROWS(make_formula(2, {{}}));
    CHECK_THROWS(make_formula(2, {{1}}, {{}}));
}

static Formula parse(const std::string& text) {
    std::istringstream input(text);
    return parse_dimacs(input);
}

TEST_CASE("the parser accepts the SATLIB trailer, CRLF endings and zero clauses") {
    CHECK(parse("p cnf 2 1\n1 2 0\n%\n0\n").clause_count() == 1);
    CHECK(parse("p cnf 2 2\r\n1 2 0\r\n-1 0\r\n").clause_count() == 2);
    Formula empty = parse("p cnf 3 0\n");
    CHECK(empty.clause_count() == 0);
    CHECK(satisfies(empty, {1, 1, 1}));
}

TEST_CASE("the parser rejects a truncated file, a missing header and a wrong clause count") {
    CHECK_THROWS_WITH_AS(parse("p cnf 2 1\n1 2\n"), doctest::Contains("terminating 0"), std::runtime_error);
    CHECK_THROWS_WITH_AS(parse("1 2 0\n"), doctest::Contains("header"), std::runtime_error);
    CHECK_THROWS_WITH_AS(parse("p cnf 2 3\n1 2 0\n"), doctest::Contains("declares 3"), std::runtime_error);
    CHECK_THROWS_WITH_AS(parse("p dnf 2 1\n1 2 0\n"), doctest::Contains("malformed header"), std::runtime_error);
}

TEST_CASE("XNF x lines are odd parities, counted in the header with the clauses and checked as such") {
    Formula f = parse("c from cnf2xnf\np xnf 3 3\n1 2 0\nx 1 -2 3 0\nx 3 0\n");
    CHECK(f.clause_count() == 3);
    CHECK(f.parity_count() == 2);
    CHECK(f.clause_is_parity[0] == 0);
    CHECK(f.clause_is_parity[1] == 1);
    CHECK(f.clause_length(1) == 3);
    CHECK(f.max_clause_length() == 3);
    CHECK(count_violated(f, {1, 1, 1}) == 1);   // literals 1 and 3 true, -2 false: two true, even, violated; x 3 holds
    CHECK(count_violated(f, {1, -1, -1}) == 2); // 1 and -2 true, 3 false: even, violated; x 3 false, violated
    CHECK(count_violated(f, {-1, 1, 1}) == 0);  // clause by x2; only literal 3 true in the parity: odd; x 3 holds
    CHECK(satisfies(f, {-1, 1, 1}));
    CHECK_FALSE(satisfies(f, {1, 1, 1}));
    CHECK_THROWS_WITH_AS(parse("p xnf 2 1\nx 1 2\n"), doctest::Contains("terminating 0"), std::runtime_error);
    CHECK_THROWS_WITH_AS(parse("p xnf 2 2\nx 1 2 0\n"), doctest::Contains("declares 2"), std::runtime_error);
}
