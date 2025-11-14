#!/usr/bin/env bash
# Ensure MCP SSE server is running (auto-start if enabled)
# Purpose: Check if MCP SSE server is running, start it if AUTO_START_MCP_SSE=1
# Usage: ./scripts/mcp_sse_ensure.sh [--force]
#   --force: Start server even if AUTO_START_MCP_SSE is not set

set -euo pipefail

ROOT="${GEMANTRIA_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$ROOT"

MCP_HOST="${MCP_HOST:-127.0.0.1}"
MCP_PORT="${MCP_PORT:-8005}"
AUTO_START="${AUTO_START_MCP_SSE:-0}"
FORCE_START=false

if [ "${1:-}" = "--force" ]; then
    FORCE_START=true
fi

# Check if server is already running
check_server() {
    if command -v lsof >/dev/null 2>&1; then
        lsof -i ":${MCP_PORT}" >/dev/null 2>&1
    else
        # Fallback: try to connect
        timeout 1 bash -c "echo >/dev/tcp/${MCP_HOST}/${MCP_PORT}" 2>/dev/null || return 1
    fi
}

# Start the server
start_server() {
    local script_path="$HOME/mcp/gemantria-ops/run_server_sse.sh"
    
    if [ ! -f "$script_path" ]; then
        echo "[mcp-sse] ERROR: Server script not found at $script_path" >&2
        return 1
    fi
    
    echo "[mcp-sse] Starting server on ${MCP_HOST}:${MCP_PORT}..."
    nohup bash "$script_path" >/tmp/mcp_sse.log 2>&1 &
    local pid=$!
    
    # Wait a moment for server to start
    sleep 2
    
    # Verify it started
    if check_server; then
        echo "[mcp-sse] ✓ Server started (PID: $pid)"
        return 0
    else
        echo "[mcp-sse] ✗ Server failed to start (check /tmp/mcp_sse.log)" >&2
        return 1
    fi
}

# Main logic
if check_server; then
    echo "[mcp-sse] ✓ Server already running on ${MCP_HOST}:${MCP_PORT}"
    exit 0
fi

# Server is not running
if [ "$FORCE_START" = "true" ] || [ "$AUTO_START" = "1" ]; then
    start_server
    exit $?
else
    echo "[mcp-sse] ⚠ Server not running (set AUTO_START_MCP_SSE=1 to auto-start)"
    exit 0
fi




