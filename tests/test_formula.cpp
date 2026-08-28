#include <sstream>

#include "doctest.h"
#include "formula.hpp"

using namespace multilinear_sat;

TEST_CASE("DIMACS parsing builds clauses and occurrence lists") {
    std::istringstream input("c comment\np cnf 3 3\n1 -2 0\n2 3 0\n-1\n-3 0\n");
    Formula f = parse_dimacs(input);
    CHECK(f.variable_count == 3);
    CHECK(f.clause_count() == 3);
    CHECK(f.clause_length(0) == 2);
    CHECK(f.clause_length(2) == 2);
    CHECK(f.max_clause_length() == 2);
    // variable 1 (index 0) occurs in clause 0 at position 0 and clause 2 at position 0
    CHECK(f.occurrence_offsets[1] - f.occurrence_offsets[0] == 2);
    CHECK(f.occurrence_clauses[f.occurrence_offsets[0]] == 0);
    CHECK(f.occurrence_clauses[f.occurrence_offsets[0] + 1] == 2);
    CHECK(f.occurrence_positions[f.occurrence_offsets[0] + 1] == 0);
    for (int v = 0; v < f.variable_count; ++v) {
        for (int o = f.occurrence_offsets[v]; o < f.occurrence_offsets[v + 1]; ++o) {
            const int literal = f.literals[f.clause_offsets[f.occurrence_clauses[o]] + f.occurrence_positions[o]];
            CHECK(std::abs(literal) - 1 == v);
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
}
