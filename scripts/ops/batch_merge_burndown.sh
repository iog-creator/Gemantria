#!/usr/bin/env bash
set -euo pipefail

# Batch merge script for DSN burndown PRs
# Merges main into each PR branch, resolves conflicts, pushes, and merges PR

cd /home/mccoy/Projects/Gemantria.v2

PRS=$(jq -r '.[].number' evidence/dsn.burndown.open.json)

for PR_NUM in $PRS; do
  echo "== Processing PR #$PR_NUM =="
  
  # Get branch name
  BRANCH=$(gh pr view "$PR_NUM" --json headRefName -q .headRefName)
  if [ -z "$BRANCH" ]; then
    echo "  Skipping: could not get branch name"
    continue
  fi
  
  # Check if already merged
  MERGEABLE=$(gh pr view "$PR_NUM" --json mergeable,mergeStateStatus -q '.mergeable // "UNKNOWN"')
  if [ "$MERGEABLE" = "MERGEABLE" ]; then
    echo "  Already mergeable, attempting merge..."
    gh pr merge "$PR_NUM" --squash 2>&1 | head -5 || echo "  Merge failed or already merged"
    continue
  fi
  
  # Fetch and checkout branch
  echo "  Fetching branch $BRANCH..."
  git fetch origin "$BRANCH:$BRANCH" 2>&1 | grep -v "From\|*" || true
  git checkout "$BRANCH" 2>&1 | head -3 || { echo "  Failed to checkout"; continue; }
  
  # Merge main into branch
  echo "  Merging main into $BRANCH..."
  if git merge main --no-edit 2>&1 | tee /tmp/merge.log | grep -q "CONFLICT"; then
    echo "  Conflict detected, resolving..."
    
    # Resolve auto_refactor_dsn.py conflict if present
    if grep -q "auto_refactor_dsn.py" /tmp/merge.log; then
      # Use main's version (already resolved)
      git checkout --theirs scripts/ops/auto_refactor_dsn.py 2>&1 || true
      git add scripts/ops/auto_refactor_dsn.py
    fi
    
    # Commit merge
    git commit --no-edit 2>&1 | head -3 || echo "  Commit failed"
  else
    echo "  Clean merge"
  fi
  
  # Push updated branch
  echo "  Pushing $BRANCH..."
  git push origin "$BRANCH" 2>&1 | head -5 || { echo "  Push failed"; continue; }
  
  # Wait a moment for GitHub to update
  sleep 2
  
  # Attempt merge
  echo "  Attempting PR merge..."
  gh pr merge "$PR_NUM" --squash 2>&1 | head -5 || echo "  Merge failed or needs manual intervention"
  
  echo "  Done with PR #$PR_NUM"
  echo ""
done

echo "== Batch processing complete =="

