#!/usr/bin/env bash
set -euo pipefail

# Fast batch merge for DSN burndown PRs
# Resolves common conflicts automatically

cd /home/mccoy/Projects/Gemantria.v2
git checkout main >/dev/null 2>&1

PRS=$(jq -r '.[].number' evidence/dsn.burndown.open.json)

for PR_NUM in $PRS; do
  echo "== PR #$PR_NUM =="
  
  # Check if already merged
  STATE=$(gh pr view "$PR_NUM" --json state,mergeStateStatus -q '.state // "OPEN"')
  if [ "$STATE" != "OPEN" ]; then
    echo "  Already $STATE, skipping"
    continue
  fi
  
  MERGE_STATUS=$(gh pr view "$PR_NUM" --json mergeStateStatus -q '.mergeStateStatus // "UNKNOWN"')
  if [ "$MERGE_STATUS" = "CLEAN" ]; then
    echo "  CLEAN, merging..."
    gh pr merge "$PR_NUM" --squash 2>&1 | head -3 || echo "  Merge failed"
    continue
  fi
  
  # Get branch and update it
  BRANCH=$(gh pr view "$PR_NUM" --json headRefName -q .headRefName)
  if [ -z "$BRANCH" ]; then
    echo "  Could not get branch, skipping"
    continue
  fi
  
  echo "  Updating $BRANCH..."
  
  # Clean up local branch if exists
  git branch -D "$BRANCH" 2>/dev/null || true
  
  # Fetch and checkout
  git fetch origin "$BRANCH:$BRANCH" 2>&1 | grep -v "^From" || true
  git checkout "$BRANCH" 2>&1 | head -1 || { echo "  Checkout failed"; continue; }
  
  # Merge main
  if git merge main --no-edit 2>&1 | tee /tmp/merge_$PR_NUM.log | grep -q "CONFLICT"; then
    echo "  Resolving conflicts..."
    # Auto-resolve common conflicts
    git checkout --theirs scripts/guards/.dsn_direct.allowlist 2>/dev/null || true
    git checkout --theirs scripts/ops/auto_refactor_dsn.py 2>/dev/null || true
    git add scripts/guards/.dsn_direct.allowlist scripts/ops/auto_refactor_dsn.py 2>/dev/null || true
    git commit --no-edit 2>&1 | head -2 || { echo "  Commit failed"; git merge --abort 2>/dev/null || true; continue; }
  fi
  
  # Push and merge
  git push origin "$BRANCH" 2>&1 | head -3 || { echo "  Push failed"; continue; }
  sleep 2
  gh pr merge "$PR_NUM" --squash 2>&1 | head -3 || echo "  Merge command failed"
  
  git checkout main >/dev/null 2>&1
  echo ""
done

echo "== Complete =="

