#!/usr/bin/env bash
# Three concurrent 3s pg_sleep calls per route. Each handler returns the order
# plus extra{thread, connection} (in the body), before the per-request timing.

set -euo pipefail

BASE="${BASE:-http://localhost:8000}"
ASYNC_URL="$BASE/orders/1/dispatch"
SYNC_URL="$BASE/orders/1/dispatch-sync"

# Ensure Order(id=1) exists. Idempotent (get_or_create on the server).
curl -fsS -o /dev/null -X POST "$BASE/orders/1"

# jq filter: input is "<json>\t<time>"; prints "  request N: 3.01s  thread=… conn=…".
FMT='
  split("\t") as $r | ($r[0] | fromjson) as $b |
  "  request \($n): \((($r[1] | tonumber) * 100 | round) / 100)s" +
  "  thread=\($b.extra.thread)  conn=\($b.extra.connection)"
'

run() {
    local url="$1"
    local label="$2"
    echo
    echo "=== $label ==="
    echo "POST $url  x3 in parallel"
    curl -fsS -X POST -w '\t%{time_total}' "$url" | jq -rR --arg n 1 "$FMT" &
    curl -fsS -X POST -w '\t%{time_total}' "$url" | jq -rR --arg n 2 "$FMT" &
    curl -fsS -X POST -w '\t%{time_total}' "$url" | jq -rR --arg n 3 "$FMT" &
    wait
}

run "$ASYNC_URL" "async route + sync_to_async (expect ~3s, ~6s, ~9s)"
run "$SYNC_URL"  "plain sync route (expect ~3s, ~3s, ~3s)"
