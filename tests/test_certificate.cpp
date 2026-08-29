// The certificate is the rounding of the point the counts were taken on, or the walk's
// own assignment, and a backend that lies about a zero count is caught by the checker in
// the solver loop.
#include "backend.hpp"
#include "doctest.h"
#include "energy_math.hpp"
#include "planted_instances.hpp"
#include "solver.hpp"

using namespace multilinear_sat;

static void check_counts_match_certificates(Backend& backend, const Formula& formula, int batch) {
    backend.initialise(formula, batch, 21);
    StepParameters step;
    std::vector<int> violated;
    for (int iteration = 0; iteration < 5; ++iteration) {
        std::vector<std::vector<float>> before(batch);
        for (int slot = 0; slot < batch; ++slot) before[slot] = backend.point(slot);
        backend.iterate(step, iteration, violated);
        for (int slot = 0; slot < batch; ++slot) {
            const std::vector<int8_t> assignment = backend.rounded_assignment(slot);
            for (int v = 0; v < formula.variable_count; ++v) CHECK(assignment[v] == (rounds_true(before[slot][v]) ? 1 : -1));
            CHECK(count_violated(formula, assignment) == violated[slot]);
        }
    }
    // The walk from the ascent starts at the rounding of the current point.
    std::vector<WalkSlotPlan> plan(batch, WalkSlotPlan{static_cast<uint8_t>(SeedKind::Ascent), static_cast<uint8_t>(WalkRule::Skc), 0});
    WalkParameters walk;
    backend.begin_walk(plan, walk, 9);
    backend.walk(walk, violated);
    for (int slot = 0; slot < batch; ++slot) {
        const std::vector<float> point = backend.point(slot);
        const std::vector<int8_t> assignment = backend.walk_assignment(slot);
        for (int v = 0; v < formula.variable_count; ++v) CHECK(assignment[v] == (rounds_true(point[v]) ? 1 : -1));
        CHECK(count_violated(formula, assignment) == violated[slot]);
    }
}

TEST_CASE("rounded_assignment is the rounding of the counted point, on every backend") {
    auto planted = testing::planted_3sat(120, 4.1, 4);
    auto cpu = make_cpu_backend();
    check_counts_match_certificates(*cpu, planted.formula, 6);
    if (cuda_available()) {
        auto cuda = make_cuda_backend();
        check_counts_match_certificates(*cuda, planted.formula, 6);
    }
}

namespace {
class LyingBackend final : public Backend {
public:
    const char* name() const override { return "liar"; }
    void initialise(const Formula& formula, int, uint64_t) override { variables_ = formula.variable_count; }
    void restart_slots(const std::vector<int>&, uint64_t) override {}
    void iterate(const StepParameters&, int64_t, std::vector<int>& violated) override { violated.assign(1, 0); }
    std::vector<int8_t> rounded_assignment(int) const override { return std::vector<int8_t>(variables_, -1); }
    std::vector<float> point(int) const override { return std::vector<float>(variables_, -1.0f); }
    void begin_walk(const std::vector<WalkSlotPlan>&, const WalkParameters&, uint64_t) override {}
    void walk(const WalkParameters&, std::vector<int>& violated) override { violated.assign(1, 0); }
    std::vector<int8_t> walk_assignment(int) const override { return std::vector<int8_t>(variables_, -1); }
    void walk_flips_done(std::vector<int32_t>& flips) const override { flips.assign(1, 0); }
    void draw_tilted(const std::vector<float>&, int, uint64_t) override {}
    void anneal(const std::vector<float>&, const std::vector<float>&, int, int, uint64_t, std::vector<float>& log_weights,
                std::vector<int>& violated, std::vector<uint8_t>& found) override {
        log_weights.assign(1, 0.0f); violated.assign(1, 0); found.assign(1, 0);
    }
    void walk_assignments(std::vector<uint8_t>& assignments) const override { assignments.assign(variables_, 0); }
    std::vector<int8_t> saved_assignment(int) const override { return std::vector<int8_t>(variables_, -1); }
private:
    int variables_ = 0;
};
}  // namespace

TEST_CASE("a backend that reports a false zero count is rejected by the checker, in either phase") {
    Formula f = make_formula(2, {{1, 2}});     // all-false violates it
    LyingBackend liar;
    SolverConfiguration configuration;
    configuration.batch_size = 1;
    CHECK_THROWS(solve_with(f, configuration, liar));
    configuration.seed_kind = SeedKind::Uniform;
    configuration.polish_flips = 10;
    CHECK_THROWS(solve_with(f, configuration, liar));
    configuration.seed_kind = SeedKind::Tilted;
    configuration.tilted.tilted_groups = 1;
    CHECK_THROWS(solve_with(f, configuration, liar));
}
