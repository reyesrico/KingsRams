#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT_DIR"

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install --constraint simulator/constraints.txt --editable .

printf 'KingsRams environment ready. Start the simulator with ./run-simulator.sh\n'