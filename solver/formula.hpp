// A formula in compressed form: rows that are clauses or, where clause_is_parity is set,
// odd-parity constraints (the x lines of XNF), with per-variable occurrence lists.
// Literals are signed 1-based variable indices, as in DIMACS. Assignments are int8
// vectors indexed from 0 with +1 meaning true and -1 meaning false.
#pragma once
#include <cstdint>
#include <istream>
#include <string>
#include <vector>

namespace multilinear_sat {

struct Formula {
    int variable_count = 0;
    std::vector<int32_t> literals;             // every row's literals, concatenated
    std::vector<int32_t> clause_offsets;       // row c spans [offsets[c], offsets[c+1])
    std::vector<uint8_t> clause_is_parity;     // 1 where row c is an odd parity, 0 where it is a clause
    std::vector<int32_t> occurrence_offsets;   // variable v's occurrences span [offsets[v], offsets[v+1])
    std::vector<int32_t> occurrence_clauses;   // row index of each occurrence
    std::vector<int32_t> occurrence_positions; // position of the literal inside that row
    std::vector<int32_t> occurrence_literals;  // the signed literal at that occurrence

    int clause_count() const { return static_cast<int>(clause_offsets.size()) - 1; }   // rows of both kinds
    int parity_count() const;
    int clause_length(int clause) const { return clause_offsets[clause + 1] - clause_offsets[clause]; }
    int max_clause_length() const;
    int max_occurrence_count() const;
};

Formula make_formula(int variable_count, const std::vector<std::vector<int32_t>>& clauses,
                     const std::vector<std::vector<int32_t>>& parities = {});
Formula parse_dimacs(std::istream& input);   // "p cnf", or "p xnf" with x lines read as odd parities
Formula read_dimacs(const std::string& path);

// Independent model check, used by tests and by the command line before it prints SAT.
bool satisfies(const Formula& formula, const std::vector<int8_t>& assignment);
int count_violated(const Formula& formula, const std::vector<int8_t>& assignment);

}  // namespace multilinear_sat
