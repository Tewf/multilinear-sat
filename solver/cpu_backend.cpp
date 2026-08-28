// CPU backend: the same per-clause and per-variable functions as the CUDA kernels,
// run as OpenMP loops over (slot, clause) and (slot, variable).
#include <algorithm>

#include "backend.hpp"
#include "batch_kernels.hpp"

namespace multilinear_sat {

class CpuBackend final : public Backend {
public:
    const char* name() const override { return "cpu"; }

    void initialise(const Formula& formula, int batch_size, uint64_t seed) override {
        formula_ = &formula;
        batch_size_ = batch_size;
        seed_ = seed;
        variable_count_ = formula.variable_count;
        clause_count_ = formula.clause_count();
        current_.assign(static_cast<size_t>(batch_size) * variable_count_, 0.0f);
        next_.assign(current_.size(), 0.0f);
        velocity_.assign(current_.size(), 0.0f);
        clause_violated_.assign(static_cast<size_t>(batch_size) * clause_count_, 0);
        restart_slots(every_slot(batch_size), 0);
    }

    void restart_slots(const std::vector<int>& slots, uint64_t epoch) override {
        for (int slot : slots) {
            const size_t base = static_cast<size_t>(slot) * variable_count_;
            for (int variable = 0; variable < variable_count_; ++variable) {
                current_[base + variable] = 2.0f * uniform_random(seed_, epoch, slot, variable) - 1.0f;
                velocity_[base + variable] = 0.0f;
            }
        }
    }

    void iterate(const StepParameters& step, int64_t iteration, std::vector<int>& violated) override {
        const Formula& formula = *formula_;
        violated.assign(batch_size_, 0);
#pragma omp parallel for schedule(static)
        for (int slot = 0; slot < batch_size_; ++slot) {
            const float* point = &current_[static_cast<size_t>(slot) * variable_count_];
            uint8_t* flags = &clause_violated_[static_cast<size_t>(slot) * clause_count_];
            int count = 0;
            for (int clause = 0; clause < clause_count_; ++clause) {
                flags[clause] = mark_clause_violated(formula.literals.data(), formula.clause_offsets.data(), clause, point);
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
                update_variable(formula.literals.data(), formula.clause_offsets.data(), formula.occurrence_offsets.data(),
                                formula.occurrence_clauses.data(), formula.occurrence_positions.data(), flags,
                                &current_[base], &next_[base], &velocity_[base], variable, step, sigma, seed_,
                                static_cast<uint64_t>(iteration) + 1, slot);
            }
        }
        std::swap(current_, next_);
    }

    std::vector<int8_t> rounded_assignment(int slot) const override {
        // After iterate() swapped the buffers, next_ holds the point the counts were taken on.
        std::vector<int8_t> assignment(variable_count_);
        const size_t base = static_cast<size_t>(slot) * variable_count_;
        for (int variable = 0; variable < variable_count_; ++variable) {
            assignment[variable] = rounds_true(next_[base + variable]) ? 1 : -1;
        }
        return assignment;
    }

    std::vector<float> point(int slot) const override {
        const size_t base = static_cast<size_t>(slot) * variable_count_;
        return std::vector<float>(current_.begin() + base, current_.begin() + base + variable_count_);
    }

private:
    const Formula* formula_ = nullptr;
    int batch_size_ = 0, variable_count_ = 0, clause_count_ = 0;
    uint64_t seed_ = 0;
    std::vector<float> current_, next_, velocity_;
    std::vector<uint8_t> clause_violated_;
};

std::unique_ptr<Backend> make_cpu_backend() { return std::make_unique<CpuBackend>(); }

}  // namespace multilinear_sat
