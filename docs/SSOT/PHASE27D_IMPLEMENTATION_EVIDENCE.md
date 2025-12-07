# Phase 27.D — Kernel Surfaces Coherence

**Status**: ✅ COMPLETE  
**Branch**: `feat/phase27l-agents-dms-contract`  
**Commit**: `b31bb758 chore(27.D): kernel surfaces coherence (PM_BOOTSTRAP_STATE, REALITY_GREEN, OA STATE)`

---

## Problem Statement

Three kernel-facing truth surfaces were found to have coherence issues:

| Surface | Pre-Fix State | Issue |
|---------|---------------|-------|
| `REALITY_GREEN_SUMMARY.json` | `reality_green: false` | Backup check had failed |
| `PM_BOOTSTRAP_STATE.json` | `meta.dms_share_alignment: "BROKEN"` | Derived from stale SSOT surface |
| `OA STATE.json` | `reality_green: true` | Stale snapshot from before backup failure |

The root causes were:
1. `SSOT_SURFACE_V17.json` was stale (showed `dms_share_alignment: "BROKEN"` when DMS was actually OK)
2. `PM_BOOTSTRAP_STATE` copied the stale value from SSOT surface
3. OA state was not refreshed after reality.green status changed
4. No guard enforced cross-surface coherence

---

## Changes Made

### 1. [generate_pm_bootstrap_state.py](file:///home/mccoy/Projects/Gemantria.v2/scripts/pm/generate_pm_bootstrap_state.py)

Added `health` section derived from `REALITY_GREEN_SUMMARY.json`:

```diff
+def load_reality_green_summary() -> dict[str, Any] | None:
+    """Load REALITY_GREEN_SUMMARY.json for canonical health state."""
+    ...

+# Load REALITY_GREEN_SUMMARY for coherent health data (Phase 27.D)
+rg_summary = load_reality_green_summary() or {}
+reality_green = rg_summary.get("reality_green", False)
+
+# Extract key check statuses for health section
+agents_sync_ok = any(c.get("name") == "AGENTS.md Sync" and c.get("passed") for c in checks)
+dms_alignment_ok = any(c.get("name") == "DMS Alignment" and c.get("passed") for c in checks)

+# Phase 27.D: Health section derived from REALITY_GREEN_SUMMARY for coherence
+"health": {
+    "reality_green": reality_green,
+    "agents_sync_ok": agents_sync_ok,
+    "dms_alignment_ok": dms_alignment_ok,
+    "source": "share/REALITY_GREEN_SUMMARY.json",
+},

-"dms_share_alignment": ssot_surface.get("dms_share_alignment", check_alignment_status()),
```

### 2. [guard_oa_state.py](file:///home/mccoy/Projects/Gemantria.v2/scripts/guards/guard_oa_state.py)

Enhanced with tri-surface coherence checks:

```python
# Phase 27.D: Tri-Surface Coherence Checks

# 1. OA reality_green must match REALITY_GREEN_SUMMARY
# 2. PM_BOOTSTRAP health.reality_green must match REALITY_GREEN_SUMMARY
# 3. Key check statuses must match between OA and REALITY_GREEN_SUMMARY
#    - "AGENTS.md Sync", "DMS Alignment", "AGENTS–DMS Contract"
# 4. PM_BOOTSTRAP health.agents_sync_ok and health.dms_alignment_ok must match
# 5. Check for contradictory stale meta.dms_share_alignment notes
```

---

## Coherence Invariants (Post-Fix)

All invariants now enforced by `guard_oa_state.py --mode STRICT`:

| Invariant | Status |
|-----------|--------|
| `OA_STATE.reality_green == REALITY_GREEN_SUMMARY.reality_green` | ✅ PASS |
| `PM_BOOTSTRAP_STATE.health.reality_green == REALITY_GREEN_SUMMARY.reality_green` | ✅ PASS |
| AGENTS Sync `passed` matches across OA and reality.green | ✅ PASS |
| DMS Alignment `passed` matches across OA and reality.green | ✅ PASS |
| No stale `meta.dms_share_alignment: "BROKEN"` contradicting reality.green | ✅ PASS |

---

## Final Surface State

### REALITY_GREEN_SUMMARY.json

```json
{
  "reality_green": true,
  "checks": [
    {"name": "AGENTS.md Sync", "passed": true},
    {"name": "DMS Alignment", "passed": true},
    ...
  ]
}
```

### PM_BOOTSTRAP_STATE.json

```json
{
  "health": {
    "reality_green": true,
    "agents_sync_ok": true,
    "dms_alignment_ok": true,
    "source": "share/REALITY_GREEN_SUMMARY.json"
  },
  "meta": {
    "current_phase": "24",
    "kb_registry_path": "share/kb_registry.json",
    "last_completed_phase": "23"
  }
}
```

### OA STATE.json

```json
{
  "reality_green": true,
  "checks_summary": [
    {"name": "AGENTS.md Sync", "passed": true},
    {"name": "DMS Alignment", "passed": true},
    ...
  ]
}
```

---

## Guard Outputs

### guard_oa_state.py --mode STRICT

```
✅ OA State Guard: PASS
   OA state is consistent with kernel surfaces

JSON: {"ok": true, "mode": "STRICT", "mismatches": [], "missing_surfaces": []}
```

### make reality.green

```json
{
  "reality_green": true,
  "checks": 18
}
```

All 18 checks passing.

---

## Files Changed

| File | Change |
|------|--------|
| `scripts/pm/generate_pm_bootstrap_state.py` | +`load_reality_green_summary()`, +`health` section, -stale `meta.dms_share_alignment` |
| `scripts/guards/guard_oa_state.py` | +tri-surface coherence enforcement (5 new checks) |
| `share/SSOT_SURFACE_V17.json` | Regenerated with `dms_share_alignment: "OK"` |
| `share/PM_BOOTSTRAP_STATE.json` | Now has `health` section derived from reality.green |
| `share/orchestrator_assistant/STATE.json` | Refreshed with current reality.green status |
| `share/REALITY_GREEN_SUMMARY.json` | Updated with all 18 checks passing |
| `share/HANDOFF_KERNEL.json` | Updated timestamps |
