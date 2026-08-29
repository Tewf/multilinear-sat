"""The variants priced against each other, as data: every arm is the base configuration with
one factor changed (then the two-factor arms the one-factor results suggested), each a named
setting of the library's flags; the families, their budgets and the stage plan of the
brief. Nothing here runs; run_arms.py runs it and dominance.py reads the records."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INSTANCES = ROOT / "benchmark" / "instances"
RECORDS = Path(__file__).resolve().parent / "arms_results.jsonl"
BENCHMARK_RESULTS = ROOT / "benchmark" / "results.json"          # CaDiCaL's verdicts on the generated instances
SEED_COMPARISON = ROOT / "benchmark" / "seed_comparison.jsonl"   # the sampling-walk record that rejects the tilted seed

# Two expected times within this fraction of each other are not distinguished: the run-to-run
# variation of a timing on this chassis from thermal throttling alone. PROVISIONAL: the
# toolkit's measured 13 %, not re-measured here.
THERMAL_BAND = 0.13
PACKAGE_CELSIUS_LIMIT = 85          # no CUDA run starts above this package temperature
GPU_MEMORY_HELD_MIB = 6000          # above this, another process holds the card
SOLVER_CAP_SECONDS = 600            # the solver's own time limit per run; a run that hits it is recorded as capped

# The base arm and the factors. A one-factor arm is BASE with one key changed.
BASE = dict(seed="uniform", rule="probsat", batch=4096, schedule="luby", polish_per_variable=10, rigorous=0.0)
SEED_FLAGS = {
    "uniform": ["--seed-kind", "uniform"],
    "all_false": ["--seed-kind", "all-false"],
    "ascent_10": ["--seed-kind", "ascent", "--seed-steps", 10],
    "ascent_30": ["--seed-kind", "ascent", "--seed-steps", 30],
    "ascent_50": ["--seed-kind", "ascent", "--seed-steps", 50],
    "ascent_200": ["--seed-kind", "ascent", "--seed-steps", 200],
}
ARMS = {
    "base": {},
    "all_false": dict(seed="all_false"),
    "ascent_10": dict(seed="ascent_10"),
    "ascent_30": dict(seed="ascent_30"),
    "ascent_50": dict(seed="ascent_50"),
    "ascent_200": dict(seed="ascent_200"),
    "skc": dict(rule="skc"),
    "batch_16384": dict(batch=16384),
    "fixed_cutoff": dict(schedule="fixed"),
    "no_restart": dict(schedule="none"),
    "polish_5n": dict(polish_per_variable=5),
    "polish_20n": dict(polish_per_variable=20),
    "rigorous_half": dict(rigorous=0.5),
    # two-factor arms, added after the one-factor results (run_arms.py --stages two_factor)
    "batch_16384+polish_20n": dict(batch=16384, polish_per_variable=20),
    "skc+polish_20n": dict(rule="skc", polish_per_variable=20),
}
# The tilted seed is not an arm: on the sampling-walk records its expected time is 94x a
# uniform start's on the same uf250 runs, far outside the brief's 2x; dominance.py reads that
# record and lists it as rejected on it.

# One budget per family, in units of the arm's polish: 12 units is seven Luby runs
# (1, 1, 2, 1, 1, 2, 4), twelve fixed-cutoff runs, or one run of twelve units with no restart.
LUBY_RUNS_FOR_UNITS = {12: 7, 4: 3}
FAMILIES = {
    "uf50-218": dict(pattern="uf50-218/*.cnf", count=20, seeds=[0, 1], units=12, probsat_cap=60),
    "uf100-430": dict(pattern="uf100-430/*.cnf", count=20, seeds=[0, 1], units=12, probsat_cap=60),
    "uf250-1065": dict(pattern="uf250-1065/*.cnf", count=20, seeds=[0, 1], units=12, probsat_cap=60),
    "n1000-r4.20": dict(pattern="uf1000_r4.20_s*.cnf", count=5, seeds=[0, 1], units=12, probsat_cap=60),
    "n1000-r4.26": dict(pattern="uf1000_r4.26_s*.cnf", count=5, seeds=[0, 1], units=12, probsat_cap=60),
    "n5000-r4.20": dict(pattern="uf5000_r4.20_s*.cnf", count=5, seeds=[0, 1], units=4, probsat_cap=120),
    "n5000-r4.26": dict(pattern="uf5000_r4.26_s*.cnf", count=5, seeds=[0, 1], units=4, probsat_cap=120),
}
SMALL = ["uf50-218", "uf100-430", "uf250-1065"]
LARGE = ["n1000-r4.20", "n1000-r4.26", "n5000-r4.20", "n5000-r4.26"]
N1000 = ["n1000-r4.20", "n1000-r4.26"]

# The brief's order: (stage, arms, families). probSAT runs beside every family of the base stage.
STAGES = [
    ("base", ["base"], SMALL + LARGE),
    ("seeds", ["ascent_10", "ascent_30", "all_false", "ascent_50", "ascent_200"], ["uf250-1065"] + LARGE),
    ("rule_and_batch", ["skc", "batch_16384"], ["uf250-1065"] + N1000),
    ("schedule_and_polish", ["fixed_cutoff", "no_restart", "polish_5n", "polish_20n"], ["uf250-1065"]),
    ("rigorous", ["rigorous_half"], ["uf250-1065"]),
    ("two_factor", ["batch_16384+polish_20n", "skc+polish_20n"], ["uf250-1065"] + N1000),
]


def configuration(arm):
    return {**BASE, **ARMS[arm]}


def instances(family):
    return sorted(INSTANCES.glob(FAMILIES[family]["pattern"]))[:FAMILIES[family]["count"]]


def run_count_and_polish(arm, family, variable_count):
    """(run_limit, restart schedule flag, polish flips per slot per unit run) for the family's budget."""
    c = configuration(arm)
    units = FAMILIES[family]["units"]
    unit_flips = c["polish_per_variable"] * variable_count
    if c["schedule"] == "luby":
        return LUBY_RUNS_FOR_UNITS[units], "luby", unit_flips
    if c["schedule"] == "fixed":
        return units, "fixed", unit_flips
    return 1, "fixed", unit_flips * units        # no restart: the whole budget in one run


def flags(arm, family, variable_count, seed):
    c = configuration(arm)
    runs, schedule, polish_flips = run_count_and_polish(arm, family, variable_count)
    return (["--backend", "cuda", "--batch-size", c["batch"], "--seed", seed, "--run-limit", runs, "--restart-schedule", schedule,
             "--polish-flips", polish_flips, "--walk-rule", c["rule"], "--rigorous-fraction", c["rigorous"], "--verbose"]
            + SEED_FLAGS[c["seed"]])
