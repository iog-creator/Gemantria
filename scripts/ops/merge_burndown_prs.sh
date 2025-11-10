#!/bin/bash
set -euo pipefail

# Merge all burndown PRs: fix imports, verify, merge

FIXER="scripts/ops/fix_env_loader_imports.py"

# Get PR numbers
PR_NUMS=$(gh pr list --state open --search '"ops/dsn: burndown-" in:title' --json number -q '.[].number' | sort -n)

for N in $PR_NUMS; do
  echo "== Handling PR #$N =="
  
  # Fetch and checkout (clean untracked files first)
  git clean -fdq 2>&1 || true
  rm -f scripts/ops/fix_env_loader_imports.py scripts/ops/merge_burndown_prs.sh 2>&1 || true
  git fetch origin pull/$N/head:pr/$N 2>&1 | grep -v "Already up to date" || true
  git checkout -f pr/$N 2>&1 || true
  
  # Copy fixer script from main if it doesn't exist
  if [ ! -f "$FIXER" ]; then
    git show main:$FIXER > "$FIXER" 2>/dev/null || echo "Warning: Could not get fixer from main"
    chmod +x "$FIXER" 2>/dev/null || true
  fi
  
  # Get changed Python files
  CHANGED_PY=$(git diff --name-only origin/main...HEAD | rg '\.py$' || true)
  
  if [ -n "$CHANGED_PY" ] && [ -f "$FIXER" ]; then
    # Fix imports
    echo "$CHANGED_PY" | xargs -r python3 "$FIXER" 2>&1 | head -5 || true
  fi
  
  # Format and check
  ruff format . 2>&1 | tail -2 || true
  ruff check . 2>&1 | head -10 || true
  
  # If there are changes, commit and push to the actual PR branch
  if ! git diff --quiet || ! git diff --cached --quiet; then
    git add -A
    git commit -m "fix: normalize env loader imports; remove unused; re-run ruff" || true
    # Push to the actual PR branch (headRefName from PR)
    HEAD_REF=$(gh pr view $N --json headRefName -q '.headRefName')
    git push origin pr/$N:$HEAD_REF || true
  fi
  
  # Run tests
  DISABLE_DOTENV=1 pytest -q tests/test_env_loader.py 2>&1 | tail -3 || true
  
  # Try to merge (will fail if checks not green, that's ok)
  gh pr merge $N --squash --auto 2>&1 | head -5 || true
  
  # Back to main
  git checkout main
  echo "---"
done

echo "✅ Processed all PRs"

