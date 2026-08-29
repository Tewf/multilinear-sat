// CPU backend, the gradient half: the same per-row and per-variable functions as the
// CUDA kernels, run as OpenMP loops over (slot, row) and (slot, variable).
#include "cpu_backend.hpp"

#include <algorithm>

#include "batch_kernels.hpp"

namespace multilinear_sat {

void CpuBackend::initialise(const Formula& formula, int batch_size, uint64_t seed) {
    formula_ = &formula;
    batch_size_ = batch_size;
    seed_ = seed;
    variable_count_ = formula.variable_count;
    clause_count_ = formula.clause_count();
    current_.assign(static_cast<size_t>(batch_size) * variable_count_, 0.0f);
    next_.assign(current_.size(), 0.0f);
    velocity_.assign(current_.size(), 0.0f);
    clause_violated_.assign(static_cast<size_t>(batch_size) * clause_count_, 0);
    assignment_.assign(current_.size(), 0);
    true_count_.assign(clause_violated_.size(), 0);
    violated_list_.assign(clause_violated_.size(), 0);
    violated_position_.assign(clause_violated_.size(), 0);
    violated_count_.assign(batch_size, 0);
    flips_done_.assign(batch_size, 0);
    plan_.assign(batch_size, WalkSlotPlan{0, 0, 0});
    restart_slots(every_slot(batch_size), 0);
}

void CpuBackend::restart_slots(const std::vector<int>& slots, uint64_t epoch) {
    for (int slot : slots) {
        const size_t base = static_cast<size_t>(slot) * variable_count_;
        for (int variable = 0; variable < variable_count_; ++variable) {
            current_[base + variable] = 2.0f * uniform_random(seed_, epoch, slot, variable) - 1.0f;
            velocity_[base + variable] = 0.0f;
        }
    }
}

void CpuBackend::iterate(const StepParameters& step, int64_t iteration, std::vector<int>& violated) {
    const Formula& formula = *formula_;
    violated.assign(batch_size_, 0);
#pragma omp parallel for schedule(static)
    for (int slot = 0; slot < batch_size_; ++slot) {
        const float* point = &current_[static_cast<size_t>(slot) * variable_count_];
        uint8_t* flags = &clause_violated_[static_cast<size_t>(slot) * clause_count_];
        int count = 0;
        for (int clause = 0; clause < clause_count_; ++clause) {
            flags[clause] = mark_clause_violated(formula.literals.data(), formula.clause_offsets.data(), formula.clause_is_parity.data(), clause, point);
            count += flags[clause];
        }
        violated[slot] = count;
    }
    const float sigma = kick_sigma_at(step, iteration);
#pragma omp parallel for schedule(static)
    for (int slot = 0; slot < batch_size_; ++slot) {
        const size_t base = static_cast<size_t>(slot) * variable_count_;
        const uint8_t* flags = &clause_violated_[static_cast<size_t>(slot) * clause_count_];
        for (int variable = 0; variable < variable_count_; ++variable) {
            update_variable(formula.literals.data(), formula.clause_offsets.data(), formula.clause_is_parity.data(),
                            formula.occurrence_offsets.data(), formula.occurrence_clauses.data(), formula.occurrence_positions.data(),
                            flags, &current_[base], &next_[base], &velocity_[base], variable, step, sigma, seed_,
                            static_cast<uint64_t>(iteration) + 1, slot);
        }
    }
    std::swap(current_, next_);
}

std::vector<int8_t> CpuBackend::rounded_assignment(int slot) const {
    // After iterate() swapped the buffers, next_ holds the point the counts were taken on.
    std::vector<int8_t> assignment(variable_count_);
    const size_t base = static_cast<size_t>(slot) * variable_count_;
    for (int variable = 0; variable < variable_count_; ++variable) {
        assignment[variable] = rounds_true(next_[base + variable]) ? 1 : -1;
    }
    return assignment;
}

std::vector<float> CpuBackend::point(int slot) const {
    const size_t base = static_cast<size_t>(slot) * variable_count_;
    return std::vector<float>(current_.begin() + base, current_.begin() + base + variable_count_);
}

std::unique_ptr<Backend> make_cpu_backend() { return std::make_unique<CpuBackend>(); }

}  // namespace multilinear_sat
