"""Counts the failed restarts of a run, rigorous (Schöning tries) and heuristic (walks from the
loop's own draws), and turns them into the two UNSAT posteriors of posterior.py."""
from posterior import beta_mixture_posterior, rigorous_posterior


class FailureRecord:
    def __init__(self, num_variables, configuration):
        self.num_variables, self.configuration = num_variables, configuration
        self.rigorous_failures = self.heuristic_failures = 0

    def count(self, violated, rigorous_slot):
        """violated [B] after the walk, rigorous_slot [B] bool: every slot still violating a clause
        is one failed restart of its kind."""
        failed = violated > 0
        self.rigorous_failures += int((failed & rigorous_slot).sum())
        self.heuristic_failures += int((failed & ~rigorous_slot).sum())

    def posteriors(self):
        """(rigorous, Beta mixture) P(UNSAT | the failures so far)."""
        configuration = self.configuration
        return (rigorous_posterior(self.num_variables, self.rigorous_failures, configuration.prior_satisfiable),
                beta_mixture_posterior(self.heuristic_failures, configuration.beta_prior_a, configuration.beta_prior_b,
                                       configuration.prior_satisfiable))
