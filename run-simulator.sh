#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
RUN_DIR="$ROOT_DIR/.run"

if [ ! -x "$ROOT_DIR/.venv/bin/rcssservermj" ]; then
    printf 'Simulator not installed. Run scripts/setup-macos.sh first.\n' >&2
    exit 1
fi

mkdir -p "$RUN_DIR"
cd "$RUN_DIR"
exec "$ROOT_DIR/.venv/bin/python" -m kingsrams.simulator \
    --host 127.0.0.1 \
    --aport 60000 \
    --mport 60001 \
    --rules ssim26 \
    --render \
    --sequential