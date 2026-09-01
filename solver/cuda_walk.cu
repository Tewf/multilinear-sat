// CUDA backend, the walk half: one thread per slot, each taking a launch's worth of
// steps on its own assignment, counts and violated list with the same inline functions
// as the CPU walk. The threads diverge (each follows its own violated rows), so the
// block is small.
#include "cuda_backend.hpp"
#include "cuda_helpers.cuh"
#include "walk_rules.hpp"
#include "walk_tables.hpp"

namespace multilinear_sat {

constexpr int walk_block_size = 128;

__global__ void begin_walk_kernel(WalkFormula formula, WalkArrays arrays, const WalkSlotPlan* plan, const float* points,
                                  uint64_t seed, uint64_t epoch, int batch_size) {
    const int slot = blockIdx.x * blockDim.x + threadIdx.x;
    if (slot >= batch_size) return;
    WalkSlot state = slot_view(arrays, slot, formula.variable_count, formula.clause_count);
    set_walk_start(formula, state, plan[slot].start, points + (size_t)slot * formula.variable_count, seed, epoch, slot);
    recount_slot(formula, state);
    arrays.flips_done[slot] = 0;
}

__global__ void walk_kernel(WalkFormula formula, WalkArrays arrays, const WalkSlotPlan* plan, WalkTables tables, float noise,
                            int flips_per_launch, uint64_t seed, uint64_t epoch, int batch_size) {
    const int slot = blockIdx.x * blockDim.x + threadIdx.x;
    if (slot >= batch_size) return;
    walk_slot(formula, slot_view(arrays, slot, formula.variable_count, formula.clause_count), tables, plan[slot], noise,
              flips_per_launch, seed, epoch, slot, arrays.flips_done[slot]);
}

WalkFormula CudaBackend::walk_formula() const {
    return {device_.literals, device_.clause_offsets, device_.clause_is_parity, device_.occurrence_offsets,
            device_.occurrence_clauses, device_.occurrence_literals, variable_count_, clause_count_};
}

WalkArrays CudaBackend::walk_arrays() const {
    return {assignment_, true_count_, violated_list_, violated_position_, violated_count_, flips_done_};
}

void CudaBackend::allocate_walk() {
    const size_t rows = (size_t)batch_size_ * clause_count_;
    assignment_ = static_cast<uint8_t*>(allocate((size_t)batch_size_ * variable_count_, "allocate assignments"));
    true_count_ = static_cast<uint8_t*>(allocate(rows, "allocate true counts"));
    violated_list_ = static_cast<int32_t*>(allocate(rows * sizeof(int32_t), "allocate violated lists"));
    violated_position_ = static_cast<int32_t*>(allocate(rows * sizeof(int32_t), "allocate violated positions"));
    violated_count_ = static_cast<int32_t*>(allocate(batch_size_ * sizeof(int32_t), "allocate violated counts"));
    flips_done_ = static_cast<int32_t*>(allocate(batch_size_ * sizeof(int32_t), "allocate flip counts"));
    plan_ = static_cast<WalkSlotPlan*>(allocate(batch_size_ * sizeof(WalkSlotPlan), "allocate walk plan"));
    table_length_ = formula_->max_occurrence_count() + 1;
    probsat_weight_ = static_cast<uint32_t*>(allocate(table_length_ * sizeof(uint32_t), "allocate probsat weights"));
    xnf_binary_clause_weight_ = static_cast<uint32_t*>(allocate(table_length_ * sizeof(uint32_t), "allocate xnf binary clause weights"));
    xnf_clause_weight_ = static_cast<uint32_t*>(allocate(table_length_ * sizeof(uint32_t), "allocate xnf clause weights"));
    xnf_parity_weight_ = static_cast<uint32_t*>(allocate(table_length_ * sizeof(uint32_t), "allocate xnf parity weights"));
    metropolis_threshold_ = static_cast<uint32_t*>(allocate(table_length_ * sizeof(uint32_t), "allocate metropolis thresholds"));
    log_weights_ = static_cast<float*>(allocate(batch_size_ * sizeof(float), "allocate log weights"));
    found_ = static_cast<uint8_t*>(allocate(batch_size_, "allocate found flags"));
    saved_ = static_cast<uint8_t*>(allocate((size_t)batch_size_ * variable_count_, "allocate saved assignments"));
}

void CudaBackend::begin_walk(const std::vector<WalkSlotPlan>& plan, const WalkParameters& walk, uint64_t epoch) {
    walk_epoch_ = epoch;
    upload_into(plan_, plan, "copy walk plan");
    upload_into(probsat_weight_, probsat_weight_table(table_length_, walk), "copy probsat weights");
    upload_into(metropolis_threshold_, metropolis_threshold_table(table_length_, walk), "copy metropolis thresholds");
    upload_into(xnf_binary_clause_weight_, xnf_weight_table(table_length_, walk.xnf_cb, walk.xnf_binary_clause_weight), "copy xnf binary clause weights");
    upload_into(xnf_clause_weight_, xnf_weight_table(table_length_, walk.xnf_cb, walk.xnf_clause_weight), "copy xnf clause weights");
    upload_into(xnf_parity_weight_, xnf_weight_table(table_length_, walk.xnf_cb, walk.xnf_parity_weight), "copy xnf parity weights");
    begin_walk_kernel<<<blocks_for(batch_size_, walk_block_size), walk_block_size>>>(walk_formula(), walk_arrays(), plan_, points_, seed_, epoch, batch_size_);
    check(cudaGetLastError(), "begin_walk_kernel launch");
}

void CudaBackend::walk(const WalkParameters& walk, std::vector<int>& violated) {
    const WalkTables tables{probsat_weight_, metropolis_threshold_, xnf_binary_clause_weight_, xnf_clause_weight_, xnf_parity_weight_};
    walk_kernel<<<blocks_for(batch_size_, walk_block_size), walk_block_size>>>(walk_formula(), walk_arrays(), plan_, tables, walk.walk_noise,
                                                                              walk.walk_flips_per_launch, seed_, walk_epoch_, batch_size_);
    check(cudaGetLastError(), "walk_kernel launch");
    download_into(violated, violated_count_, batch_size_, "copy violated counts (or the walk kernel failed)");
}

std::vector<int8_t> CudaBackend::walk_assignment(int slot) const {
    std::vector<uint8_t> host;
    download_into(host, assignment_ + (size_t)slot * variable_count_, variable_count_, "copy assignment");
    std::vector<int8_t> assignment(variable_count_);
    for (int variable = 0; variable < variable_count_; ++variable) assignment[variable] = host[variable] ? 1 : -1;
    return assignment;
}

void CudaBackend::walk_flips_done(std::vector<int32_t>& flips) const { download_into(flips, flips_done_, batch_size_, "copy flip counts"); }

}  // namespace multilinear_sat
