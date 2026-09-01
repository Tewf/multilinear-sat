// CPU backend, the walk half: one OpenMP iteration per slot, each taking a launch's
// worth of steps with the same inline functions as the CUDA walk kernel.
#include "cpu_backend.hpp"
#include "walk_rules.hpp"
#include "walk_tables.hpp"

namespace multilinear_sat {

WalkArrays CpuBackend::walk_arrays() {
    return {assignment_.data(), true_count_.data(), violated_list_.data(), violated_position_.data(),
            violated_count_.data(), flips_done_.data()};
}

void CpuBackend::begin_walk(const std::vector<WalkSlotPlan>& plan, const WalkParameters& walk, uint64_t epoch) {
    plan_ = plan;
    walk_epoch_ = epoch;
    const int table_length = formula_->max_occurrence_count() + 1;
    probsat_weight_ = probsat_weight_table(table_length, walk);
    metropolis_threshold_ = metropolis_threshold_table(table_length, walk);
    xnf_binary_clause_weight_ = xnf_weight_table(table_length, walk.xnf_cb, walk.xnf_binary_clause_weight);
    xnf_clause_weight_ = xnf_weight_table(table_length, walk.xnf_cb, walk.xnf_clause_weight);
    xnf_parity_weight_ = xnf_weight_table(table_length, walk.xnf_cb, walk.xnf_parity_weight);
    const WalkFormula formula = walk_formula_of(*formula_);
    const WalkArrays arrays = walk_arrays();
#pragma omp parallel for schedule(static)
    for (int slot = 0; slot < batch_size_; ++slot) {
        WalkSlot state = slot_view(arrays, slot, variable_count_, clause_count_);
        set_walk_start(formula, state, plan_[slot].start, &current_[static_cast<size_t>(slot) * variable_count_], seed_, epoch, slot);
        recount_slot(formula, state);
        flips_done_[slot] = 0;
    }
}

void CpuBackend::walk(const WalkParameters& walk, std::vector<int>& violated) {
    violated.resize(batch_size_);
    const WalkFormula formula = walk_formula_of(*formula_);
    const WalkArrays arrays = walk_arrays();
    const WalkTables tables{probsat_weight_.data(), metropolis_threshold_.data(), xnf_binary_clause_weight_.data(),
                            xnf_clause_weight_.data(), xnf_parity_weight_.data()};
#pragma omp parallel for schedule(dynamic, 16)
    for (int slot = 0; slot < batch_size_; ++slot) {
        walk_slot(formula, slot_view(arrays, slot, variable_count_, clause_count_), tables, plan_[slot], walk.walk_noise,
                  walk.walk_flips_per_launch, seed_, walk_epoch_, slot, flips_done_[slot]);
        violated[slot] = violated_count_[slot];
    }
}

std::vector<int8_t> CpuBackend::walk_assignment(int slot) const {
    std::vector<int8_t> assignment(variable_count_);
    const size_t base = static_cast<size_t>(slot) * variable_count_;
    for (int variable = 0; variable < variable_count_; ++variable) assignment[variable] = assignment_[base + variable] ? 1 : -1;
    return assignment;
}

void CpuBackend::walk_flips_done(std::vector<int32_t>& flips) const { flips = flips_done_; }

}  // namespace multilinear_sat
