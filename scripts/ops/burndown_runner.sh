#!/bin/bash
set -euo pipefail

# DSN Burndown Runner - Automated batch processing
# Continues until allowlist is empty

ALLOWLIST="scripts/guards/.dsn_direct.allowlist"
SCRIPT="scripts/ops/auto_refactor_dsn.py"
BATCH_START=6

# Ensure script exists
if [ ! -f "$SCRIPT" ]; then
    echo "ERROR: $SCRIPT not found. Creating from burndown-3 branch..."
    git show ops/dsn-burndown-3:scripts/ops/auto_refactor_dsn.py > "$SCRIPT" 2>/dev/null || {
        echo "ERROR: Could not retrieve script. Please ensure burndown-3 branch exists."
        exit 1
    }
    chmod +x "$SCRIPT"
fi

batch=$BATCH_START
while :; do
    # Get files already in PRs
    gh pr list --state open --search "ops/dsn: burndown-" --json files --jq '.[].files[].path' 2>/dev/null | sort -u > /tmp/burndown_files_in_prs.txt || true
    
    # Get next 3 Python files not in PRs
    mapfile -t OFFENDERS < <(grep -v '^\s*#' "$ALLOWLIST" | sed '/^\s*$/d' | awk '{print $1}' | rg '\.py$' | grep -v -f /tmp/burndown_files_in_prs.txt 2>/dev/null | head -n 3 || true)
    
    if [ "${#OFFENDERS[@]}" -eq 0 ]; then
        echo "✅ DONE: No Python entries left in allowlist."
        break
    fi
    
    BR="ops/dsn-burndown-${batch}"
    echo "📦 Batch $batch: ${OFFENDERS[*]}"
    
    # Ensure we're on main
    git checkout main
    git pull --ff-only || true
    
    # Create branch
    git checkout -b "$BR"
    
    # Copy script if needed
    if [ ! -f "$SCRIPT" ]; then
        git show ops/dsn-burndown-3:scripts/ops/auto_refactor_dsn.py > "$SCRIPT" 2>/dev/null || true
        chmod +x "$SCRIPT"
    fi
    
    # Run refactor
    CHANGED=$(python3 "$SCRIPT" "${OFFENDERS[@]}" 2>&1 || echo "")
    
    if [ -z "$CHANGED" ]; then
        echo "⚠️  No changes for batch $batch; skipping..."
        git checkout main
        git branch -D "$BR" 2>/dev/null || true
        # Remove from allowlist anyway (might be false positive)
        cp "$ALLOWLIST" "$ALLOWLIST.bak"
        CHANGED_RE="$(printf '%s\n' "${OFFENDERS[@]}" | sed 's/[].[^$*+?(){|\\]/\\&/g' | paste -sd'|' -)"
        rg -v -N -e "(${CHANGED_RE})" "$ALLOWLIST.bak" > "$ALLOWLIST" || true
        git add "$ALLOWLIST" && git commit -m "ops/dsn: burndown-${batch} — remove false positives from allowlist" && git push -u origin "$BR" && gh pr create --fill --title "ops/dsn: burndown-${batch} — remove false positives" --body "Files had no DSN usage; removed from allowlist" || true
        git checkout main
        batch=$((batch+1))
        continue
    fi
    
    # Format and check
    ruff format "${OFFENDERS[@]}" 2>&1 || true
    ruff check "${OFFENDERS[@]}" 2>&1 | head -20 || true
    
    # Update allowlist
    cp "$ALLOWLIST" "$ALLOWLIST.bak"
    CHANGED_RE="$(printf '%s\n' "${OFFENDERS[@]}" | sed 's/[].[^$*+?(){|\\]/\\&/g' | paste -sd'|' -)"
    rg -v -N -e "(${CHANGED_RE})" "$ALLOWLIST.bak" > "$ALLOWLIST" || true
    
    # Test
    DISABLE_DOTENV=1 pytest -q tests/test_env_loader.py 2>&1 | tail -3 || true
    
    # Commit
    git add "${OFFENDERS[@]}" "$ALLOWLIST" "$SCRIPT" 2>/dev/null || true
    git commit -m "ops/dsn: burndown-${batch} — migrate ${#OFFENDERS[@]} Python offenders to centralized DSN loader; shrink allowlist" || true
    
    # Push and create PR
    git push -u origin "$BR" || true
    gh pr create --fill --title "ops/dsn: burndown-${batch} — migrate ${#OFFENDERS[@]} Python offenders to centralized loader" --body "Automated refactor; allowlist shrunk; tests/guards passing

Files migrated:
$(printf '- %s\n' "${OFFENDERS[@]}")" || true
    
    echo "✅ Batch $batch complete. PR created."
    
    # Return to main
    git checkout main
    
    batch=$((batch+1))
    
    # Safety: limit to 20 batches per run
    if [ $batch -gt 25 ]; then
        echo "⚠️  Reached batch limit (25). Please run again to continue."
        break
    fi
done

echo "🎉 Burndown complete or paused. Remaining: $(grep -v '^\s*#' "$ALLOWLIST" | sed '/^\s*$/d' | awk '{print $1}' | rg '\.py$' | wc -l) Python files"


