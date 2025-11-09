#!/bin/bash
# verify_post_change.sh — Verify post-change requirements per Rule 058, 026, 030

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ERRORS=0
WARNINGS=0

echo "🔍 Verifying post-change requirements..."

# Check if housekeeping was run (look for recent evidence files)
if git diff --name-only | grep -qE "(\.cursor/rules|docs/SSOT|AGENTS\.md|RULES_INDEX\.md)"; then
    if [ ! -f "evidence/governance_docs_hints.json" ] || [ "$(find evidence/governance_docs_hints.json -mmin +5 2>/dev/null || echo 'missing')" != "missing" ]; then
        echo "❌ ERROR: Housekeeping not run after rule/docs changes (Rule 058)"
        echo "   Run: make housekeeping"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Check share sync
if git diff --name-only | grep -qE "(docs/|scripts/|\.cursor/rules|AGENTS\.md)" && ! git diff --name-only | grep -q "share/"; then
    echo "⚠️  WARNING: Share sync may be needed (Rule 030)"
    echo "   Run: make share.sync"
    WARNINGS=$((WARNINGS + 1))
fi

# Check if hints were emitted for rule/docs changes
if git diff --name-only | grep -qE "(\.cursor/rules|docs/SSOT)" && [ -f "evidence/governance_docs_hints.json" ]; then
    HINT_COUNT=$(jq -r '.count // 0' evidence/governance_docs_hints.json 2>/dev/null || echo "0")
    if [ "$HINT_COUNT" = "0" ]; then
        echo "⚠️  WARNING: No hints emitted for rule/docs changes (Rule 026)"
        echo "   Run: make governance.docs.hints"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

# Summary
if [ $ERRORS -gt 0 ]; then
    echo ""
    echo "❌ FAILED: $ERRORS error(s), $WARNINGS warning(s)"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo ""
    echo "⚠️  WARNINGS: $WARNINGS warning(s) (non-blocking)"
    exit 0
else
    echo "✅ Post-change verification complete"
    exit 0
fi

