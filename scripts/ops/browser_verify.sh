#!/usr/bin/env bash
# Browser Verification Script (Rule-051 + Rule-067)
# Purpose: Standardized browser verification for visual/web artifacts
# Usage: bash scripts/ops/browser_verify.sh [--strict] [--port PORT] [--pages PAGE1,PAGE2]
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

STRICT="${STRICT_WEBPROOF:-0}"
PORT="${BROWSER_PORT:-8778}"
PAGES="${BROWSER_PAGES:-index.html,mcp_catalog_view.html}"
OUT_DIR="${BROWSER_OUT_DIR:-evidence/webproof}"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --strict) STRICT=1; shift ;;
        --port) PORT="$2"; shift 2 ;;
        --pages) PAGES="$2"; shift 2 ;;
        --out-dir) OUT_DIR="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

mkdir -p "$OUT_DIR"

# Start local HTTP server
echo "[browser_verify] Starting HTTP server on port $PORT..."
python3 -m http.server "$PORT" >/tmp/http_server_${PORT}.log 2>&1 & 
SERVER_PID=$!
echo "$SERVER_PID" > /tmp/http_server_${PORT}.pid

# Wait for server to be ready
for i in {1..30}; do
    if curl -fsS "http://127.0.0.1:${PORT}/" >/dev/null 2>&1; then
        echo "[browser_verify] ✓ Server ready"
        break
    fi
    sleep 0.2
done

# Cleanup function
cleanup() {
    if [ -f "/tmp/http_server_${PORT}.pid" ]; then
        PID=$(cat /tmp/http_server_${PORT}.pid)
        kill "$PID" 2>/dev/null || true
        rm -f /tmp/http_server_${PORT}.pid
        echo "[browser_verify] ✓ Server stopped"
    fi
}
trap cleanup EXIT

# Generate browser verification instructions for Cursor
echo "[browser_verify] Generating browser verification instructions..."
cat > "$OUT_DIR/browser_verify_instructions.txt" <<EOF
# Browser Verification Instructions (Rule-051 + Rule-067)
# Server running on port $PORT
# Execute these browser tool calls:

# For each page in: $PAGES
EOF

IFS=',' read -ra PAGE_ARRAY <<< "$PAGES"
for page in "${PAGE_ARRAY[@]}"; do
    page_clean=$(basename "$page" .html)
    url="http://127.0.0.1:${PORT}/docs/atlas/${page}?nocache=\$(date +%s)"
    echo "" >> "$OUT_DIR/browser_verify_instructions.txt"
    echo "# Page: $page" >> "$OUT_DIR/browser_verify_instructions.txt"
    echo "#   browser_navigate: $url" >> "$OUT_DIR/browser_verify_instructions.txt"
    echo "#   browser_wait_for: time=3" >> "$OUT_DIR/browser_verify_instructions.txt"
    echo "#   browser_snapshot" >> "$OUT_DIR/browser_verify_instructions.txt"
    echo "#   browser_take_screenshot: filename=$OUT_DIR/browser_verified_${page_clean}.png, fullPage=true" >> "$OUT_DIR/browser_verify_instructions.txt"
done

echo "" >> "$OUT_DIR/browser_verify_instructions.txt"
echo "# After browser verification, run:" >> "$OUT_DIR/browser_verify_instructions.txt"
echo "#   STRICT_WEBPROOF=$STRICT bash scripts/ci/atlas_webproof.sh" >> "$OUT_DIR/browser_verify_instructions.txt"

cat "$OUT_DIR/browser_verify_instructions.txt"

# Run headless webproof if available (non-blocking)
if command -v google-chrome >/dev/null 2>&1 || command -v chromium >/dev/null 2>&1; then
    echo "[browser_verify] Running headless webproof..."
    STRICT_WEBPROOF="$STRICT" bash scripts/ci/atlas_webproof.sh || {
        if [ "$STRICT" = "1" ]; then
            echo "[browser_verify] ✗ Webproof failed (STRICT mode)"
            exit 1
        else
            echo "[browser_verify] ⚠ Webproof failed (non-strict, continuing)"
        fi
    }
else
    echo "[browser_verify] ⚠ No headless browser found, skipping automated webproof"
    echo "[browser_verify] ⚠ Cursor must perform browser verification manually using instructions above"
fi

echo "[browser_verify] ✓ Browser verification setup complete"
echo "[browser_verify] Instructions saved to: $OUT_DIR/browser_verify_instructions.txt"
echo "[browser_verify] Server PID: $SERVER_PID (will auto-cleanup on exit)"

