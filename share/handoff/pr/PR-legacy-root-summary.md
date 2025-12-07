# Phase 24 Remediation + Phase 27.A/E/F Bundle

## Summary

This PR bundles Phase 24 remediation work (guard fixes, bootstrap alignment) with Phase 27 features (kernel interpreter foundation, share namespace planning, OA/PM/Console agent views).

## Phase 24 Remediation

### 24.B — DMS Alignment Guard Fix
- **Fixed**: `guard_dms_share_alignment.py` now correctly ignores legitimate non-DMS-managed paths
  - Added `handoff/` to `ALLOWED_SUBDIRS` (kernel bundle directory)
  - Added `planning_context.json` to `ALLOWED_FILES` (planning pipeline output)
  - Added SSOT reference to `SHARE_FOLDER_ANALYSIS.md`

### 24.B — Share Sync Policy Guard Fix  
- **Fixed**: `guard_share_sync_policy.py` now correctly ignores same paths
  - Added `share/handoff` to `SYSTEM_PREFIXES`
  - Added `share/planning_context.json` to `SYSTEM_FILES`
  - Added SSOT reference comment

### 24.D — Backup System
- **Status**: ✅ Passing (fresh backup created)
- Backup guard now correctly validates recent backups

### 24.E — Kernel/Bootstrap Coherence
- **Fixed**: Bootstrap state regenerated on current branch
  - `PM_BOOTSTRAP_STATE.json` regenerated via `make pm.bootstrap.state`
  - `PM_KERNEL.json` regenerated via `pmagent handoff kernel-bundle`
  - Branch mismatch resolved: both now on `feat/phase27-kernel-consumers`

### Makefile Cleanup
- **Fixed**: Removed duplicate target definitions causing warnings
  - Removed duplicate `phase8.temporal` (kept full implementation)
  - Removed duplicate `rerank.smoke` (kept simpler version)
  - Removed duplicate `governance.ingest.docs` (kept Python script version)
- **Fixed**: Restored `mcp.proof.snapshot` target with proper Python implementation
  - Replaced bash stub script with canonical `scripts/mcp/generate_proof_snapshot.py`
  - Target now generates `share/mcp/knowledge_mcp_proof.json` as expected by `guard.mcp.proof`
  - Verified `make mcp.proof.snapshot` and `make guard.mcp.proof` both work correctly

## Kernel Status

**Before:**
- `reality_green: false`
- `degraded: true`
- `warnings: ["Branch mismatch: ..."]`

**After:**
- `reality_green: true` ✅
- `degraded: false` ✅
- `warnings: []` ✅

## Current Kernel State

```json
{
  "ok": true,
  "kernel": {
    "current_phase": "24",
    "last_completed_phase": "23",
    "branch": "feat/phase27-kernel-consumers"
  },
  "health": {
    "reality_green": true,
    "failed_checks": []
  },
  "degraded": false,
  "warnings": []
}
```

## Phase 27 Features (Already Implemented)

This branch includes Phase 27 work that was already implemented:
- **27.A**: Kernel interpreter foundation (design spec + partial implementation)
- **27.E**: Share namespace planning + preflight
- **27.F**: OA/PM/Console agent views in `planning_context.json`

## Testing

- ✅ `make reality.green` passes
- ✅ `pmagent handoff status-handoff` shows `degraded: false`
- ✅ `tests/pmagent/test_handoff_boot.py` passes (4 tests)
- ✅ Ruff checks pass on modified Python files
- ✅ All guards passing (DMS Alignment, Share Sync Policy, Backup System)

## Note on Phase Pointer

This PR **does not** change the kernel's `current_phase`/`last_completed_phase` logic. The kernel still reports `current_phase: "24"` and `last_completed_phase: "23"` for honesty — we haven't formally advanced the phase pointer in SSOT yet. Phase pointer reconciliation will be a follow-up change.

## Files Changed (This Session)

- `scripts/guards/guard_dms_share_alignment.py` — Added allowlist for non-DMS-managed paths
- `scripts/guards/guard_share_sync_policy.py` — Added allowlist for non-DMS-managed paths  
- `Makefile` — Removed duplicate target definitions
- `share/PM_BOOTSTRAP_STATE.json` — Regenerated on current branch
- `share/handoff/PM_KERNEL.json` — Regenerated with aligned branches
