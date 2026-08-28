// Command-line flags to a SolverConfiguration. Every tunable of configuration.hpp
// has a flag of the same name with dashes.
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
    return "usage: multilinear-sat <file.cnf> [--time-limit S] [--iteration-limit N] [--seed N] [--batch-size B]\n"
           "         [--backend cpu|cuda|auto] [--step-size X] [--momentum X] [--kick-sigma X] [--kick-decay X]\n"
           "         [--focused-kick 0|1] [--luby-unit N] [--stall-patience N] [--no-model] [--verbose]\n"
           "prints s SATISFIABLE and a v line (exit 10) or s UNKNOWN (exit 0); never claims UNSAT\n";
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
        else if (flag == "--seed") c.seed = std::stoull(value(i));
        else if (flag == "--batch-size") c.batch_size = std::stoi(value(i));
        else if (flag == "--step-size") c.step.step_size = std::stof(value(i));
        else if (flag == "--momentum") c.step.momentum = std::stof(value(i));
        else if (flag == "--kick-sigma") c.step.kick_sigma = std::stof(value(i));
        else if (flag == "--kick-decay") c.step.kick_decay = std::stof(value(i));
        else if (flag == "--focused-kick") c.step.focused_kick = std::stoi(value(i)) != 0;
        else if (flag == "--luby-unit") c.luby_unit = std::stoi(value(i));
        else if (flag == "--stall-patience") c.stall_patience = std::stoi(value(i));
        else if (flag == "--no-model") arguments.print_model = false;
        else if (flag == "--verbose") c.verbose = true;
        else if (flag == "--backend") {
            const std::string kind = value(i);
            c.backend = kind == "cpu" ? BackendKind::Cpu : kind == "cuda" ? BackendKind::Cuda : BackendKind::Auto;
        } else if (flag.rfind("--", 0) == 0) throw std::invalid_argument("unknown flag " + flag);
        else arguments.path = flag;
    }
    if (arguments.path.empty()) throw std::invalid_argument("no input file");
    return arguments;
}

}  // namespace multilinear_sat::cli
