#!/usr/bin/env bash
# API Server Process Manager with Auto-Restart
# Purpose: Keep API server running with automatic restart on failure

set -euo pipefail

REPO_ROOT="${GEMANTRIA_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$REPO_ROOT"

API_PORT="${API_PORT:-8000}"
API_HOST="${API_HOST:-0.0.0.0}"
LOG_DIR="${LOG_DIR:-$REPO_ROOT/logs}"
PID_FILE="${PID_FILE:-$REPO_ROOT/.api_server.pid}"
MAX_RESTARTS=10
RESTART_DELAY=2

mkdir -p "$LOG_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_DIR/api_server_manager.log"
}

check_server() {
    if timeout 2 bash -c "echo >/dev/tcp/127.0.0.1/$API_PORT" 2>/dev/null; then
        return 0
    fi
    return 1
}

start_server() {
    log "Starting API server on $API_HOST:$API_PORT..."
    
    # Ensure venv is activated
    if [ -z "${VIRTUAL_ENV:-}" ]; then
        log "${RED}ERROR: Virtual environment not activated${NC}"
        log "Run: source .venv/bin/activate"
        return 1
    fi
    
    # Start server in background
    nohup python3 -m uvicorn src.services.api_server:app \
        --host "$API_HOST" \
        --port "$API_PORT" \
        --log-level info \
        >> "$LOG_DIR/api_server.log" 2>&1 &
    
    local pid=$!
    echo $pid > "$PID_FILE"
    
    # Wait for server to be ready
    local wait_count=0
    while [ $wait_count -lt 10 ]; do
        if check_server; then
            log "${GREEN}✓ API server started (PID: $pid)${NC}"
            return 0
        fi
        sleep 1
        wait_count=$((wait_count + 1))
    done
    
    log "${RED}✗ API server failed to start${NC}"
    return 1
}

stop_server() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            log "Stopping API server (PID: $pid)..."
            kill "$pid" 2>/dev/null || true
            sleep 1
            kill -9 "$pid" 2>/dev/null || true
        fi
        rm -f "$PID_FILE"
    fi
    
    # Also kill any uvicorn processes on the port
    if command -v lsof >/dev/null 2>&1; then
        lsof -ti :$API_PORT | xargs kill -9 2>/dev/null || true
    fi
}

restart_server() {
    log "Restarting API server..."
    stop_server
    sleep "$RESTART_DELAY"
    start_server
}

status_server() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            if check_server; then
                echo "${GREEN}✓ Running${NC} (PID: $pid)"
                return 0
            else
                echo "${YELLOW}⚠ Process exists but not responding${NC} (PID: $pid)"
                return 1
            fi
        else
            echo "${RED}✗ Not running${NC} (stale PID file)"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        if check_server; then
            echo "${YELLOW}⚠ Running but no PID file${NC}"
            return 0
        else
            echo "${RED}✗ Not running${NC}"
            return 1
        fi
    fi
}

watch_server() {
    log "Starting API server watcher (auto-restart enabled)..."
    local restart_count=0
    
    while true; do
        if ! check_server; then
            restart_count=$((restart_count + 1))
            
            if [ $restart_count -gt $MAX_RESTARTS ]; then
                log "${RED}ERROR: Max restarts ($MAX_RESTARTS) reached. Stopping watcher.${NC}"
                exit 1
            fi
            
            log "${YELLOW}Server down, restarting... (attempt $restart_count/$MAX_RESTARTS)${NC}"
            start_server || {
                log "${RED}Failed to restart server${NC}"
                sleep "$RESTART_DELAY"
                continue
            }
            
            # Reset counter on successful start
            restart_count=0
        else
            # Server is healthy, reset counter
            if [ $restart_count -gt 0 ]; then
                log "${GREEN}Server recovered${NC}"
                restart_count=0
            fi
        fi
        
        sleep 5
    done
}

case "${1:-}" in
    start)
        if check_server; then
            log "${YELLOW}Server already running${NC}"
            exit 0
        fi
        start_server
        ;;
    stop)
        stop_server
        log "${GREEN}Server stopped${NC}"
        ;;
    restart)
        restart_server
        ;;
    status)
        status_server
        ;;
    watch)
        watch_server
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|watch}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the API server"
        echo "  stop    - Stop the API server"
        echo "  restart - Restart the API server"
        echo "  status  - Check server status"
        echo "  watch   - Start watcher with auto-restart"
        exit 1
        ;;
esac

