"""Uniform random 3-SAT instances in DIMACS form, reproducible from (n, ratio, seed).

Each clause draws 3 distinct variables and negates each independently with
probability 1/2, the standard uniform model. Satisfiability is decided later by the
CDCL baseline, not planted, so the instances are the ones the literature measures on.

Usage: python generate_instances.py --out instances --n 200 1000 --ratios 4.0 4.2 4.26 --seeds 5
"""
import argparse
import os
import random


def random_3sat(n_vars, ratio, seed):
    rng = random.Random(seed * 1000003 + n_vars * 31 + int(ratio * 100))
    m = round(ratio * n_vars)
    clauses = []
    for _ in range(m):
        variables = rng.sample(range(1, n_vars + 1), 3)
        clauses.append([v if rng.random() < 0.5 else -v for v in variables])
    return clauses


def write_dimacs(path, n_vars, clauses, comment):
    with open(path, "w") as f:
        f.write(f"c {comment}\n")
        f.write(f"p cnf {n_vars} {len(clauses)}\n")
        for clause in clauses:
            f.write(" ".join(str(l) for l in clause) + " 0\n")


def instance_name(n_vars, ratio, seed):
    return f"uf{n_vars}_r{ratio:.2f}_s{seed}.cnf"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default="instances")
    parser.add_argument("--n", type=int, nargs="+", default=[200, 1000, 5000])
    parser.add_argument("--ratios", type=float, nargs="+", default=[4.0, 4.2, 4.26])
    parser.add_argument("--seeds", type=int, default=5)
    args = parser.parse_args()
    os.makedirs(args.out, exist_ok=True)
    count = 0
    for n_vars in args.n:
        for ratio in args.ratios:
            for seed in range(args.seeds):
                path = os.path.join(args.out, instance_name(n_vars, ratio, seed))
                write_dimacs(path, n_vars, random_3sat(n_vars, ratio, seed),
                             f"uniform random 3-SAT n={n_vars} ratio={ratio} seed={seed}")
                count += 1
    print(f"wrote {count} instances to {args.out}")


if __name__ == "__main__":
    main()
