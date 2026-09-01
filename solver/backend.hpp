// What a backend must provide: a batch of points on its device, one gradient iteration
// over the whole batch, and the walk over the whole batch. The restart policy, the time
// limit and the certificate check live in the solver loop, which is backend-independent.
// The gradient is bit-exact with itself from a seed on each backend and the two backends
// agree only to float tolerance (their transcendental functions differ in the last bits);
// the walk is integer arithmetic on hashes and agrees bit for bit.
#pragma once
#include <cstdint>
#include <memory>
#include <vector>

#include "configuration.hpp"
#include "formula.hpp"
#include "walk_bookkeeping.hpp"

namespace multilinear_sat {

class Backend {
public:
    virtual ~Backend() = default;
    virtual const char* name() const = 0;

    // Allocate the batch for this formula and fill every slot with a fresh random point.
    virtual void initialise(const Formula& formula, int batch_size, uint64_t seed) = 0;

    // Resample the listed slots (epoch distinguishes successive restarts of the same slot).
    virtual void restart_slots(const std::vector<int>& slots, uint64_t epoch) = 0;

    // One iteration: rounded-point violation counts per slot (written into violated,
    // size batch_size), then gradient, kick and projected update of every slot.
    virtual void iterate(const StepParameters& step, int64_t iteration, std::vector<int>& violated) = 0;

    // The rounding of the point the last iterate() counted violations on (the point
    // before that iteration's update), as an assignment (+1 true, -1 false). This is the
    // certificate when the count was zero.
    virtual std::vector<int8_t> rounded_assignment(int slot) const = 0;

    // The current point of one slot, i.e. the one the next iterate() will evaluate.
    virtual std::vector<float> point(int slot) const = 0;

    // The walk. begin_walk sets every slot's assignment as its plan says (the rounding of
    // its current point, a fresh uniform draw of the restart stream, or all false),
    // recounts, and fixes the slot's rule and step budget. walk() then takes up to
    // walk_flips_per_launch steps on every slot with budget and violated rows left,
    // drawing from the walk stream at (epoch, slot, step), and writes the violated counts.
    virtual void begin_walk(const std::vector<WalkSlotPlan>& plan, const WalkParameters& walk, uint64_t epoch) = 0;
    virtual void walk(const WalkParameters& walk, std::vector<int>& violated) = 0;
    virtual std::vector<int8_t> walk_assignment(int slot) const = 0;
    virtual void walk_flips_done(std::vector<int32_t>& flips) const = 0;

    // The tilted seed (tilted_anneal.hpp). draw_tilted sets every slot's assignment to a
    // draw of its group's q_theta (theta is groups x variables, group = slot / slots_per_group)
    // from the restart stream at epoch, and recounts. anneal runs the ladder of `rungs`
    // proposals on every slot, leaving the annealed samples as the walk's state; it writes
    // each slot's log weight, its violated count and whether it passed through a satisfying
    // assignment, which saved_assignment then returns. walk_assignments downloads the whole
    // batch's assignments (batch x variables, 1 = true) in one copy.
    virtual void draw_tilted(const std::vector<float>& theta, int slots_per_group, uint64_t epoch) = 0;
    virtual void anneal(const std::vector<float>& theta, const std::vector<float>& beta, int slots_per_group, int rungs, bool skc_rungs, float noise, uint64_t epoch,
                        std::vector<float>& log_weights, std::vector<int>& violated, std::vector<uint8_t>& found) = 0;
    virtual void walk_assignments(std::vector<uint8_t>& assignments) const = 0;
    virtual std::vector<int8_t> saved_assignment(int slot) const = 0;
};

std::unique_ptr<Backend> make_cpu_backend();
std::unique_ptr<Backend> make_cuda_backend();   // throws if built without CUDA or no device
bool cuda_available();

inline std::vector<int> every_slot(int batch_size) {
    std::vector<int> slots(batch_size);
    for (int slot = 0; slot < batch_size; ++slot) slots[slot] = slot;
    return slots;
}

inline WalkFormula walk_formula_of(const Formula& formula) {
    return {formula.literals.data(), formula.clause_offsets.data(), formula.clause_is_parity.data(),
            formula.occurrence_offsets.data(), formula.occurrence_clauses.data(), formula.occurrence_literals.data(),
            formula.variable_count, formula.clause_count()};
}

}  // namespace multilinear_sat
