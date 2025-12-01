#!/bin/bash
# Merge Guard - Prevents destructive merges
# Usage: ./guard_merge.sh <branch-name> [base-branch]

set -e

BRANCH=${1:-HEAD}
BASE=${2:-main}

echo "🛡️  Merge Guard: Checking $BRANCH against $BASE"
echo ""

# Get diff stats
STATS=$(git diff --shortstat $BASE...$BRANCH 2>/dev/null || echo "")

if [ -z "$STATS" ]; then
    echo "✅ No changes detected - safe to merge"
    exit 0
fi

INSERTIONS=$(echo "$STATS" | grep -oP '\d+(?= insertion)' || echo "0")
DELETIONS=$(echo "$STATS" | grep -oP '\d+(?= deletion)' || echo "0")

echo "📊 Stats: +$INSERTIONS / -$DELETIONS lines"

# Check for net negative
if [ "$DELETIONS" -gt "$INSERTIONS" ]; then
    NET=$((DELETIONS - INSERTIONS))
    echo ""
    echo "⚠️  WARNING: This merge would DELETE $NET net lines!"
    echo ""
    echo "❌ BLOCKED: Potential destructive merge detected"
    echo ""
    echo "This branch would remove more code than it adds."
    echo "This is usually a sign of:"
    echo "  - Branch based on old main (missing recent merges)"
    echo "  - Accidental file deletions"
    echo "  - Reverted changes"
    echo ""
    echo "To proceed anyway: FORCE_MERGE=1 $0 $@"
    
    if [ "${FORCE_MERGE}" != "1" ]; then
        exit 1
    else
        echo ""
        echo "⚠️  FORCE_MERGE enabled - proceeding despite warnings"
    fi
fi

# Check for deleted critical files
DELETED_FILES=$(git diff --diff-filter=D --name-only $BASE...$BRANCH 2>/dev/null || echo "")

if [ -n "$DELETED_FILES" ]; then
    CRITICAL=$(echo "$DELETED_FILES" | grep -E '\.(py|ts|tsx|js)$' || echo "")
    
    if [ -n "$CRITICAL" ]; then
        echo ""
        echo "⚠️  WARNING: Code files would be deleted:"
        echo "$CRITICAL" | head -10
        
        LOGIC_FILES=$(echo "$CRITICAL" | grep -E 'logic\.py|adapter\.py|flow\.py|commands\.py' || echo "")
        if [ -n "$LOGIC_FILES" ]; then
            echo ""
            echo "❌ CRITICAL: Implementation files would be deleted!"
            echo "$LOGIC_FILES"
            echo ""
            echo "This is likely a destructive merge. BLOCKED."
            
            if [ "${FORCE_MERGE}" != "1" ]; then
                exit 1
            fi
        fi
    fi
fi

# Check if branch is up to date with base
BEHIND=$(git rev-list --count $BRANCH..$BASE 2>/dev/null || echo "0")

if [ "$BEHIND" -gt 0 ]; then
    echo ""
    echo "⚠️  WARNING: Branch is $BEHIND commits behind $BASE"
    echo ""
    echo "Branch is not up to date. This can cause conflicts or loss of recent work."
    echo ""
    echo "Recommended: Update branch first:"
    echo "  git checkout $BRANCH"
    echo "  git merge $BASE"
    echo "  # or: git rebase $BASE"
    echo ""
fi

# Summary
echo ""
echo "✅ Merge guard checks passed"
echo ""
echo "Summary:"
echo "  Base: $BASE"
echo "  Branch: $BRANCH"
echo "  Changes: +$INSERTIONS / -$DELETIONS"
echo "  Branch status: $BEHIND commits behind base"
echo ""

if [ "$DELETIONS" -gt 100 ] || [ "$BEHIND" -gt 10 ]; then
    echo "⚠️  Note: Large changes detected - please review carefully"
fi

exit 0
