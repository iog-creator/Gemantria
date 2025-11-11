#!/usr/bin/env bash
# Sync local DSN values to GitHub repository variables and secrets
# Usage: ./scripts/ops/sync_github_dsns.sh [--dry-run] [--force]

set -euo pipefail

DRY_RUN="${1:-}"
FORCE="${2:-}"

# Load environment
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Import centralized DSN loaders
export PYTHONPATH="${PYTHONPATH:-.}:."
GEMATRIA_DSN=$(python3 -c "from scripts.config.env import get_rw_dsn; import os; os.environ.setdefault('DISABLE_DOTENV', '0'); print(get_rw_dsn() or '')" 2>/dev/null || echo "${GEMATRIA_DSN:-}")
BIBLE_DB_DSN=$(python3 -c "from scripts.config.env import get_bible_db_dsn; import os; os.environ.setdefault('DISABLE_DOTENV', '0'); print(get_bible_db_dsn() or '')" 2>/dev/null || echo "${BIBLE_DB_DSN:-}")
ATLAS_DSN=$(python3 -c "from scripts.config.env import env; import os; os.environ.setdefault('DISABLE_DOTENV', '0'); print(env('ATLAS_DSN', '') or env('ATLAS_DSN_RW', '') or '')" 2>/dev/null || echo "${ATLAS_DSN:-${ATLAS_DSN_RW:-}}")

# Check authentication
if ! gh auth status >/dev/null 2>&1; then
    echo "ERROR: Not authenticated with GitHub CLI. Run: gh auth login"
    exit 1
fi

# Check admin permissions
if ! gh api repos/iog-creator/Gemantria --jq '.permissions.admin' 2>/dev/null | grep -q 'true'; then
    echo "ERROR: Insufficient permissions. Admin access required to set secrets/variables."
    exit 1
fi

echo "=== GitHub DSN Sync ==="
echo ""

# Function to set variable or secret
sync_item() {
    local name=$1
    local value=$2
    local type=$3  # "variable" or "secret"
    local current_value=""
    
    if [ "$type" = "variable" ]; then
        current_value=$(gh variable list --json name,value --jq ".[] | select(.name==\"$name\") | .value" 2>/dev/null || echo "")
    else
        # Secrets can't be read, so we check if they exist
        current_value=$(gh secret list --json name --jq ".[] | select(.name==\"$name\") | .name" 2>/dev/null | grep -q "^$name$" && echo "(exists)" || echo "")
    fi
    
    if [ -z "$value" ]; then
        echo "⚠️  SKIP: $name ($type) - no local value found"
        return 0
    fi
    
    if [ "$type" = "variable" ] && [ -n "$current_value" ] && [ "$current_value" != "(exists)" ] && [ "$current_value" = "$value" ]; then
        echo "✓ SKIP: $name ($type) - already set to same value"
        return 0
    fi
    
    if [ "$type" = "secret" ] && [ "$current_value" = "(exists)" ] && [ "$FORCE" != "--force" ]; then
        echo "⚠️  SKIP: $name ($type) - already exists (use --force to overwrite)"
        return 0
    fi
    
    if [ "$DRY_RUN" = "--dry-run" ]; then
        echo "🔍 DRY-RUN: Would set $name ($type) = ${value:0:30}..."
        return 0
    fi
    
    if [ "$type" = "variable" ]; then
        echo "$value" | gh variable set "$name" --body -
        echo "✓ SET: $name (variable)"
    else
        echo "$value" | gh secret set "$name" --body -
        echo "✓ SET: $name (secret)"
    fi
}

# Sync variables
echo "--- Variables ---"
sync_item "ATLAS_DSN" "$ATLAS_DSN" "variable"

echo ""
echo "--- Secrets ---"
sync_item "BIBLE_DB_DSN" "$BIBLE_DB_DSN" "secret"
sync_item "GEMATRIA_DSN" "$GEMATRIA_DSN" "secret"

echo ""
if [ "$DRY_RUN" = "--dry-run" ]; then
    echo "=== DRY-RUN COMPLETE ==="
    echo "Run without --dry-run to actually set values."
else
    echo "=== SYNC COMPLETE ==="
    echo "Values synced to GitHub. Verify with:"
    echo "  gh variable list"
    echo "  gh secret list"
fi

