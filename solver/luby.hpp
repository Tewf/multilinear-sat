// The Luby, Sinclair, Zuckerman (1993) universal restart sequence, indexed from 1:
// 1, 1, 2, 1, 1, 2, 4, 1, 1, 2, 1, 1, 2, 4, 8, ...
// luby(2^k - 1) = 2^{k-1}; otherwise luby(i) = luby(i - 2^{k-1} + 1) for 2^{k-1} <= i < 2^k - 1.
#pragma once
#include <cstdint>

namespace multilinear_sat {

inline int64_t luby(int64_t index) {
    for (;;) {
        int64_t power = 1;
        while (power - 1 < index) power *= 2;
        if (power - 1 == index) return power / 2;
        index -= power / 2 - 1;
    }
}

}  // namespace multilinear_sat
