#include "formula.hpp"

#include <fstream>
#include <sstream>
#include <stdexcept>

namespace multilinear_sat {

int Formula::max_clause_length() const {
    int longest = 0;
    for (int c = 0; c < clause_count(); ++c) longest = std::max(longest, clause_length(c));
    return longest;
}

static void build_occurrences(Formula& formula) {
    const int n = formula.variable_count;
    std::vector<int32_t> counts(n, 0);
    for (int32_t literal : formula.literals) ++counts[std::abs(literal) - 1];
    formula.occurrence_offsets.assign(n + 1, 0);
    for (int v = 0; v < n; ++v) formula.occurrence_offsets[v + 1] = formula.occurrence_offsets[v] + counts[v];
    formula.occurrence_clauses.assign(formula.literals.size(), 0);
    formula.occurrence_positions.assign(formula.literals.size(), 0);
    std::vector<int32_t> cursor(formula.occurrence_offsets.begin(), formula.occurrence_offsets.end() - 1);
    for (int c = 0; c < formula.clause_count(); ++c) {
        for (int p = formula.clause_offsets[c]; p < formula.clause_offsets[c + 1]; ++p) {
            const int v = std::abs(formula.literals[p]) - 1;
            formula.occurrence_clauses[cursor[v]] = c;
            formula.occurrence_positions[cursor[v]] = p - formula.clause_offsets[c];
            ++cursor[v];
        }
    }
}

Formula make_formula(int variable_count, const std::vector<std::vector<int32_t>>& clauses) {
    Formula formula;
    formula.variable_count = variable_count;
    formula.clause_offsets.push_back(0);
    for (const auto& clause : clauses) {
        if (clause.empty()) throw std::invalid_argument("empty clause");
        for (int32_t literal : clause) {
            if (literal == 0 || std::abs(literal) > variable_count) throw std::invalid_argument("literal out of range");
            formula.literals.push_back(literal);
        }
        formula.clause_offsets.push_back(static_cast<int32_t>(formula.literals.size()));
    }
    build_occurrences(formula);
    return formula;
}

Formula parse_dimacs(std::istream& input) {
    int variable_count = 0, declared_clauses = -1;
    std::vector<std::vector<int32_t>> clauses;
    std::vector<int32_t> current;
    std::string line;
    while (std::getline(input, line)) {
        if (line.empty() || line[0] == 'c' || line[0] == '%') continue;
        std::istringstream tokens(line);
        if (line[0] == 'p') {
            std::string p, format;
            if (!(tokens >> p >> format >> variable_count >> declared_clauses) || format != "cnf" || variable_count < 0 || declared_clauses < 0) {
                throw std::runtime_error("malformed header: " + line);
            }
            continue;
        }
        if (declared_clauses < 0) throw std::runtime_error("clause line before the p cnf header: " + line);
        int32_t literal;
        while (tokens >> literal) {
            if (literal != 0) current.push_back(literal);
            else if (!current.empty()) {          // a lone 0 (the SATLIB trailer) is not a clause
                clauses.push_back(current);
                current.clear();
            }
        }
    }
    if (declared_clauses < 0) throw std::runtime_error("missing p cnf header");
    if (!current.empty()) throw std::runtime_error("last clause has no terminating 0 (truncated file?)");
    if (static_cast<int>(clauses.size()) != declared_clauses) {
        throw std::runtime_error("header declares " + std::to_string(declared_clauses) + " clauses, file has " + std::to_string(clauses.size()));
    }
    return make_formula(variable_count, clauses);
}

Formula read_dimacs(const std::string& path) {
    std::ifstream file(path);
    if (!file) throw std::runtime_error("cannot open " + path);
    return parse_dimacs(file);
}

int count_violated(const Formula& formula, const std::vector<int8_t>& assignment) {
    int violated = 0;
    for (int c = 0; c < formula.clause_count(); ++c) {
        bool satisfied = false;
        for (int p = formula.clause_offsets[c]; p < formula.clause_offsets[c + 1] && !satisfied; ++p) {
            const int32_t literal = formula.literals[p];
            const int8_t value = assignment[std::abs(literal) - 1];
            satisfied = (literal > 0) ? (value > 0) : (value < 0);
        }
        if (!satisfied) ++violated;
    }
    return violated;
}

bool satisfies(const Formula& formula, const std::vector<int8_t>& assignment) {
    return count_violated(formula, assignment) == 0;
}

}  // namespace multilinear_sat
