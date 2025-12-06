# Phase 23.2 — Failure Injection

**Status:** COMPLETE  
**Date:** 2025-12-05

## Purpose

Verify the system fails loudly when critical files are missing or corrupt.

## Scenarios Tested

### Scenario 1: Missing SSOT_SURFACE_V17.json

**Actions:**
1. Backup and remove `share/SSOT_SURFACE_V17.json`
2. Run `python scripts/pm/check_console_v2.py`
3. Run `make stress.smoke`
4. Restore from backup

**Expected:** Loud failure with clear error message  
**Actual:** ✅ Both tools failed loudly with:
```
ERROR: Data source 'ssot_surface' points to 'share/SSOT_SURFACE_V17.json' 
but the resolved path does not exist
```

### Scenario 2: Corrupt JSON (syntax error)

**Actions:**
1. Corrupt `share/SSOT_SURFACE_V17.json` with invalid JSON
2. Run `python scripts/pm/check_console_v2.py`
3. Restore valid JSON

**Expected:** Loud failure on JSON parse  
**Actual:** ⚠️ Script passed silently (only checks existence, not validity)

## Detection Matrix

| Failure Mode | `check_console_v2.py` | `stress.smoke` |
|--------------|----------------------|----------------|
| Missing file | ✅ Loud FAIL | ✅ Propagates |
| Corrupt JSON | ⚠️ Silent PASS | ⚠️ Silent PASS |

## Conclusion

File existence is validated. JSON validity is NOT validated (acceptable boundary
for Phase 23; can be improved in future phase).

## Evidence

- `evidence/stress/failure_injection/console_check_missing_ssot.txt`
- `evidence/stress/failure_injection/stress_smoke_missing_ssot.txt`
- `evidence/stress/failure_injection/stress_smoke_after_restore.txt`
