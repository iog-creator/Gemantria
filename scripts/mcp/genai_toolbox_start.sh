#!/bin/bash
# Start script for MCP Toolbox server
# This script starts the genai-toolbox MCP server for database access

set -e

TOOLBOX_DIR="${HOME}/mcp/genai-toolbox"
TOOLS_FILE="${TOOLBOX_DIR}/tools.yaml"
PORT="${GENAI_TOOLBOX_PORT:-5000}"
ADDRESS="${GENAI_TOOLBOX_ADDRESS:-127.0.0.1}"
LOG_LEVEL="${GENAI_TOOLBOX_LOG_LEVEL:-info}"
PID_FILE="/tmp/genai-toolbox.pid"
LOG_FILE="/tmp/genai-toolbox.log"

# Check if toolbox binary exists
if [ ! -f "${TOOLBOX_DIR}/toolbox" ]; then
    echo "Error: toolbox binary not found at ${TOOLBOX_DIR}/toolbox"
    echo "Please install genai-toolbox first"
    exit 1
fi

# Check if tools.yaml exists
if [ ! -f "${TOOLS_FILE}" ]; then
    echo "Error: tools.yaml not found at ${TOOLS_FILE}"
    exit 1
fi

# Stop existing server if running
if [ -f "${PID_FILE}" ]; then
    OLD_PID=$(cat "${PID_FILE}")
    if ps -p "${OLD_PID}" > /dev/null 2>&1; then
        echo "Stopping existing server (PID: ${OLD_PID})..."
        kill "${OLD_PID}" 2>/dev/null || true
        sleep 1
    fi
    rm -f "${PID_FILE}"
fi

# Start the server
echo "Starting MCP Toolbox server..."
echo "  Address: ${ADDRESS}"
echo "  Port: ${PORT}"
echo "  Tools file: ${TOOLS_FILE}"
echo "  Log file: ${LOG_FILE}"

cd "${TOOLBOX_DIR}"
PGHOST=/var/run/postgresql ./toolbox \
    --tools-file "${TOOLS_FILE}" \
    --port "${PORT}" \
    --address "${ADDRESS}" \
    --log-level "${LOG_LEVEL}" \
    > "${LOG_FILE}" 2>&1 &

SERVER_PID=$!
echo "${SERVER_PID}" > "${PID_FILE}"

# Wait a moment for server to start
sleep 2

# Check if server is still running
if ps -p "${SERVER_PID}" > /dev/null 2>&1; then
    echo "✓ Server started successfully (PID: ${SERVER_PID})"
    echo "  Health check: http://${ADDRESS}:${PORT}/health"
    echo "  MCP endpoint: http://${ADDRESS}:${PORT}/mcp"
    echo "  Logs: ${LOG_FILE}"
else
    echo "✗ Server failed to start. Check logs: ${LOG_FILE}"
    tail -20 "${LOG_FILE}"
    exit 1
fi

