"""The DIMACS reader on a SATLIB-style file, and what it rejects."""
import pytest

from dimacs import read_dimacs

SATLIB_TEXT = """c a comment line
c another one
p cnf 4 3
1 -2 3 0
-1 2
4 0
2 -3 -4 0
%
0

"""


def write_cnf(tmp_path, text):
    path = tmp_path / "formula.cnf"
    path.write_text(text)
    return path


def test_reads_the_satlib_layout(tmp_path):
    formula = read_dimacs(write_cnf(tmp_path, SATLIB_TEXT))
    assert (formula.num_variables, formula.num_clauses) == (4, 3)
    assert formula.clauses.tolist() == [[1, -2, 3], [-1, 2, 4], [2, -3, -4]]
    assert formula.variable_index.tolist() == [[0, 1, 2], [0, 1, 3], [1, 2, 3]]
    assert formula.sign.tolist() == [[1, -1, 1], [-1, 1, 1], [1, -1, -1]]


@pytest.mark.parametrize("text, message", [
    ("p cnf 3 1\n1 2 0\n", "3-SAT only"),
    ("p cnf 3 1\n1 -1 2 0\n", "repeats a variable"),
    ("p cnf 3 2\n1 2 3 0\n", "header announces"),
    ("1 2 3 0\n", "no 'p cnf' header"),
], ids=["two_literals", "duplicate_variable", "count_mismatch", "no_header"])
def test_rejects(tmp_path, text, message):
    with pytest.raises(ValueError, match=message):
        read_dimacs(write_cnf(tmp_path, text))
