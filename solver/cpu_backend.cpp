// CPU backend: the same per-clause and per-variable functions as the CUDA kernels,
// run as OpenMP loops over (slot, clause) and (slot, variable).
#include <algorithm>
#include <cmath>

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
        n_ = formula.variable_count;
        m_ = formula.clause_count();
        current_.assign(static_cast<size_t>(batch_size) * n_, 0.0f);
        next_.assign(current_.size(), 0.0f);
        velocity_.assign(current_.size(), 0.0f);
        clause_violated_.assign(static_cast<size_t>(batch_size) * m_, 0);
        std::vector<int> all(batch_size);
        for (int b = 0; b < batch_size; ++b) all[b] = b;
        restart_slots(all, 0);
    }

    void restart_slots(const std::vector<int>& slots, uint64_t epoch) override {
        for (int slot : slots) {
            for (int v = 0; v < n_; ++v) {
                current_[static_cast<size_t>(slot) * n_ + v] = 2.0f * uniform_random(seed_, epoch, slot, v) - 1.0f;
                velocity_[static_cast<size_t>(slot) * n_ + v] = 0.0f;
            }
        }
    }

    void iterate(const StepParameters& step, int64_t iteration, std::vector<int>& violated) override {
        const Formula& f = *formula_;
        violated.assign(batch_size_, 0);
#pragma omp parallel for schedule(static)
        for (int b = 0; b < batch_size_; ++b) {
            const float* point = &current_[static_cast<size_t>(b) * n_];
            uint8_t* flags = &clause_violated_[static_cast<size_t>(b) * m_];
            int count = 0;
            for (int c = 0; c < m_; ++c) {
                flags[c] = mark_clause_violated(f.literals.data(), f.clause_offsets.data(), c, point);
                count += flags[c];
            }
            violated[b] = count;
        }
        const float sigma = step.kick_sigma * powf(step.kick_decay, static_cast<float>(iteration));
#pragma omp parallel for schedule(static)
        for (int b = 0; b < batch_size_; ++b) {
            const size_t base = static_cast<size_t>(b) * n_;
            for (int v = 0; v < n_; ++v) {
                update_variable(f.literals.data(), f.clause_offsets.data(), f.occurrence_offsets.data(),
                                f.occurrence_clauses.data(), f.occurrence_positions.data(),
                                &clause_violated_[static_cast<size_t>(b) * m_], &current_[base], &next_[base],
                                &velocity_[base], v, step, sigma, seed_, static_cast<uint64_t>(iteration) + 1, b);
            }
        }
        std::swap(current_, next_);
    }

    std::vector<int8_t> rounded_assignment(int slot) const override {
        // After iterate() swapped the buffers, next_ holds the point the counts were taken on.
        std::vector<int8_t> assignment(n_);
        for (int v = 0; v < n_; ++v) assignment[v] = next_[static_cast<size_t>(slot) * n_ + v] >= 0.0f ? 1 : -1;
        return assignment;
    }

    std::vector<float> point(int slot) const override {
        return std::vector<float>(current_.begin() + static_cast<size_t>(slot) * n_,
                                  current_.begin() + static_cast<size_t>(slot + 1) * n_);
    }

private:
    const Formula* formula_ = nullptr;
    int batch_size_ = 0, n_ = 0, m_ = 0;
    uint64_t seed_ = 0;
    std::vector<float> current_, next_, velocity_;
    std::vector<uint8_t> clause_violated_;
};

std::unique_ptr<Backend> make_cpu_backend() { return std::make_unique<CpuBackend>(); }

}  // namespace multilinear_sat
