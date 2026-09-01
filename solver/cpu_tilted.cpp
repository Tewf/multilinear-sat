// CPU backend, the tilted seed's half: the draw of q_theta and the annealing ladder, one
// OpenMP iteration per slot with the same inline functions as the CUDA kernels.
#include "cpu_backend.hpp"
#include "tilted_anneal.hpp"

namespace multilinear_sat {

void CpuBackend::draw_tilted(const std::vector<float>& theta, int slots_per_group, uint64_t epoch) {
    const WalkFormula formula = walk_formula_of(*formula_);
    const WalkArrays arrays = walk_arrays();
#pragma omp parallel for schedule(static)
    for (int slot = 0; slot < batch_size_; ++slot) {
        WalkSlot state = slot_view(arrays, slot, variable_count_, clause_count_);
        draw_tilted_slot(formula, state, theta.data() + static_cast<size_t>(slot / slots_per_group) * variable_count_, seed_, epoch, slot);
    }
}

void CpuBackend::anneal(const std::vector<float>& theta, const std::vector<float>& beta, int slots_per_group, int rungs, bool skc_rungs, float noise, uint64_t epoch,
                        std::vector<float>& log_weights, std::vector<int>& violated, std::vector<uint8_t>& found) {
    log_weights.resize(batch_size_);
    violated.resize(batch_size_);
    found.assign(batch_size_, 0);
    saved_.assign(static_cast<size_t>(batch_size_) * variable_count_, 0);
    const WalkFormula formula = walk_formula_of(*formula_);
    const WalkArrays arrays = walk_arrays();
#pragma omp parallel for schedule(dynamic, 16)
    for (int slot = 0; slot < batch_size_; ++slot) {
        WalkSlot state = slot_view(arrays, slot, variable_count_, clause_count_);
        const int group = slot / slots_per_group;
        log_weights[slot] = anneal_slot(formula, state, theta.data() + static_cast<size_t>(group) * variable_count_, beta[group], rungs, skc_rungs, noise,
                                        seed_, epoch, slot, &found[slot], &saved_[static_cast<size_t>(slot) * variable_count_]);
        violated[slot] = violated_count_[slot];
    }
}

void CpuBackend::walk_assignments(std::vector<uint8_t>& assignments) const { assignments = assignment_; }

std::vector<int8_t> CpuBackend::saved_assignment(int slot) const {
    std::vector<int8_t> assignment(variable_count_);
    const size_t base = static_cast<size_t>(slot) * variable_count_;
    for (int variable = 0; variable < variable_count_; ++variable) assignment[variable] = saved_[base + variable] ? 1 : -1;
    return assignment;
}

}  // namespace multilinear_sat
