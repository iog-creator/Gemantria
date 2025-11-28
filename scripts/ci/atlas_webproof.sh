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
COMPLIANCE_SUMMARY_URL="http://127.0.0.1:8778/docs/atlas/dashboard/compliance_summary.html"
COMPLIANCE_TIMESERIES_URL="http://127.0.0.1:8778/docs/atlas/dashboard/compliance_timeseries.html"
COMPLIANCE_HEATMAP_URL="http://127.0.0.1:8778/docs/atlas/dashboard/compliance_heatmap.html"
VIOLATIONS_URL="http://127.0.0.1:8778/docs/atlas/browser/violations.html"
GUARD_RECEIPTS_URL="http://127.0.0.1:8778/docs/atlas/browser/guard_receipts.html"

ok_compliance_summary=0
ok_compliance_timeseries=0
ok_compliance_heatmap=0
ok_violations=0
ok_guard_receipts=0

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

# Screenshot compliance dashboards
shot "compliance_summary.png" "$COMPLIANCE_SUMMARY_URL"
summary_dom="$(dump "$COMPLIANCE_SUMMARY_URL")"
[[ -n "$summary_dom" ]] && ok_compliance_summary=1

shot "compliance_timeseries.png" "$COMPLIANCE_TIMESERIES_URL"
timeseries_dom="$(dump "$COMPLIANCE_TIMESERIES_URL")"
[[ -n "$timeseries_dom" ]] && ok_compliance_timeseries=1

shot "compliance_heatmap.png" "$COMPLIANCE_HEATMAP_URL"
heatmap_dom="$(dump "$COMPLIANCE_HEATMAP_URL")"
[[ -n "$heatmap_dom" ]] && ok_compliance_heatmap=1

shot "violations.png" "$VIOLATIONS_URL"
violations_dom="$(dump "$VIOLATIONS_URL")"
[[ -n "$violations_dom" ]] && ok_violations=1

shot "guard_receipts.png" "$GUARD_RECEIPTS_URL"
receipts_dom="$(dump "$GUARD_RECEIPTS_URL")"
[[ -n "$receipts_dom" ]] && ok_guard_receipts=1

ok=$(( ok_browser & ok_index & ok_catalog & ok_endpoints ))
jq -n --argjson ok "$ok" \
      --argjson ok_browser "$ok_browser" \
      --argjson ok_index "$ok_index" \
      --argjson ok_catalog "$ok_catalog" \
      --argjson ok_endpoints "$ok_endpoints" \
      --argjson ok_compliance_summary "$ok_compliance_summary" \
      --argjson ok_compliance_timeseries "$ok_compliance_timeseries" \
      --argjson ok_compliance_heatmap "$ok_compliance_heatmap" \
      --argjson ok_violations "$ok_violations" \
      --argjson ok_guard_receipts "$ok_guard_receipts" \
      --arg endpoints "$endpoints" \
      --arg index_png "evidence/webproof/index.png" \
      --arg catalog_png "evidence/webproof/catalog.png" \
      --arg compliance_summary_png "evidence/webproof/compliance_summary.png" \
      --arg compliance_timeseries_png "evidence/webproof/compliance_timeseries.png" \
      --arg compliance_heatmap_png "evidence/webproof/compliance_heatmap.png" \
      --arg violations_png "evidence/webproof/violations.png" \
      --arg guard_receipts_png "evidence/webproof/guard_receipts.png" \
      '{
         ok:($ok == 1),
         checks:{ 
           ok_browser:($ok_browser == 1), 
           ok_index:($ok_index == 1), 
           ok_catalog:($ok_catalog == 1), 
           ok_endpoints:($ok_endpoints == 1),
           ok_compliance_summary:($ok_compliance_summary == 1),
           ok_compliance_timeseries:($ok_compliance_timeseries == 1),
           ok_compliance_heatmap:($ok_compliance_heatmap == 1),
           ok_violations:($ok_violations == 1),
           ok_guard_receipts:($ok_guard_receipts == 1),
           endpoints_count:($endpoints|tonumber) 
         },
         screenshots:{ 
           index:$index_png, 
           catalog:$catalog_png,
           compliance_summary:$compliance_summary_png,
           compliance_timeseries:$compliance_timeseries_png,
           compliance_heatmap:$compliance_heatmap_png,
           violations:$violations_png,
           guard_receipts:$guard_receipts_png
         }
       }' | tee "$report_json" >/dev/null
popd >/dev/null

# Fail only if STRICT_WEBPROOF=1 and not ok
if [ "$strict" = "1" ] && ! jq -e '.ok' "$report_json" >/dev/null; then
  exit 1
fi

