#!/usr/bin/env bash
# Three async handlers each doing a 3s pg_sleep
#
# Compare with the sync route below: FastAPI runs sync routes on its own
# threadpool, so all three return in ~3s.

set -euo pipefail

BASE="${BASE:-http://localhost:8000}"
ASYNC_URL="$BASE/orders/1/dispatch"
SYNC_URL="$BASE/orders/1/dispatch-sync"

# Ensure Order(id=1) exists. Idempotent (get_or_create on the server).
curl -fsS -o /dev/null -X POST "$BASE/orders/1"

run() {
    local url="$1"
    local label="$2"
    echo
    echo "=== $label ==="
    echo "POST $url  x3 in parallel"
    curl -fsS -o /dev/null -X POST -w "  request 1: %{time_total}s\n" "$url" &
    curl -fsS -o /dev/null -X POST -w "  request 2: %{time_total}s\n" "$url" &
    curl -fsS -o /dev/null -X POST -w "  request 3: %{time_total}s\n" "$url" &
    wait
}

run "$ASYNC_URL" "async route + sync_to_async (expect ~3s, ~6s, ~9s)"
run "$SYNC_URL"  "plain sync route (expect ~3s, ~3s, ~3s)"
