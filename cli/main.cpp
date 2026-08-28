// DIMACS in, SAT-competition style output: "s SATISFIABLE" plus "v" lines and exit
// code 10, or "s UNKNOWN" and exit code 0. A "c json {...}" line carries the run
// statistics for the benchmark harness.
#include <cstdio>
#include <exception>

#include "arguments.hpp"
#include "formula.hpp"
#include "solver.hpp"

using namespace multilinear_sat;

static void print_model(const std::vector<int8_t>& assignment) {
    std::printf("v");
    int on_line = 0;
    for (size_t v = 0; v < assignment.size(); ++v) {
        std::printf(" %d", assignment[v] > 0 ? static_cast<int>(v + 1) : -static_cast<int>(v + 1));
        if (++on_line == 20 && v + 1 < assignment.size()) { std::printf("\nv"); on_line = 0; }
    }
    std::printf(" 0\n");
}

int main(int argc, char** argv) {
    cli::Arguments arguments;
    try {
        arguments = cli::parse_arguments(argc, argv);
    } catch (const std::exception& error) {
        std::fprintf(stderr, "%s\n%s", error.what(), cli::usage());
        return 1;
    }
    try {
        const Formula formula = read_dimacs(arguments.path);
        std::printf("c multilinear-sat: %d variables, %d clauses, max length %d\n", formula.variable_count,
                    formula.clause_count(), formula.max_clause_length());
        const SolveResult result = solve(formula, arguments.configuration);
        const bool certified = satisfies(formula, result.assignment);
        if (result.status == Status::Satisfiable && !certified) std::fprintf(stderr, "c certificate rejected: reporting UNKNOWN\n");
        const bool satisfiable = result.status == Status::Satisfiable && certified;
        std::printf("c json {\"status\": \"%s\", \"backend\": \"%s\", \"iterations\": %lld, \"restarts\": %lld, "
                    "\"best_violated\": %d, \"elapsed_seconds\": %.3f, \"batch_size\": %d, \"seed\": %llu}\n",
                    satisfiable ? "SATISFIABLE" : "UNKNOWN", result.backend_name.c_str(),
                    static_cast<long long>(result.iterations), static_cast<long long>(result.restarts),
                    result.best_violated, result.elapsed_seconds, arguments.configuration.batch_size,
                    static_cast<unsigned long long>(arguments.configuration.seed));
        if (satisfiable) {
            std::printf("s SATISFIABLE\n");
            if (arguments.print_model) print_model(result.assignment);
            return 10;
        }
        std::printf("s UNKNOWN\n");
        return 0;
    } catch (const std::exception& error) {
        std::fprintf(stderr, "error: %s\n", error.what());
        return 1;
    }
}
