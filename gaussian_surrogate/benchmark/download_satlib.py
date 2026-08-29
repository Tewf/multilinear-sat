"""Fetch the SATLIB uniform random 3-SAT families (satisfiable uf, unsatisfiable uuf) into the
repository's ignored instances directory."""
import io
import tarfile
import urllib.request
from pathlib import Path

SATLIB_URL = "https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/{family}.tar.gz"
FAMILIES = ("uf20-91", "uf50-218", "uf100-430", "uf250-1065", "uuf250-1065")   # uuf: unsatisfiable twins
INSTANCES_DIRECTORY = Path(__file__).resolve().parents[2] / "benchmark" / "instances"


def download_family(family):
    """Extract every .cnf of the family flat into its own directory; skip a family already present."""
    target = INSTANCES_DIRECTORY / family
    if any(target.glob("*.cnf")):
        return len(list(target.glob("*.cnf"))), "already present"
    target.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(SATLIB_URL.format(family=family), timeout=120) as response:
        archive = tarfile.open(fileobj=io.BytesIO(response.read()), mode="r:gz")
    for member in archive.getmembers():
        if member.isfile() and member.name.endswith(".cnf"):
            member.name = Path(member.name).name
            archive.extract(member, target, filter="data")
    return len(list(target.glob("*.cnf"))), "downloaded"


if __name__ == "__main__":
    for family in FAMILIES:
        count, action = download_family(family)
        print(f"{family}: {count} .cnf files ({action}) in {INSTANCES_DIRECTORY / family}")
