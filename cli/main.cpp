// DIMACS or XNF in, SAT-competition style output: "s SATISFIABLE" plus "v" lines and
// exit code 10, or "s UNKNOWN" and exit code 0. A "c json {...}" line carries the run
// statistics for the benchmark scripts; the two posteriors in it are numbers about the
// failed restarts, never a verdict.
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

static const char* seed_kind_name(SeedKind kind) {
    return kind == SeedKind::Uniform ? "uniform" : kind == SeedKind::AllFalse ? "all-false" : kind == SeedKind::Ascent ? "ascent" : "tilted";
}

static const char* walk_rule_name(WalkRule rule) {
    return rule == WalkRule::Skc ? "skc" : rule == WalkRule::ProbSat ? "probsat" : rule == WalkRule::Schoening ? "schoening" : "metropolis";
}

static void print_json(const SolveResult& r, const SolverConfiguration& c, bool satisfiable) {
    std::printf("c json {\"status\": \"%s\", \"backend\": \"%s\", \"iterations\": %lld, \"restarts\": %lld, \"runs\": %lld, "
                "\"flips\": %lld, \"best_violated\": %d, \"elapsed_seconds\": %.3f, \"seed_seconds\": %.3f, \"polish_seconds\": %.3f, "
                "\"polish_successes\": %lld, \"heuristic_failures\": %lld, \"rigorous_failures\": %lld, "
                "\"posterior_beta\": %.6g, \"posterior_rigorous\": %.6g, \"batch_size\": %d, \"seed\": %llu, "
                "\"seed_kind\": \"%s\", \"seed_steps\": %d, \"polish_flips\": %lld, \"walk_rule\": \"%s\", \"rigorous_fraction\": %g}\n",
                satisfiable ? "SATISFIABLE" : "UNKNOWN", r.backend_name.c_str(), static_cast<long long>(r.iterations),
                static_cast<long long>(r.restarts), static_cast<long long>(r.runs), static_cast<long long>(r.flips), r.best_violated,
                r.elapsed_seconds, r.seed_seconds, r.polish_seconds, static_cast<long long>(r.polish_successes),
                static_cast<long long>(r.heuristic_failures), static_cast<long long>(r.rigorous_failures), r.posterior_beta,
                r.posterior_rigorous, c.batch_size, static_cast<unsigned long long>(c.seed), seed_kind_name(c.seed_kind), c.seed_steps,
                static_cast<long long>(c.polish_flips), walk_rule_name(c.walk.walk_rule), static_cast<double>(c.rigorous_fraction));
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
        std::printf("c multilinear-sat: %d variables, %d clauses, %d parities, max length %d\n", formula.variable_count,
                    formula.clause_count() - formula.parity_count(), formula.parity_count(), formula.max_clause_length());
        const SolveResult result = solve(formula, arguments.configuration);
        const bool certified = satisfies(formula, result.assignment);
        if (result.status == Status::Satisfiable && !certified) std::fprintf(stderr, "c certificate rejected: reporting UNKNOWN\n");
        const bool satisfiable = result.status == Status::Satisfiable && certified;
        print_json(result, arguments.configuration, satisfiable);
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
