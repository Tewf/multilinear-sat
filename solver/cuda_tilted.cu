// CUDA backend, the tilted seed's half: one thread per slot for the draw of q_theta and for
// the annealing ladder, the group's theta and beta uploaded before each launch.
#include "cuda_backend.hpp"
#include "cuda_helpers.cuh"
#include "tilted_anneal.hpp"

namespace multilinear_sat {

constexpr int tilted_block_size = 128;

__global__ void draw_tilted_kernel(WalkFormula formula, WalkArrays arrays, const float* theta, int slots_per_group, uint64_t seed,
                                   uint64_t epoch, int batch_size) {
    const int slot = blockIdx.x * blockDim.x + threadIdx.x;
    if (slot >= batch_size) return;
    WalkSlot state = slot_view(arrays, slot, formula.variable_count, formula.clause_count);
    draw_tilted_slot(formula, state, theta + (size_t)(slot / slots_per_group) * formula.variable_count, seed, epoch, slot);
}

__global__ void anneal_kernel(WalkFormula formula, WalkArrays arrays, const float* theta, const float* beta, int slots_per_group, int rungs, bool skc_rungs, float noise,
                              uint64_t seed, uint64_t epoch, int batch_size, float* log_weights, uint8_t* found, uint8_t* saved) {
    const int slot = blockIdx.x * blockDim.x + threadIdx.x;
    if (slot >= batch_size) return;
    WalkSlot state = slot_view(arrays, slot, formula.variable_count, formula.clause_count);
    const int group = slot / slots_per_group;
    found[slot] = 0;
    log_weights[slot] = anneal_slot(formula, state, theta + (size_t)group * formula.variable_count, beta[group], rungs, skc_rungs, noise, seed, epoch, slot,
                                    found + slot, saved + (size_t)slot * formula.variable_count);
}

void CudaBackend::ensure_tilted_buffers(size_t theta_size, size_t beta_size) {
    if (theta_capacity_ >= theta_size && beta_capacity_ >= beta_size) return;
    for (void* p : {(void*)theta_, (void*)beta_}) cudaFree(p);
    theta_ = static_cast<float*>(allocate(theta_size * sizeof(float), "allocate theta"));
    beta_ = static_cast<float*>(allocate(beta_size * sizeof(float), "allocate beta"));
    theta_capacity_ = theta_size;
    beta_capacity_ = beta_size;
}

void CudaBackend::draw_tilted(const std::vector<float>& theta, int slots_per_group, uint64_t epoch) {
    ensure_tilted_buffers(theta.size(), theta.size() / std::max(1, variable_count_));
    upload_into(theta_, theta, "copy theta");
    draw_tilted_kernel<<<blocks_for(batch_size_, tilted_block_size), tilted_block_size>>>(walk_formula(), walk_arrays(), theta_, slots_per_group, seed_, epoch, batch_size_);
    check(cudaGetLastError(), "draw_tilted_kernel launch");
}

void CudaBackend::anneal(const std::vector<float>& theta, const std::vector<float>& beta, int slots_per_group, int rungs, bool skc_rungs, float noise, uint64_t epoch,
                         std::vector<float>& log_weights, std::vector<int>& violated, std::vector<uint8_t>& found) {
    ensure_tilted_buffers(theta.size(), beta.size());
    upload_into(theta_, theta, "copy theta");
    upload_into(beta_, beta, "copy beta");
    anneal_kernel<<<blocks_for(batch_size_, tilted_block_size), tilted_block_size>>>(walk_formula(), walk_arrays(), theta_, beta_, slots_per_group, rungs, skc_rungs, noise,
                                                                                    seed_, epoch, batch_size_, log_weights_, found_, saved_);
    check(cudaGetLastError(), "anneal_kernel launch");
    download_into(log_weights, log_weights_, batch_size_, "copy log weights (or the anneal kernel failed)");
    download_into(violated, violated_count_, batch_size_, "copy violated counts");
    download_into(found, found_, batch_size_, "copy found flags");
}

void CudaBackend::walk_assignments(std::vector<uint8_t>& assignments) const {
    download_into(assignments, assignment_, (size_t)batch_size_ * variable_count_, "copy assignments");
}

std::vector<int8_t> CudaBackend::saved_assignment(int slot) const {
    std::vector<uint8_t> host;
    download_into(host, saved_ + (size_t)slot * variable_count_, variable_count_, "copy saved assignment");
    std::vector<int8_t> assignment(variable_count_);
    for (int variable = 0; variable < variable_count_; ++variable) assignment[variable] = host[variable] ? 1 : -1;
    return assignment;
}

}  // namespace multilinear_sat
