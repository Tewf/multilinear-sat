// CPU and CUDA backends compute the same thing from the same seed: the gradient to float
// tolerance, the walk bit for bit. Skipped when no CUDA device is present, so the suite
// still passes on a CPU-only build.
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

TEST_CASE("cpu and cuda walks agree bit for bit under every rule, from every start, on clauses and parities") {
    if (!cuda_available()) {
        MESSAGE("no CUDA device: walk agreement test skipped");
        return;
    }
    for (int with_parities = 0; with_parities < 2; ++with_parities) {
        auto planted = with_parities ? testing::planted_xnf(150, 3.8, 40, 5, 13) : testing::planted_3sat(200, 4.2, 12);
        const int batch = 64;
        for (WalkRule rule : {WalkRule::Skc, WalkRule::ProbSat, WalkRule::Schoening, WalkRule::Metropolis, WalkRule::Xnf}) {
            for (SeedKind start : {SeedKind::Uniform, SeedKind::AllFalse, SeedKind::Ascent}) {
                auto cpu = make_cpu_backend();
                auto cuda = make_cuda_backend();
                cpu->initialise(planted.formula, batch, 77);
                cuda->initialise(planted.formula, batch, 77);
                std::vector<WalkSlotPlan> plan(batch, WalkSlotPlan{static_cast<uint8_t>(start), static_cast<uint8_t>(rule), 500});
                plan[3].budget = 120;   // one slot with a shorter budget, one thread that idles early
                WalkParameters walk;
                walk.walk_rule = rule;
                walk.walk_flips_per_launch = 64;
                cpu->begin_walk(plan, walk, 5);
                cuda->begin_walk(plan, walk, 5);
                std::vector<int> cpu_violated, cuda_violated;
                std::vector<int32_t> cpu_flips, cuda_flips;
                for (int launch = 0; launch < 8; ++launch) {
                    cpu->walk(walk, cpu_violated);
                    cuda->walk(walk, cuda_violated);
                    CHECK(cpu_violated == cuda_violated);
                }
                for (int slot = 0; slot < batch; slot += 7) CHECK(cpu->walk_assignment(slot) == cuda->walk_assignment(slot));
                cpu->walk_flips_done(cpu_flips);
                cuda->walk_flips_done(cuda_flips);
                CHECK(cpu_flips == cuda_flips);
                CHECK(cpu_flips[3] <= 120);
            }
        }
    }
}

TEST_CASE("cpu and cuda tilted draws agree exactly and their annealing ladders agree to float tolerance") {
    if (!cuda_available()) {
        MESSAGE("no CUDA device: tilted agreement test skipped");
        return;
    }
    auto planted = testing::planted_3sat(120, 4.0, 14);
    const int batch = 64, groups = 4;
    std::vector<float> theta(static_cast<size_t>(groups) * planted.formula.variable_count);
    uint64_t state = 8;
    for (float& value : theta) value = static_cast<float>(testing::next_random(state) % 1000) / 500.0f - 1.0f;
    const std::vector<float> beta = {0.1f, 0.5f, 1.0f, 2.0f};
    auto cpu = make_cpu_backend();
    auto cuda = make_cuda_backend();
    cpu->initialise(planted.formula, batch, 91);
    cuda->initialise(planted.formula, batch, 91);
    cpu->draw_tilted(theta, batch / groups, 3);
    cuda->draw_tilted(theta, batch / groups, 3);
    std::vector<uint8_t> cpu_draws, cuda_draws;
    cpu->walk_assignments(cpu_draws);
    cuda->walk_assignments(cuda_draws);
    CHECK(cpu_draws == cuda_draws);
    std::vector<float> cpu_weights, cuda_weights;
    std::vector<int> cpu_violated, cuda_violated;
    std::vector<uint8_t> cpu_found, cuda_found;
    cpu->anneal(theta, beta, batch / groups, 200, false, 0.5f, 3, cpu_weights, cpu_violated, cpu_found);
    cuda->anneal(theta, beta, batch / groups, 200, false, 0.5f, 3, cuda_weights, cuda_violated, cuda_found);
    // logf differs in the last bits between host and device, so one acceptance in a few
    // thousand may go the other way and the chains diverge from there: the weights agree
    // closely on most slots and the counts stay in the same range.
    int weight_disagreements = 0;
    for (int slot = 0; slot < batch; ++slot) weight_disagreements += std::fabs(cpu_weights[slot] - cuda_weights[slot]) > 1e-3f * std::fabs(cpu_weights[slot]) + 1e-2f;
    CHECK(weight_disagreements <= 8);
    CHECK(cpu_found == cuda_found);
    // The SKC rung takes no acceptance, so that mode has no logf and must agree exactly.
    cpu->draw_tilted(theta, batch / groups, 4);
    cuda->draw_tilted(theta, batch / groups, 4);
    cpu->anneal(theta, beta, batch / groups, 200, true, 0.5f, 5, cpu_weights, cpu_violated, cpu_found);
    cuda->anneal(theta, beta, batch / groups, 200, true, 0.5f, 5, cuda_weights, cuda_violated, cuda_found);
    CHECK(cpu_violated == cuda_violated);
    CHECK(cpu_found == cuda_found);
}
