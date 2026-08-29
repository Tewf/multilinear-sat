// The batch on the host: the gradient's points, velocities and row flags (cpu_backend.cpp)
// and the walk's assignments, counts and violated lists (cpu_walk.cpp), as OpenMP loops
// over slots calling the same inline functions as the CUDA kernels.
#pragma once
#include <vector>

#include "backend.hpp"

namespace multilinear_sat {

class CpuBackend final : public Backend {
public:
    const char* name() const override { return "cpu"; }
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
    WalkArrays walk_arrays();

    const Formula* formula_ = nullptr;
    int batch_size_ = 0, variable_count_ = 0, clause_count_ = 0;
    uint64_t seed_ = 0, walk_epoch_ = 0;
    std::vector<float> current_, next_, velocity_;
    std::vector<uint8_t> clause_violated_;
    std::vector<uint8_t> assignment_, true_count_, saved_;
    std::vector<int32_t> violated_list_, violated_position_, violated_count_, flips_done_;
    std::vector<WalkSlotPlan> plan_;
    std::vector<uint32_t> probsat_weight_, metropolis_threshold_;
};

}  // namespace multilinear_sat
