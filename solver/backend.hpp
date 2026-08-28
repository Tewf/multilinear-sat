// What a backend must provide: a batch of points on its device and one iteration of
// the dynamics over the whole batch. The restart policy, the time limit and the
// certificate check live in the solver loop, which is backend-independent.
#pragma once
#include <cstdint>
#include <memory>
#include <vector>

#include "configuration.hpp"
#include "formula.hpp"

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
};

std::unique_ptr<Backend> make_cpu_backend();
std::unique_ptr<Backend> make_cuda_backend();   // throws if built without CUDA or no device
bool cuda_available();

}  // namespace multilinear_sat
