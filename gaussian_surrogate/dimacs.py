"""Read a DIMACS CNF file into the tensors the solver works on. 3-SAT only."""
from dataclasses import dataclass

import torch


@dataclass
class Formula:
    num_variables: int
    clauses: torch.Tensor         # [m, 3] signed DIMACS literals, int64
    variable_index: torch.Tensor  # [m, 3] zero-based variable of each literal
    sign: torch.Tensor            # [m, 3] +1.0 or -1.0

    @property
    def num_clauses(self):
        return self.clauses.shape[0]

    def to(self, device):
        return Formula(self.num_variables, self.clauses.to(device),
                       self.variable_index.to(device), self.sign.to(device))


def formula_from_clauses(num_variables, clauses):
    """Build a Formula from a list (or tensor) of 3-literal clauses; rejects anything but 3-SAT."""
    clauses = torch.as_tensor(clauses, dtype=torch.int64)
    if clauses.ndim != 2 or clauses.shape[1] != 3:
        raise ValueError("3-SAT only: every clause must have exactly 3 literals")
    if (clauses == 0).any():
        raise ValueError("a literal is 0")
    variable_index = clauses.abs() - 1
    if int(variable_index.max()) >= num_variables:
        raise ValueError(f"a literal names variable {int(variable_index.max()) + 1} "
                         f"but the formula has {num_variables}")
    sorted_variables = variable_index.sort(dim=1).values
    if (sorted_variables[:, 1:] == sorted_variables[:, :-1]).any():
        raise ValueError("3-SAT only: a clause repeats a variable (duplicate or tautological literal)")
    return Formula(num_variables, clauses, variable_index, clauses.sign().to(torch.float32))


def read_dimacs(path):
    """Parse DIMACS: comment lines, one 'p cnf' header, clauses over any number of lines,
    and SATLIB's trailer (a '%' line followed by a lone 0) which ends the clause list."""
    num_variables = num_clauses = None
    tokens = []
    with open(path) as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("c"):
                continue
            if line.startswith("p"):
                fields = line.split()
                if len(fields) != 4 or fields[1] != "cnf":
                    raise ValueError(f"{path}: bad header {line!r}")
                num_variables, num_clauses = int(fields[2]), int(fields[3])
                continue
            if line.startswith("%"):
                break
            tokens.extend(int(token) for token in line.split())
    if num_variables is None:
        raise ValueError(f"{path}: no 'p cnf' header")
    clauses, current = [], []
    for token in tokens:
        if token == 0:
            clauses.append(current)
            current = []
        else:
            current.append(token)
    if current:
        raise ValueError(f"{path}: the last clause is not terminated by 0")
    if len(clauses) != num_clauses:
        raise ValueError(f"{path}: header announces {num_clauses} clauses, file has {len(clauses)}")
    lengths = {len(clause) for clause in clauses}
    if lengths != {3}:
        raise ValueError(f"{path}: 3-SAT only, found clause lengths {sorted(lengths)}")
    return formula_from_clauses(num_variables, clauses)
