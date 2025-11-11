#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
OUT="$ROOT/evidence/webproof"
mkdir -p "$OUT"

# Find a headless Chromium/Chrome
BROWSER=""
for c in google-chrome chromium-browser chromium chrome; do
  if command -v "$c" >/dev/null 2>&1; then BROWSER="$c"; break; fi
done

strict="${STRICT_WEBPROOF:-0}"

# Start static server so JS fetches work (relative URLs)
pushd "$ROOT" >/dev/null
python3 -m http.server 8778 >/dev/null 2>&1 &
srv_pid=$!
trap "kill -9 $srv_pid >/dev/null 2>&1 || true" EXIT

# Wait for server
for i in {1..30}; do
  curl -sf "http://127.0.0.1:8778/docs/atlas/index.html" >/dev/null && break || sleep 0.2
done

report_json="$OUT/report.json"
ok_browser=0; ok_index=0; ok_catalog=0; ok_endpoints=0; endpoints=0
err=""

if [ -z "$BROWSER" ]; then
  err="no headless browser found"
  if [ "$strict" = "1" ]; then
    printf '{"ok":false,"error":"%s"}\n' "$err" | tee "$report_json"
    exit 1
  else
    printf '{"ok":false,"skipped":true,"reason":"%s"}\n' "$err" | tee "$report_json"
    exit 0
  fi
fi
ok_browser=1

# Screenshot + DOM dump helpers
shot() { "$BROWSER" --headless=new --disable-gpu --window-size=1280,800 --virtual-time-budget=4000 --screenshot="$OUT/$1" "$2" >/dev/null 2>&1 || true; }
dump() { "$BROWSER" --headless=new --disable-gpu --window-size=1280,800 --virtual-time-budget=4000 --dump-dom "$1" 2>/dev/null || true; }

INDEX_URL="http://127.0.0.1:8778/docs/atlas/index.html"
VIEW_URL="http://127.0.0.1:8778/docs/atlas/mcp_catalog_view.html"

shot "index.png" "$INDEX_URL"
index_dom="$(dump "$INDEX_URL")"
if [[ -n "$index_dom" ]]; then
  ok_index=1
  # Rule-067: Fail if Mermaid shows error banner (regression check)
  if echo "$index_dom" | grep -qi "Syntax error in text"; then
    echo "[webproof] ERROR: Mermaid syntax error detected in index page" >&2
    ok_index=0
  fi
fi

shot "catalog.png" "$VIEW_URL"
catalog_dom="$(dump "$VIEW_URL")"
if [[ -n "$catalog_dom" ]]; then
  ok_catalog=1
  # Verify rendered endpoint names from stub JSON (means JS ran + fetch worked)
  for k in "hybrid_search" "graph_neighbors" "lookup_ref"; do
    if echo "$catalog_dom" | grep -q "$k"; then endpoints=$((endpoints+1)); fi
  done
  [[ "$endpoints" -ge 3 ]] && ok_endpoints=1
fi

ok=$(( ok_browser & ok_index & ok_catalog & ok_endpoints ))
jq -n --argjson ok "$ok" \
      --argjson ok_browser "$ok_browser" \
      --argjson ok_index "$ok_index" \
      --argjson ok_catalog "$ok_catalog" \
      --argjson ok_endpoints "$ok_endpoints" \
      --arg endpoints "$endpoints" \
      --arg index_png "evidence/webproof/index.png" \
      --arg catalog_png "evidence/webproof/catalog.png" \
      '{
         ok:($ok == 1),
         checks:{ ok_browser:($ok_browser == 1), ok_index:($ok_index == 1), ok_catalog:($ok_catalog == 1), ok_endpoints:($ok_endpoints == 1), endpoints_count:($endpoints|tonumber) },
         screenshots:{ index:$index_png, catalog:$catalog_png }
       }' | tee "$report_json" >/dev/null
popd >/dev/null

# Fail only if STRICT_WEBPROOF=1 and not ok
if [ "$strict" = "1" ] && ! jq -e '.ok' "$report_json" >/dev/null; then
  exit 1
fi

