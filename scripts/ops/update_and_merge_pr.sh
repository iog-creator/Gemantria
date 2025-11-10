#!/usr/bin/env bash
set -euo pipefail

# Update and merge a single PR using worktree
# Usage: update_and_merge_pr.sh <PR_NUMBER>

N="$1"
HEAD_REF="$(gh pr view "$N" --json headRefName -q .headRefName)"
WT=".wt/pr-$N"

echo "== PR #$N ($HEAD_REF) =="

# Clean up any existing worktree
rm -rf "$WT"

# Fetch latest
git fetch origin "$HEAD_REF" main --quiet

# Create worktree
git worktree add -f "$WT" "origin/$HEAD_REF" >/dev/null

pushd "$WT" >/dev/null

# Ensure branch checked out locally, sync from origin
git switch -C "$HEAD_REF" >/dev/null
git pull --ff-only 2>/dev/null || true

# Always merge main (create merge commit even if fast-forward possible)
MERGE_OUTPUT=$(git merge --no-edit --no-ff origin/main 2>&1 | tee /tmp/merge_$N.log) || true
if echo "$MERGE_OUTPUT" | grep -q "CONFLICT"; then
  echo "  Conflict detected; resolving by taking main's versions for known files"
  # Known conflict set: keep main's versions
  git checkout --theirs scripts/guards/.dsn_direct.allowlist 2>/dev/null || true
  git checkout --theirs scripts/ops/auto_refactor_dsn.py 2>/dev/null || true
  git add -A
  git commit -m "ops/dsn: sync with main (keep allowlist + auto_refactor from main)" || true
elif echo "$MERGE_OUTPUT" | grep -q "Already up to date"; then
  echo "  Branch already up to date with main, creating empty merge commit"
  # Create a merge commit anyway to update GitHub's view
  git merge --no-edit --no-ff -s ours origin/main 2>&1 | head -3 || true
fi

# Minimal hygiene (SSOT formatter)
ruff format . >/dev/null 2>&1 || true
ruff check --fix . >/dev/null 2>&1 || true

# Push
git push origin "HEAD:$HEAD_REF" 2>&1 | head -5

popd >/dev/null
git worktree remove -f "$WT" >/dev/null

# Wait a moment for GitHub to update
sleep 2

# Check required checks (if any), then try merge
gh pr checks "$N" --required --watch 2>&1 | head -10 || true
gh pr merge "$N" --squash 2>&1 | head -5 || echo "  Merge command completed (may need manual intervention)"

echo "  Done with PR #$N"
echo ""

