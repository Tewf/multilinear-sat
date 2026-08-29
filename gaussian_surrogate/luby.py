"""The Luby restart sequence, and one restart budget per group counted in steps of the loop."""


def luby(index):
    """1, 1, 2, 1, 1, 2, 4, 1, 1, 2, 1, 1, 2, 4, 8, ... for index = 1, 2, 3, ... (Luby, Sinclair, Zuckerman 1993)."""
    power = 1
    while (1 << power) - 1 < index:
        power += 1
    if (1 << power) - 1 == index:
        return 1 << (power - 1)
    return luby(index - (1 << (power - 1)) + 1)


class LubyRestarts:
    """Group g starts at position 1 + g of the sequence so that the groups do not all restart on
    the same step; each then follows the sequence from there. advance() counts one step for every
    group and returns the groups whose budget is spent, moving them to their next budget."""

    def __init__(self, num_groups, unit_steps):
        self.unit_steps = unit_steps
        self.sequence_index = [1 + group for group in range(num_groups)]
        self.steps_in_restart = [0] * num_groups
        self.num_restarts = 0

    def budget(self, group):
        return luby(self.sequence_index[group]) * self.unit_steps

    def advance(self):
        restarted = []
        for group in range(len(self.sequence_index)):
            self.steps_in_restart[group] += 1
            if self.steps_in_restart[group] >= self.budget(group):
                self.steps_in_restart[group] = 0
                self.sequence_index[group] += 1
                restarted.append(group)
        self.num_restarts += len(restarted)
        return restarted
