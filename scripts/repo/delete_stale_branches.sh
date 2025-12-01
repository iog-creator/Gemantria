#!/bin/bash
# FINAL BRANCH CLEANUP - Delete stale unmerged branches
# Preserves branches modified in last 30 days

set -e

DRY_RUN=true
if [ "$1" = "--execute" ]; then
    DRY_RUN=false
fi

CUTOFF_DAYS=30
DELETED_COUNT=0
PRESERVED_COUNT=0

echo "=== FINAL BRANCH CLEANUP - Stale Unmerged Branches ==="
echo "Cutoff: Branches older than ${CUTOFF_DAYS} days"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo "DRY RUN MODE - No branches will be deleted"
    echo "Run with --execute to actually delete"
    echo ""
fi

# Get all remote branches with their last commit date
git for-each-ref --sort=-committerdate refs/remotes/origin/ \
  --format='%(committerdate:short)|%(refname:short)' | \
  while IFS='|' read -r date branch; do
    # Skip HEAD and main
    if [[ "$branch" == *"HEAD"* ]] || [[ "$branch" == "origin/main" ]]; then
        continue
    fi
    
    # Calculate age
    commit_time=$(date -d "$date" +%s)
    now=$(date +%s)
    age_days=$(( (now - commit_time) / 86400 ))
    
    # Check if branch is merged
    merged=false
    if git branch -r --merged main | grep -q "$branch"; then
        merged=true
    fi
    
    # Skip if recently modified
    if [ $age_days -lt $CUTOFF_DAYS ]; then
        ((PRESERVED_COUNT++))
        continue
    fi
    
    # Delete stale unmerged branches
    branch_name=${branch#origin/}
    
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY RUN] Would delete: $branch_name (${age_days} days old, merged=$merged)"
    else
        if git push origin --delete "$branch_name" 2>/dev/null; then
            echo "✓ Deleted: $branch_name (${age_days} days old)"
            ((DELETED_COUNT++))
        else
            echo "⚠ Failed to delete: $branch_name"
        fi
    fi
done

echo ""
echo "=== SUMMARY ==="
if [ "$DRY_RUN" = true ]; then
    echo "DRY RUN: Would have processed branches"
else
    echo "Deleted: $DELETED_COUNT stale branches"
fi
echo "Preserved: $PRESERVED_COUNT recent branches (<${CUTOFF_DAYS} days)"
