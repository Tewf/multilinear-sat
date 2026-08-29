// The walk's per-slot state and the operations that keep it current, shared by the CPU
// loops and the CUDA kernels: an assignment, the true-literal count of every row, and the
// violated rows as a list with each row's position in it (probSAT's falseClause and
// whereFalse), so a violated row is drawn in O(1) and a flip updates the list in O(1) per
// row it touches. A clause is violated with no true literal, an odd parity with an even
// number of them; a flip of a variable toggles every parity it occurs in.
#pragma once
#include <cstdint>

#include "device_inline.hpp"
#include "energy_math.hpp"
#include "random_hash.hpp"

namespace multilinear_sat {

// The formula as raw pointers, on the host or on the device.
struct WalkFormula {
    const int32_t* literals;
    const int32_t* clause_offsets;
    const uint8_t* clause_is_parity;
    const int32_t* occurrence_offsets;
    const int32_t* occurrence_clauses;
    const int32_t* occurrence_literals;
    int variable_count;
    int clause_count;
};

// The whole batch's walk arrays, slot-major.
struct WalkArrays {
    uint8_t* assignment;         // batch x variables, 1 = true
    uint8_t* true_count;         // batch x rows
    int32_t* violated_list;      // batch x rows
    int32_t* violated_position;  // batch x rows
    int32_t* violated_count;     // batch
    int32_t* flips_done;         // batch: steps taken since begin_walk
};

// One slot's view of them.
struct WalkSlot {
    uint8_t* assignment;
    uint8_t* true_count;
    int32_t* violated_list;
    int32_t* violated_position;
    int32_t* violated_count;
};

// What the solver loop asks of each slot's walk: where it starts (a SeedKind), which
// rule it flips by (a WalkRule), and how many steps it may take.
struct WalkSlotPlan {
    uint8_t start;
    uint8_t rule;
    int32_t budget;
};

MULTILINEAR_SAT_INLINE WalkSlot slot_view(const WalkArrays& arrays, int slot, int variable_count, int clause_count) {
    const size_t variables = static_cast<size_t>(slot) * variable_count, rows = static_cast<size_t>(slot) * clause_count;
    return {arrays.assignment + variables, arrays.true_count + rows, arrays.violated_list + rows,
            arrays.violated_position + rows, arrays.violated_count + slot};
}

MULTILINEAR_SAT_INLINE bool literal_true(const uint8_t* assignment, int32_t literal) {
    return (assignment[variable_of(literal)] != 0) == (literal > 0);
}

MULTILINEAR_SAT_INLINE bool violated_by_count(bool is_parity, int true_count) {
    return is_parity ? (true_count & 1) == 0 : true_count == 0;
}

MULTILINEAR_SAT_INLINE void add_violated(WalkSlot& slot, int row) {
    slot.violated_position[row] = *slot.violated_count;
    slot.violated_list[(*slot.violated_count)++] = row;
}

MULTILINEAR_SAT_INLINE void remove_violated(WalkSlot& slot, int row) {
    const int position = slot.violated_position[row];
    const int last = slot.violated_list[--(*slot.violated_count)];
    slot.violated_list[position] = last;
    slot.violated_position[last] = position;
}

// The start of a walk: the rounding of the slot's continuous point (SeedKind::Ascent, 2),
// the rounding of a fresh restart-stream point (Uniform, 0), all false (AllFalse, 1), or the
// assignment already in the slot, the tilted seed's last draw (Tilted, 3).
MULTILINEAR_SAT_INLINE void set_walk_start(const WalkFormula& formula, WalkSlot& slot, uint8_t start, const float* point,
                                           uint64_t seed, uint64_t epoch, int slot_index) {
    if (start == 3) return;
    for (int v = 0; v < formula.variable_count; ++v) {
        bool value = false;
        if (start == 2) value = rounds_true(point[v]);
        else if (start == 0) value = rounds_true(2.0f * uniform_random(seed, epoch, static_cast<uint64_t>(slot_index), static_cast<uint64_t>(v)) - 1.0f);
        slot.assignment[v] = value ? 1 : 0;
    }
}

// Counts and the violated list from scratch, for a freshly set assignment.
MULTILINEAR_SAT_INLINE void recount_slot(const WalkFormula& formula, WalkSlot& slot) {
    *slot.violated_count = 0;
    for (int row = 0; row < formula.clause_count; ++row) {
        int count = 0;
        for (int p = formula.clause_offsets[row]; p < formula.clause_offsets[row + 1]; ++p) count += literal_true(slot.assignment, formula.literals[p]);
        slot.true_count[row] = static_cast<uint8_t>(count);
        if (violated_by_count(formula.clause_is_parity[row] != 0, count)) add_violated(slot, row);
    }
}

// The rows a flip of the variable would satisfy (make) and violate (break): a clause
// makes when it has no true literal and breaks when this literal is its only true one; a
// parity makes when violated and breaks when satisfied.
MULTILINEAR_SAT_INLINE void flip_effect(const WalkFormula& formula, const WalkSlot& slot, int variable, int& make, int& breaks) {
    make = 0;
    breaks = 0;
    for (int o = formula.occurrence_offsets[variable]; o < formula.occurrence_offsets[variable + 1]; ++o) {
        const int row = formula.occurrence_clauses[o];
        const int count = slot.true_count[row];
        if (formula.clause_is_parity[row]) {
            const bool violated = (count & 1) == 0;
            make += violated;
            breaks += !violated;
        } else {
            make += (count == 0);
            breaks += (count == 1 && literal_true(slot.assignment, formula.occurrence_literals[o]));
        }
    }
}

MULTILINEAR_SAT_INLINE int break_count(const WalkFormula& formula, const WalkSlot& slot, int variable) {
    int make = 0, breaks = 0;
    flip_effect(formula, slot, variable, make, breaks);
    return breaks;
}

// Flips the variable and brings the counts and the violated list up to date.
MULTILINEAR_SAT_INLINE void flip_variable(const WalkFormula& formula, WalkSlot& slot, int variable) {
    slot.assignment[variable] ^= 1;
    for (int o = formula.occurrence_offsets[variable]; o < formula.occurrence_offsets[variable + 1]; ++o) {
        const int row = formula.occurrence_clauses[o];
        const bool is_parity = formula.clause_is_parity[row] != 0;
        const int before = slot.true_count[row];
        const int after = before + (literal_true(slot.assignment, formula.occurrence_literals[o]) ? 1 : -1);
        slot.true_count[row] = static_cast<uint8_t>(after);
        const bool was = violated_by_count(is_parity, before), now = violated_by_count(is_parity, after);
        if (now && !was) add_violated(slot, row);
        else if (was && !now) remove_violated(slot, row);
    }
}

}  // namespace multilinear_sat
