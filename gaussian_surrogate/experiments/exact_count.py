"""Exact log P(all clauses satisfied) under the product measure, and its gradient in p, from
one SDD compilation per formula (PySDD): the fidelity experiment's ground truth. The plan named
Ganak first; a compiled circuit gives the same weighted count at every trajectory point from a
single compilation, and the exact gradient without 2n counter calls."""
import math

from pysdd.sdd import SddManager

CORNER_CLAMP = 1.0 - 1e-9   # the box relaxation reaches exact +-1, where one literal weight is 0


class ExactCounter:
    """Compile once, then evaluate log P and d log P / d p at any point of [-1, 1]^n.

    Every node held across an apply is ref'd first: with auto_gc_and_minimize the manager may
    collect unreferenced nodes during any operation, which silently leaves a wrong circuit."""

    def __init__(self, formula):
        self.num_variables = formula.num_variables
        self.manager = SddManager(var_count=formula.num_variables, auto_gc_and_minimize=True)
        root = self.manager.true()
        root.ref()
        for clause in formula.clauses.tolist():
            disjunction = self.manager.false()
            disjunction.ref()
            for literal in clause:
                extended = disjunction | self.manager.literal(literal)
                extended.ref()
                disjunction.deref()
                disjunction = extended
            conjoined = root & disjunction
            conjoined.ref()
            root.deref()
            disjunction.deref()
            root = conjoined
        self.root = root
        self._check_against_own_model()

    def _check_against_own_model(self):
        """At p = CHECK_SCALE * (a model of the circuit), P(sat) >= P(x = model), so log P must
        land in [n log((1 + CHECK_SCALE) / 2), 0]: a compilation the garbage collector damaged
        fails this immediately."""
        scale = 0.999
        model = next(self.root.models())
        point = [scale if model.get(index + 1, 1) else -scale for index in range(self.num_variables)]
        log_probability, _ = self.log_probability_and_gradient(point)
        floor = self.num_variables * math.log((1.0 + scale) / 2.0)
        if not floor - 1e-9 <= log_probability <= 1e-9:
            raise RuntimeError(f"self-check failed: log P = {log_probability} outside [{floor}, 0]")

    @property
    def node_count(self):
        return self.root.count()

    def log_probability_and_gradient(self, p):
        """(log P, gradient list [n]) at p; d log P / d p_i = (P(x_i=1|sat)/w_i+ - P(x_i=0|sat)/w_i-) / 2,
        from W = w_i+ A + w_i- B with A, B free of p_i and dw_i+-/dp_i = +-1/2."""
        wmc = self.root.wmc(log_mode=True)
        weights = []
        for index in range(self.num_variables):
            value = min(max(float(p[index]), -CORNER_CLAMP), CORNER_CLAMP)
            positive, negative = (1.0 + value) / 2.0, (1.0 - value) / 2.0
            weights.append((positive, negative))
            wmc.set_literal_weight(self.manager.literal(index + 1), math.log(positive))
            wmc.set_literal_weight(self.manager.literal(-(index + 1)), math.log(negative))
        log_probability = wmc.propagate()
        gradient = []
        for index, (positive, negative) in enumerate(weights):
            marginal_positive = math.exp(wmc.literal_pr(self.manager.literal(index + 1)))
            marginal_negative = math.exp(wmc.literal_pr(self.manager.literal(-(index + 1))))
            gradient.append(0.5 * (marginal_positive / positive - marginal_negative / negative))
        return log_probability, gradient
