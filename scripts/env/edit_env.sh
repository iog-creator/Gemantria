#!/usr/bin/env bash

set -euo pipefail

# Safe .env file editor with backup protection
# Usage: ./scripts/env/edit_env.sh [editor_command]

ENV_FILE=".env"
BACKUP_SCRIPT="./scripts/env/backup_env.sh"

# Check if .env exists
if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: $ENV_FILE does not exist. Run setup first."
    exit 1
fi

# Check if backup script exists
if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo "ERROR: Backup script not found: $BACKUP_SCRIPT"
    exit 1
fi

echo "🔒 Creating backup before editing..."
"$BACKUP_SCRIPT"

echo "📝 Opening $ENV_FILE for editing..."
echo "⚠️  WARNING: Changes will be tracked in version control"
echo "⚠️  WARNING: Make sure you know what you're changing"
echo ""

# Default editor or use provided command
if [ $# -eq 0 ]; then
    # Use $EDITOR or default to nano
    ${EDITOR:-nano} "$ENV_FILE"
else
    "$@" "$ENV_FILE"
fi

echo ""
echo "✅ Edit complete. Backup created automatically."
echo "💡 Run 'make share.sync' if you updated documentation-related variables"
