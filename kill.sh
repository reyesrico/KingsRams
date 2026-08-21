#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
RUN_DIR="$ROOT_DIR/.run"

if [ -f "$RUN_DIR/team.pids" ]; then
    while IFS= read -r pid; do
        kill "$pid" 2>/dev/null || true
    done < "$RUN_DIR/team.pids"
    rm -f "$RUN_DIR/team.pids"
fi

if [ -f "$RUN_DIR/server.pid" ]; then
    kill "$(cat "$RUN_DIR/server.pid")" 2>/dev/null || true
    rm -f "$RUN_DIR/server.pid"
fi

printf 'Stopped KingsRams agents and local simulator.\n'