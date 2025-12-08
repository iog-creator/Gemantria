# Guard Debugging Gotchas — Lessons Learned

**Status:** Living document  
**Last Updated:** 2025-12-08  
**Phase:** 28B

---

## 1. OA State Circular Dependency

### Symptom
`reality_green mismatch: PM_BOOTSTRAP.health=True vs REALITY_GREEN=False`

### Root Cause
Circular read chain:
1. `reality.green` runs, writes `REALITY_GREEN_SUMMARY.json` with `false` on failure
2. `PM_BOOTSTRAP_STATE.json` generator reads this file → caches `reality_green: false`
3. On next `reality.green` run, OA State guard compares PM_BOOTSTRAP (cached false) vs new REALITY_GREEN (true after checks pass)
4. Mismatch → failure → writes false again → cycle continues

### Fix Applied
1. **Disabled** `PM_BOOTSTRAP.health.reality_green` check in `guard_oa_state.py` (lines 115-127)
2. **Moved** OA state refresh to AFTER final summary write in `guard_reality_green.py`
3. **Removed** redundant `write_oa_state()` from `check_oa_state()` wrapper

### Prevention
- Never compare cached surfaces against freshly-written surfaces in same pipeline
- Order matters: write final state FIRST, then refresh dependent surfaces

---

## 2. Stale REALITY_GREEN_SUMMARY

### Symptom
Guard reports failure but files/state are actually correct

### Root Cause
`REALITY_GREEN_SUMMARY.json` contains results from PRIOR run, not current run.

### Fix
Run `make reality.green` again to refresh the summary with current state.

### Prevention
- Always run `make reality.green` twice after major changes
- Debug output shows actual file state via standalone guard scripts

---

## 3. Backup System Blocking

### Symptom
`No recent backup found` blocks all operations

### Root Cause
Strict backup check with 5-minute timeout. Long-running operations exceed timeout.

### Fix Applied
Modified `check_backup_system()` to auto-create backup if missing (commit `5218a82a`)

### Prevention
- Auto-create is better than fail-closed for non-destructive checks
- Consider backup timeout extension for long operations

---

## 4. Root Surface Phantom Files

### Symptom
Guard reports unexpected files in root that don't exist

### Root Cause
Same as #2 — stale `REALITY_GREEN_SUMMARY.json`

### Debug Steps
```bash
# Check if files actually exist
ls -la <filename>

# If not found, run reality.green again to refresh
make reality.green
```

---

## 5. Embedding Performance

### Symptom
`make housekeeping` takes 8+ minutes, re-embeds all 51k fragments

### Root Cause
`ingest_doc_content.py` deleted ALL fragments for each doc on every run, orphaning embeddings.

### Fix Applied
Added `version_id` check (commit `9bcc3466`):
```python
# Skip if fragments exist for current version
existing = conn.execute("SELECT COUNT(*) FROM doc_fragment WHERE doc_id=:d AND version_id=:v")
if existing > 0:
    continue  # Skip unchanged doc
```

### Prevention
- Always check for unchanged state before delete/recreate
- Content hash or version_id comparison is sufficient

---

## Debugging Workflow

1. **Run standalone guard** to isolate issue:
   ```bash
   python scripts/guards/guard_oa_state.py --mode STRICT
   ```

2. **Check actual file state** vs summary:
   ```bash
   cat share/REALITY_GREEN_SUMMARY.json | jq '.checks[] | select(.passed == false)'
   ```

3. **Verify surfaces match**:
   ```bash
   cat share/orchestrator_assistant/STATE.json | jq '.reality_green'
   cat share/REALITY_GREEN_SUMMARY.json | jq '.reality_green'
   ```

4. **When in doubt, run twice**:
   ```bash
   make reality.green && make reality.green
   ```
