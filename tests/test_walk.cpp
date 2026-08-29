// The walk: its bookkeeping against a recount from scratch, every rule's counts against
// the independent checker after k flips, reproducibility from the seed, and Schoening's
// walk of 3n flips on 20-variable, 91-clause instances (uf20-91's shape) at a success
// rate consistent across seeds.
#include <algorithm>

#include "backend.hpp"
#include "doctest.h"
#include "planted_instances.hpp"
#include "solver.hpp"
#include "walk_rules.hpp"

using namespace multilinear_sat;

namespace {
struct HostSlot {
    std::vector<uint8_t> assignment, true_count;
    std::vector<int32_t> list, position;
    int32_t count = 0;
    explicit HostSlot(const Formula& f)
        : assignment(f.variable_count, 0), true_count(f.clause_count(), 0), list(f.clause_count(), 0), position(f.clause_count(), 0) {}
    WalkSlot view() { return {assignment.data(), true_count.data(), list.data(), position.data(), &count}; }
    std::vector<int8_t> as_signs() const {
        std::vector<int8_t> signs(assignment.size());
        for (size_t v = 0; v < assignment.size(); ++v) signs[v] = assignment[v] ? 1 : -1;
        return signs;
    }
};

void check_against_recount(const Formula& f, const WalkFormula& wf, HostSlot& slot) {
    HostSlot fresh(f);
    fresh.assignment = slot.assignment;
    WalkSlot fresh_view = fresh.view();
    recount_slot(wf, fresh_view);
    CHECK(fresh.true_count == slot.true_count);
    CHECK(fresh.count == slot.count);
    std::vector<int32_t> a(slot.list.begin(), slot.list.begin() + slot.count), b(fresh.list.begin(), fresh.list.begin() + fresh.count);
    std::sort(a.begin(), a.end());
    std::sort(b.begin(), b.end());
    CHECK(a == b);
    for (int i = 0; i < slot.count; ++i) CHECK(slot.position[slot.list[i]] == i);
    CHECK(count_violated(f, slot.as_signs()) == slot.count);
}
}  // namespace

TEST_CASE("flip_variable keeps the counts and the violated list equal to a recount from scratch") {
    auto planted = testing::planted_3sat(60, 4.2, 5);
    const Formula& f = planted.formula;
    const WalkFormula wf = walk_formula_of(f);
    HostSlot slot(f);
    uint64_t state = 3;
    for (int v = 0; v < f.variable_count; ++v) slot.assignment[v] = testing::next_random(state) & 1;
    WalkSlot view = slot.view();
    recount_slot(wf, view);
    check_against_recount(f, wf, slot);
    for (int k = 1; k <= 400; ++k) {
        flip_variable(wf, view, static_cast<int>(testing::next_random(state) % f.variable_count));
        if (k % 20 == 0) check_against_recount(f, wf, slot);
    }
}

TEST_CASE("every rule's walk reports counts the checker confirms after k flips, from every start") {
    auto planted = testing::planted_3sat(100, 4.2, 6);
    const Formula& f = planted.formula;
    for (WalkRule rule : {WalkRule::Skc, WalkRule::ProbSat, WalkRule::Schoening, WalkRule::Metropolis}) {
        for (SeedKind start : {SeedKind::Uniform, SeedKind::AllFalse, SeedKind::Ascent}) {
            auto backend = make_cpu_backend();
            backend->initialise(f, 16, 11);
            std::vector<WalkSlotPlan> plan(16, WalkSlotPlan{static_cast<uint8_t>(start), static_cast<uint8_t>(rule), 300});
            WalkParameters walk;
            walk.walk_rule = rule;
            walk.walk_flips_per_launch = 37;
            backend->begin_walk(plan, walk, 1);
            std::vector<int> violated;
            std::vector<int32_t> flips;
            for (int launch = 0; launch < 9; ++launch) {
                backend->walk(walk, violated);
                for (int slot = 0; slot < 16; ++slot) CHECK(count_violated(f, backend->walk_assignment(slot)) == violated[slot]);
            }
            backend->walk_flips_done(flips);
            for (int slot = 0; slot < 16; ++slot) {
                CHECK(flips[slot] <= 300);
                if (violated[slot] > 0) CHECK(flips[slot] == 300);
            }
        }
    }
}

TEST_CASE("the walk is reproducible from its seed and differs across seeds") {
    auto planted = testing::planted_3sat(80, 4.2, 7);
    auto run = [&](uint64_t seed) {
        SolverConfiguration c;
        c.backend = BackendKind::Cpu;
        c.batch_size = 8;
        c.seed = seed;
        c.seed_kind = SeedKind::Uniform;
        c.polish_flips = 50;
        c.run_limit = 1;
        return solve(planted.formula, c);
    };
    const SolveResult a = run(3), b = run(3), c = run(4);
    CHECK(a.assignment == b.assignment);
    CHECK(a.best_violated == b.best_violated);
    CHECK(a.flips == b.flips);
    CHECK(a.assignment != c.assignment);
}

TEST_CASE("Schoening's walk of 3n flips finds solutions on 20-variable, 91-clause instances at a rate consistent across seeds") {
    for (uint64_t instance = 40; instance < 43; ++instance) {
        auto planted = testing::planted_3sat(20, 4.55, instance);
        REQUIRE(planted.formula.clause_count() == 91);
        std::vector<double> fractions;
        for (uint64_t seed = 0; seed < 4; ++seed) {
            SolverConfiguration c;
            c.backend = BackendKind::Cpu;
            c.batch_size = 2048;
            c.seed = seed;
            c.seed_kind = SeedKind::Uniform;
            c.walk.walk_rule = WalkRule::Schoening;
            c.polish_flips = 3 * 20;
            c.run_limit = 1;
            const SolveResult result = solve(planted.formula, c);
            CHECK(result.runs == 1);
            CHECK(result.flips <= 2048 * 60);
            fractions.push_back(static_cast<double>(result.polish_successes) / 2048.0);
        }
        const double lowest = *std::min_element(fractions.begin(), fractions.end());
        const double highest = *std::max_element(fractions.begin(), fractions.end());
        CHECK(lowest > 0.05);              // far above Schoening's worst-case bound of (3/4)^20 / 183
        CHECK(highest < 1.5 * lowest);     // 2048 tries per seed: the binomial spread is a few percent
    }
}
