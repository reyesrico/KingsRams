#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
RUN_DIR="$ROOT_DIR/.run"
HOST=${KINGRAMS_HOST:-127.0.0.1}
PORT=${KINGRAMS_PORT:-60000}
mkdir -p "$RUN_DIR"

if [ ! -x "$ROOT_DIR/.venv/bin/kingsrams-agent" ]; then
    printf 'Team not installed. Run scripts/setup-macos.sh first.\n' >&2
    exit 1
fi

if [ -f "$RUN_DIR/team.pids" ]; then
    while IFS= read -r pid; do
        if kill -0 "$pid" 2>/dev/null; then
            printf 'KingsRams agents are already running. Run ./kill.sh first.\n' >&2
            exit 1
        fi
    done < "$RUN_DIR/team.pids"
    rm -f "$RUN_DIR/team.pids"
fi

: > "$RUN_DIR/team.pids"
uniform_number=1
while [ "$uniform_number" -le 7 ]; do
    "$ROOT_DIR/.venv/bin/kingsrams-agent" \
        --host "$HOST" \
        --port "$PORT" \
        --uniform-number "$uniform_number" \
        >/dev/null 2>&1 &
    printf '%s\n' "$!" >> "$RUN_DIR/team.pids"
    uniform_number=$((uniform_number + 1))
done

printf 'Started 7 KingsRams agents.\n'