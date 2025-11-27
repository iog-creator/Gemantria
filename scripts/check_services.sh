#!/usr/bin/env bash
# Service Status Check - ALWAYS RUN BEFORE TROUBLESHOOTING
# Purpose: Verify all required services are running before debugging
# Rule 062: Environment Validation (Always Required)

set -euo pipefail

REPO_ROOT="${GEMANTRIA_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$REPO_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
ALL_OK=true

echo "🔍 Service Status Check"
echo "======================"
echo ""

# 1. Check .venv FIRST (most common issue)
echo "1. Virtual Environment (.venv)"
echo "   ----------------------------"
if [ -z "${VIRTUAL_ENV:-}" ]; then
    echo -e "   ${RED}✗ NOT ACTIVATED${NC}"
    echo "   ACTION: source .venv/bin/activate"
    ALL_OK=false
elif [ "${VIRTUAL_ENV}" != "$REPO_ROOT/.venv" ]; then
    echo -e "   ${RED}✗ WRONG VENV${NC}"
    echo "   Current: $VIRTUAL_ENV"
    echo "   Expected: $REPO_ROOT/.venv"
    echo "   ACTION: source .venv/bin/activate"
    ALL_OK=false
else
    echo -e "   ${GREEN}✓ Activated${NC}"
    echo "   Path: $VIRTUAL_ENV"
fi
echo ""

# 2. Check API Server (port 8000)
echo "2. API Server (port 8000)"
echo "   -----------------------"
if command -v lsof >/dev/null 2>&1; then
    if lsof -i :8000 >/dev/null 2>&1; then
        PID=$(lsof -ti :8000 | head -1)
        echo -e "   ${GREEN}✓ Running${NC} (PID: $PID)"
    else
        echo -e "   ${RED}✗ NOT RUNNING${NC}"
        echo "   ACTION: python3 -m uvicorn src.services.api_server:app --host 0.0.0.0 --port 8000 --reload"
        ALL_OK=false
    fi
else
    # Fallback: try to connect
    if timeout 1 bash -c "echo >/dev/tcp/127.0.0.1/8000" 2>/dev/null; then
        echo -e "   ${GREEN}✓ Running${NC}"
    else
        echo -e "   ${RED}✗ NOT RUNNING${NC}"
        echo "   ACTION: python3 -m uvicorn src.services.api_server:app --host 0.0.0.0 --port 8000 --reload"
        ALL_OK=false
    fi
fi
echo ""

# 3. Check Vite Dev Server (port 5173)
echo "3. Vite Dev Server (port 5173)"
echo "   ----------------------------"
if command -v lsof >/dev/null 2>&1; then
    if lsof -i :5173 >/dev/null 2>&1; then
        PID=$(lsof -ti :5173 | head -1)
        echo -e "   ${GREEN}✓ Running${NC} (PID: $PID)"
        # Check which directory it's running from
        if ps -p "$PID" -o cmd= 2>/dev/null | grep -q "ui/"; then
            echo "   Location: ui/"
        elif ps -p "$PID" -o cmd= 2>/dev/null | grep -q "webui/graph/"; then
            echo "   Location: webui/graph/"
        fi
    else
        echo -e "   ${RED}✗ NOT RUNNING${NC}"
        echo "   ACTION: cd ui && npm run dev"
        ALL_OK=false
    fi
else
    # Fallback: try to connect
    if timeout 1 bash -c "echo >/dev/tcp/127.0.0.1/5173" 2>/dev/null; then
        echo -e "   ${GREEN}✓ Running${NC}"
    else
        echo -e "   ${RED}✗ NOT RUNNING${NC}"
        echo "   ACTION: cd ui && npm run dev"
        ALL_OK=false
    fi
fi
echo ""

# 4. Check Database (optional - only if DB operations needed)
echo "4. Database Connection (PostgreSQL)"
echo "   ---------------------------------"
if [ -n "${GEMATRIA_DSN:-}" ] || [ -n "${BIBLE_DB_DSN:-}" ]; then
    # Try to connect (non-blocking check)
    if command -v psql >/dev/null 2>&1; then
        if timeout 2 psql "$GEMATRIA_DSN" -c "SELECT 1;" >/dev/null 2>&1; then
            echo -e "   ${GREEN}✓ Connected${NC}"
        else
            echo -e "   ${YELLOW}⚠ Connection failed${NC}"
            echo "   (May be expected in CI/hermetic mode)"
        fi
    else
        echo -e "   ${YELLOW}⚠ psql not available${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠ DSN not set${NC}"
    echo "   (May be expected in CI/hermetic mode)"
fi
echo ""

# Summary
echo "======================"
if [ "$ALL_OK" = true ]; then
    echo -e "${GREEN}✓ All critical services running${NC}"
    exit 0
else
    echo -e "${RED}✗ Some services are not running${NC}"
    echo ""
    echo "Quick Start Commands:"
    echo "  # Activate venv"
    echo "  source .venv/bin/activate"
    echo ""
    echo "  # Start API server (in background)"
    echo "  python3 -m uvicorn src.services.api_server:app --host 0.0.0.0 --port 8000 --reload &"
    echo ""
    echo "  # Start Vite dev server (in background)"
    echo "  cd ui && npm run dev &"
    echo ""
    exit 1
fi

