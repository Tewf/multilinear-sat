// Command-line flags to a SolverConfiguration. Every tunable of configuration.hpp
// has a flag of the same name with dashes; --luby-unit is the older spelling of
// --seed-steps, kept so the recorded benchmark command lines still run.
#pragma once
#include <cstdlib>
#include <stdexcept>
#include <string>

#include "configuration.hpp"

namespace multilinear_sat::cli {

struct Arguments {
    std::string path;
    SolverConfiguration configuration;
    bool print_model = true;
};

inline const char* usage() {
    return "usage: multilinear-sat <file.cnf|file.xnf> [--time-limit S] [--iteration-limit N] [--run-limit N] [--seed N]\n"
           "         [--batch-size B] [--backend cpu|cuda|auto] [--step-size X] [--momentum X] [--kick-sigma X]\n"
           "         [--kick-decay X] [--focused-kick 0|1] [--seed-kind uniform|all-false|ascent] [--seed-steps N]\n"
           "         [--polish-flips N] [--stall-patience N] [--walk-rule skc|probsat|schoening|metropolis]\n"
           "         [--walk-noise X] [--probsat-cb X] [--probsat-eps X] [--metropolis-beta X] [--walk-flips-per-launch N]\n"
           "         [--rigorous-fraction X] [--prior-satisfiable X] [--beta-prior-a X] [--beta-prior-b X]\n"
           "         [--no-model] [--verbose]\n"
           "prints s SATISFIABLE and a v line (exit 10) or s UNKNOWN (exit 0); never claims UNSAT\n";
}

inline SeedKind parse_seed_kind(const std::string& kind) {
    if (kind == "uniform") return SeedKind::Uniform;
    if (kind == "all-false") return SeedKind::AllFalse;
    if (kind == "ascent") return SeedKind::Ascent;
    throw std::invalid_argument("unknown seed kind " + kind + " (uniform, all-false or ascent)");
}

inline WalkRule parse_walk_rule(const std::string& rule) {
    if (rule == "skc") return WalkRule::Skc;
    if (rule == "probsat") return WalkRule::ProbSat;
    if (rule == "schoening") return WalkRule::Schoening;
    if (rule == "metropolis") return WalkRule::Metropolis;
    throw std::invalid_argument("unknown walk rule " + rule + " (skc, probsat, schoening or metropolis)");
}

inline BackendKind parse_backend(const std::string& kind) {
    if (kind == "cpu") return BackendKind::Cpu;
    if (kind == "cuda") return BackendKind::Cuda;
    if (kind == "auto") return BackendKind::Auto;
    throw std::invalid_argument("unknown backend " + kind + " (cpu, cuda or auto)");
}

inline Arguments parse_arguments(int argc, char** argv) {
    Arguments arguments;
    auto value = [&](int& i) -> std::string {
        if (i + 1 >= argc) throw std::invalid_argument(std::string("missing value for ") + argv[i]);
        return argv[++i];
    };
    for (int i = 1; i < argc; ++i) {
        const std::string flag = argv[i];
        SolverConfiguration& c = arguments.configuration;
        if (flag == "--time-limit") c.time_limit_seconds = std::stod(value(i));
        else if (flag == "--iteration-limit") c.iteration_limit = std::stoll(value(i));
        else if (flag == "--run-limit") c.run_limit = std::stoll(value(i));
        else if (flag == "--seed") c.seed = std::stoull(value(i));
        else if (flag == "--batch-size") c.batch_size = std::stoi(value(i));
        else if (flag == "--step-size") c.step.step_size = std::stof(value(i));
        else if (flag == "--momentum") c.step.momentum = std::stof(value(i));
        else if (flag == "--kick-sigma") c.step.kick_sigma = std::stof(value(i));
        else if (flag == "--kick-decay") c.step.kick_decay = std::stof(value(i));
        else if (flag == "--focused-kick") c.step.focused_kick = std::stoi(value(i)) != 0;
        else if (flag == "--seed-kind") c.seed_kind = parse_seed_kind(value(i));
        else if (flag == "--seed-steps" || flag == "--luby-unit") c.seed_steps = std::stoi(value(i));
        else if (flag == "--polish-flips") c.polish_flips = std::stoll(value(i));
        else if (flag == "--stall-patience") c.stall_patience = std::stoi(value(i));
        else if (flag == "--walk-rule") c.walk.walk_rule = parse_walk_rule(value(i));
        else if (flag == "--walk-noise") c.walk.walk_noise = std::stof(value(i));
        else if (flag == "--probsat-cb") c.walk.probsat_cb = std::stof(value(i));
        else if (flag == "--probsat-eps") c.walk.probsat_eps = std::stof(value(i));
        else if (flag == "--metropolis-beta") c.walk.metropolis_beta = std::stof(value(i));
        else if (flag == "--walk-flips-per-launch") c.walk.walk_flips_per_launch = std::stoi(value(i));
        else if (flag == "--rigorous-fraction") c.rigorous_fraction = std::stof(value(i));
        else if (flag == "--prior-satisfiable") c.prior_satisfiable = std::stod(value(i));
        else if (flag == "--beta-prior-a") c.beta_prior_a = std::stod(value(i));
        else if (flag == "--beta-prior-b") c.beta_prior_b = std::stod(value(i));
        else if (flag == "--no-model") arguments.print_model = false;
        else if (flag == "--verbose") c.verbose = true;
        else if (flag == "--backend") c.backend = parse_backend(value(i));
        else if (flag.rfind("--", 0) == 0) throw std::invalid_argument("unknown flag " + flag);
        else arguments.path = flag;
    }
    if (arguments.path.empty()) throw std::invalid_argument("no input file");
    return arguments;
}

}  // namespace multilinear_sat::cli
