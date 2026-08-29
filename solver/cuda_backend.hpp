// The batch on the device: the gradient's buffers and kernels (cuda_backend.cu) and the
// walk's (cuda_walk.cu), one class so the walk can start from the gradient's points.
#pragma once
#include "backend.hpp"

namespace multilinear_sat {

struct DeviceFormula {
    const int32_t *literals, *clause_offsets, *occurrence_offsets, *occurrence_clauses, *occurrence_positions, *occurrence_literals;
    const uint8_t* clause_is_parity;
};

class CudaBackend final : public Backend {
public:
    ~CudaBackend() override;
    const char* name() const override { return "cuda"; }
    void initialise(const Formula& formula, int batch_size, uint64_t seed) override;
    void restart_slots(const std::vector<int>& slots, uint64_t epoch) override;
    void iterate(const StepParameters& step, int64_t iteration, std::vector<int>& violated) override;
    std::vector<int8_t> rounded_assignment(int slot) const override;
    std::vector<float> point(int slot) const override;
    void begin_walk(const std::vector<WalkSlotPlan>& plan, const WalkParameters& walk, uint64_t epoch) override;
    void walk(const WalkParameters& walk, std::vector<int>& violated) override;
    std::vector<int8_t> walk_assignment(int slot) const override;
    void walk_flips_done(std::vector<int32_t>& flips) const override;
    void draw_tilted(const std::vector<float>& theta, int slots_per_group, uint64_t epoch) override;
    void anneal(const std::vector<float>& theta, const std::vector<float>& beta, int slots_per_group, int rungs, uint64_t epoch,
                std::vector<float>& log_weights, std::vector<int>& violated, std::vector<uint8_t>& found) override;
    void walk_assignments(std::vector<uint8_t>& assignments) const override;
    std::vector<int8_t> saved_assignment(int slot) const override;

private:
    std::vector<float> download(const float* buffer, int slot) const;
    WalkFormula walk_formula() const;
    WalkArrays walk_arrays() const;
    void allocate_walk();
    void ensure_tilted_buffers(size_t theta_size, size_t beta_size);
    void release();

    const Formula* formula_ = nullptr;
    DeviceFormula device_{};
    float *points_ = nullptr, *next_ = nullptr, *velocity_ = nullptr;
    uint8_t* flags_ = nullptr;
    int *counts_ = nullptr, *slots_ = nullptr;
    uint8_t *assignment_ = nullptr, *true_count_ = nullptr;
    int32_t *violated_list_ = nullptr, *violated_position_ = nullptr, *violated_count_ = nullptr, *flips_done_ = nullptr;
    WalkSlotPlan* plan_ = nullptr;
    uint32_t *probsat_weight_ = nullptr, *metropolis_threshold_ = nullptr;
    float *theta_ = nullptr, *beta_ = nullptr, *log_weights_ = nullptr;
    uint8_t *found_ = nullptr, *saved_ = nullptr;
    size_t theta_capacity_ = 0, beta_capacity_ = 0;
    int batch_size_ = 0, variable_count_ = 0, clause_count_ = 0, table_length_ = 0;
    uint64_t seed_ = 0, walk_epoch_ = 0;
};

}  // namespace multilinear_sat
