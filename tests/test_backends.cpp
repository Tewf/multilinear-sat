// CPU and CUDA backends compute the same thing from the same seed. Skipped when no
// CUDA device is present, so the suite still passes on a CPU-only build.
#include <cmath>

#include "backend.hpp"
#include "doctest.h"
#include "planted_instances.hpp"

using namespace multilinear_sat;

TEST_CASE("cpu and cuda backends agree on initial points, counts and one step") {
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
    for (int iteration = 0; iteration < 3; ++iteration) {
        cpu->iterate(step, iteration, cpu_violated);
        cuda->iterate(step, iteration, cuda_violated);
        CHECK(cpu_violated == cuda_violated);
        for (int slot = 0; slot < batch; slot += 3) {
            const std::vector<float> a = cpu->point(slot), b = cuda->point(slot);
            REQUIRE(a.size() == b.size());
            float largest = 0.0f;
            for (size_t i = 0; i < a.size(); ++i) largest = std::max(largest, std::fabs(a[i] - b[i]));
            CHECK(largest < 1e-4f);
        }
    }
    cpu->restart_slots({1, 4}, 7);
    cuda->restart_slots({1, 4}, 7);
    CHECK(cpu->point(1) == cuda->point(1));
}
