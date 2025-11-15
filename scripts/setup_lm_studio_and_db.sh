#!/bin/bash
# Setup script for LM Studio and Database configuration
# This script helps configure and verify LM Studio and Postgres setup

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

echo "🔧 Gemantria LM Studio & Database Setup"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from env_example.txt..."
    cp env_example.txt .env
    echo "✅ Created .env file"
else
    echo "✅ .env file already exists"
fi

# Source .env to check current values
set +u
source .env 2>/dev/null || true
set -u

echo ""
echo "📋 Current Configuration:"
echo "-------------------------"

# Check LM Studio config
if [ "${LM_STUDIO_ENABLED:-false}" = "true" ] || [ "${LM_STUDIO_ENABLED:-false}" = "1" ]; then
    echo "✅ LM_STUDIO_ENABLED: enabled"
else
    echo "❌ LM_STUDIO_ENABLED: disabled"
fi

if [ -n "${LM_STUDIO_BASE_URL:-}" ]; then
    echo "✅ LM_STUDIO_BASE_URL: ${LM_STUDIO_BASE_URL}"
else
    echo "⚠️  LM_STUDIO_BASE_URL: not set (will use default: http://localhost:1234/v1)"
fi

if [ -n "${LM_STUDIO_MODEL:-}" ]; then
    echo "✅ LM_STUDIO_MODEL: ${LM_STUDIO_MODEL}"
else
    echo "❌ LM_STUDIO_MODEL: not set (required)"
fi

# Check Database config
if [ -n "${GEMATRIA_DSN:-}" ]; then
    echo "✅ GEMATRIA_DSN: set"
else
    echo "❌ GEMATRIA_DSN: not set"
fi

echo ""
echo "🔍 System Checks:"
echo "-----------------"

# Check if psycopg is installed
if python3 -c "import psycopg" 2>/dev/null; then
    echo "✅ psycopg: installed"
else
    echo "❌ psycopg: not installed"
    echo "   Run: pip install psycopg[binary,pool]"
fi

# Check if lms CLI is available
if command -v lms >/dev/null 2>&1; then
    echo "✅ lms CLI: available ($(which lms))"
    lms --version 2>/dev/null || echo "   (version check failed)"
else
    echo "⚠️  lms CLI: not found in PATH"
    if [ -f "$HOME/.lmstudio/bin/lms" ]; then
        echo "   Found at: $HOME/.lmstudio/bin/lms"
        echo "   Add to PATH: export PATH=\"\$HOME/.lmstudio/bin:\$PATH\""
    fi
fi

# Check if Postgres is running
if command -v pg_isready >/dev/null 2>&1; then
    if pg_isready -h localhost >/dev/null 2>&1 || pg_isready >/dev/null 2>&1; then
        echo "✅ Postgres: running"
    else
        echo "❌ Postgres: not running"
        if [ -n "${DB_START_CMD:-}" ]; then
            echo "   DB_START_CMD is set: ${DB_START_CMD}"
            echo "   You can start Postgres with: ${DB_START_CMD}"
        else
            echo "   Set DB_START_CMD in .env to auto-start Postgres"
            echo "   Example: DB_START_CMD=\"sudo systemctl start postgresql\""
        fi
    fi
else
    echo "⚠️  pg_isready: not found (cannot check Postgres status)"
fi

echo ""
echo "📝 Configuration Recommendations:"
echo "----------------------------------"

# Generate recommendations
RECOMMENDATIONS=()

if [ "${LM_STUDIO_ENABLED:-false}" != "true" ] && [ "${LM_STUDIO_ENABLED:-false}" != "1" ]; then
    RECOMMENDATIONS+=("Set LM_STUDIO_ENABLED=1 in .env")
fi

if [ -z "${LM_STUDIO_MODEL:-}" ]; then
    RECOMMENDATIONS+=("Set LM_STUDIO_MODEL in .env (e.g., christian-bible-expert-v2.0-12b)")
fi

if [ -z "${LM_STUDIO_BASE_URL:-}" ]; then
    RECOMMENDATIONS+=("Set LM_STUDIO_BASE_URL in .env (e.g., http://127.0.0.1:1234/v1)")
fi

if [ -z "${DB_START_CMD:-}" ]; then
    # Try to detect systemd
    if command -v systemctl >/dev/null 2>&1 && systemctl list-units --type=service | grep -q postgresql; then
        RECOMMENDATIONS+=("Set DB_START_CMD=\"sudo systemctl start postgresql\" in .env")
    fi
fi

if [ ${#RECOMMENDATIONS[@]} -eq 0 ]; then
    echo "✅ Configuration looks good!"
else
    echo "To enable LM Studio and database, add these to your .env file:"
    echo ""
    for rec in "${RECOMMENDATIONS[@]}"; do
        echo "  - $rec"
    done
    echo ""
    echo "Example .env additions:"
    echo "  LM_STUDIO_ENABLED=1"
    echo "  LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1"
    echo "  LM_STUDIO_MODEL=christian-bible-expert-v2.0-12b"
    echo "  DB_START_CMD=\"sudo systemctl start postgresql\"  # or your system's command"
fi

echo ""
echo "🧪 Testing Configuration:"
echo "-------------------------"

# Test Python imports
if python3 -c "from scripts.config.env import get_lm_studio_settings, get_rw_dsn; import json; s = get_lm_studio_settings(); d = get_rw_dsn(); print('LM Studio:', json.dumps(s, indent=2)); print('DB DSN:', 'SET' if d else 'NOT SET')" 2>&1; then
    echo "✅ Configuration loader: OK"
else
    echo "❌ Configuration loader: FAILED"
fi

echo ""
echo "🚀 Next Steps:"
echo "--------------"
echo "1. Update .env with the recommended settings above"
echo "2. Start Postgres (if not running): ${DB_START_CMD:-'manually start postgresql'}"
echo "3. Start LM Studio server: lms server start --port 1234"
echo "4. Test with: pmagent health db && pmagent health lm"
echo "5. Run Reality Check #1: pmagent reality-check 1"
echo ""

