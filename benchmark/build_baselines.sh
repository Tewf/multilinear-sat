#!/usr/bin/env bash
# Clones and builds the two baseline solvers into benchmark/third_party/ (git-ignored)
# and records their commit hashes into benchmark/third_party/versions.txt.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THIRD_PARTY="$HERE/third_party"
mkdir -p "$THIRD_PARTY"
VERSIONS_FILE="$THIRD_PARTY/versions.txt"
: > "$VERSIONS_FILE"

echo "==> probSAT"
if [ ! -d "$THIRD_PARTY/probSAT" ]; then
    git clone https://github.com/adrianopolus/probSAT "$THIRD_PARTY/probSAT"
fi
(
    cd "$THIRD_PARTY/probSAT"
    make
)
PROBSAT_COMMIT=$(git -C "$THIRD_PARTY/probSAT" rev-parse HEAD)
echo "probSAT $PROBSAT_COMMIT" >> "$VERSIONS_FILE"

echo "==> CaDiCaL"
if [ ! -d "$THIRD_PARTY/cadical" ]; then
    git clone https://github.com/arminbiere/cadical "$THIRD_PARTY/cadical"
fi
(
    cd "$THIRD_PARTY/cadical"
    ./configure
    make -j"$(nproc)"
)
CADICAL_COMMIT=$(git -C "$THIRD_PARTY/cadical" rev-parse HEAD)
echo "cadical $CADICAL_COMMIT" >> "$VERSIONS_FILE"

echo "==> done"
cat "$VERSIONS_FILE"
echo "probSAT binary:  $THIRD_PARTY/probSAT/probSAT"
echo "cadical binary:  $THIRD_PARTY/cadical/build/cadical"
