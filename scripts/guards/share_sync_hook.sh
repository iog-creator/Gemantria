#!/usr/bin/env bash
# Pre-commit hook: auto-sync share/ when tracked files change
# This ensures share/ stays in sync with source files automatically

set -euo pipefail

# Files that should trigger share sync
TRACKED_FILES=(
    "MASTER_PLAN.md"
    "docs/SSOT/MASTER_PLAN.md"
    "RULES_INDEX.md"
    "docs/SSOT/RULES_INDEX.md"
    "AGENTS.md"
    "README_FULL.md"
    "README.md"
    "docs/SSOT/GPT_SYSTEM_PROMPT.md"
    "docs/runbooks/LM_STUDIO_SETUP.md"
    "docs/runbooks/DB_HEALTH.md"
    "docs/SSOT/webui-contract.md"
    "docs/SSOT/SHARE_MANIFEST.json"
)

# Check if any tracked files are staged or changed
CHANGED=0
for file in "${TRACKED_FILES[@]}"; do
    if git diff --cached --name-only --quiet -- "$file" 2>/dev/null; then
        # Not in staged changes, check if file exists and was modified
        if [ -f "$file" ] && ! git diff --quiet -- "$file" 2>/dev/null; then
            CHANGED=1
            break
        fi
    else
        CHANGED=1
        break
    fi
done

# Also check if share manifest itself changed
if git diff --cached --name-only | grep -q "SHARE_MANIFEST.json\|share.sync\|update_share.py\|sync_share.py"; then
    CHANGED=1
fi

if [ "$CHANGED" = "1" ]; then
    echo "[share-sync-hook] Detected changes to tracked files, syncing share/..."
    make share.sync || {
        echo "[share-sync-hook] WARNING: share.sync failed (non-fatal)"
        exit 0  # Don't block commit, but warn
    }
    # Stage any changes made by share.sync
    if ! git diff --quiet -- share/ 2>/dev/null; then
        echo "[share-sync-hook] Staging updated share/ files..."
        git add share/ || true
    fi
fi

exit 0

