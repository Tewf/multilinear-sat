// CPU and CUDA backends compute the same thing from the same seed. Skipped when no
// CUDA device is present, so the suite still passes on a CPU-only build.
#include <cmath>

#include "backend.hpp"
#include "doctest.h"
#include "planted_instances.hpp"

using namespace multilinear_sat;

TEST_CASE("cpu and cuda backends agree on initial points, counts and 200 steps with a restart") {
    if (!cuda_available()) {
        MESSAGE("no CUDA device: backend agreement test skipped");
        return;
    }
    auto planted = testing::planted_3sat(300, 4.2, 9);
    auto cpu = make_cpu_backend();
    auto cuda = make_cuda_backend();
    const int batch = 8;
    cpu->initialise(planted.formula, batch, 42);
    cuda->initialise(planted.formula, batch, 42);
    StepParameters step;
    std::vector<int> cpu_violated, cuda_violated;
    int count_disagreements = 0;
    float largest = 0.0f;
    for (int iteration = 0; iteration < 200; ++iteration) {
        if (iteration == 50) {            // a restart in the middle must keep the two in step
            cpu->restart_slots({1, 4}, 7);
            cuda->restart_slots({1, 4}, 7);
            CHECK(cpu->point(1) == cuda->point(1));
        }
        cpu->iterate(step, iteration, cpu_violated);
        cuda->iterate(step, iteration, cuda_violated);
        count_disagreements += (cpu_violated != cuda_violated);
        for (int slot = 0; slot < batch; slot += 3) {
            const std::vector<float> a = cpu->point(slot), b = cuda->point(slot);
            REQUIRE(a.size() == b.size());
            for (size_t i = 0; i < a.size(); ++i) largest = std::max(largest, std::fabs(a[i] - b[i]));
        }
    }
    // The transcendental functions differ in the last bits between host and device, so the
    // trajectories agree to float tolerance; a coordinate within that of zero may round
    // differently once, which is why a handful of count disagreements is tolerated.
    CHECK(largest < 1e-3f);
    CHECK(count_disagreements <= 5);
}
