# OA Tools Registry (Phase 27.E Batch 3)

## Overview

This registry defines the **explicit set of tools** that the Orchestrator Assistant (OA) is allowed
to use. Each tool wraps a pmagent command or kernel surface accessor. OA must use these wrappers
rather than arbitrary shell commands.

All tools are implemented in `pmagent/oa/tools.py` and are:
- **Read-only** — No writes to git, DB, or kernel surfaces
- **Kernel-aligned** — Use pmagent APIs, not direct subprocess calls where possible
- **DSPy-ready** — Typed interfaces suitable for DSPy program consumption (Phase 28)

---

## Tool Registry Table

| tool_id | Function | pmagent_command | Allowed Modes | Safety Notes |
|---------|----------|-----------------|---------------|--------------|
| `oa.kernel_status` | `kernel_status()` | `pmagent handoff kernel-interpret` | ALL | Read-only; returns kernel mode+health |
| `oa.reality_check` | `reality_check()` | `python scripts/guards/guard_reality_green.py` | ALL | Read-only; returns guard results |
| `oa.guard.run` | `run_guard(name)` | `python scripts/guards/guard_{name}.py` | ALL | Read-only; name must be in allowed list |
| `oa.bootstrap_state` | `get_bootstrap_state()` | Load file: `share/PM_BOOTSTRAP_STATE.json` | ALL | Read-only; returns PM boot envelope |
| `oa.ssot_surface` | `get_ssot_surface()` | Load file: `share/SSOT_SURFACE_V17.json` | ALL | Read-only; returns phase index |
| `oa.reality_summary` | `get_reality_summary()` | Load file: `share/REALITY_GREEN_SUMMARY.json` | ALL | Read-only; returns health status |
| `oa.handoff_kernel` | `get_handoff_kernel()` | Load file: `share/HANDOFF_KERNEL.json` | ALL | Read-only; returns handoff kernel bundle |

---

## Tool Specifications

### oa.kernel_status

**Purpose:** Get current kernel mode, health, and interpretation.

**Function:** `kernel_status() -> dict[str, Any]`

**pmagent Command:** `pmagent handoff kernel-interpret --format json`

**Input Schema:** None (reads kernel state directly)

**Output Schema Reference:** `KernelInterpretation` from OA_API_CONTRACT.md

```json
{
  "mode": "NORMAL",
  "health": { "overall": "green" },
  "interpretation": {
    "allowed_actions": ["feature_work", "ops_blocks"],
    "forbidden_actions": [],
    "recommended_commands": []
  }
}
```

**Allowed Modes:** `["NORMAL", "DEGRADED", "BLOCKED"]`

**Safety Notes:**
- Read-only (never modifies kernel)
- Must use pmagent CLI, not direct JSON parsing

---

### oa.reality_check

**Purpose:** Run reality.green validation and return structured results.

**Function:** `reality_check() -> dict[str, Any]`

**pmagent Command:** `python scripts/guards/guard_reality_green.py`

**Input Schema:** None

**Output Schema Reference:** `RealityCheckResult` from OA_API_CONTRACT.md

```json
{
  "reality_green": true,
  "total_checks": 18,
  "passed_checks": 18,
  "failed_checks": [],
  "checks": [
    { "name": "DB Health", "passed": true, "details": {} }
  ]
}
```

**Allowed Modes:** `["NORMAL", "DEGRADED", "BLOCKED"]`

**Safety Notes:**
- Read-only (runs guard scripts, no writes)
- May take several seconds to complete

---

### oa.guard.run

**Purpose:** Run a specific guard script and return results.

**Function:** `run_guard(name: str) -> dict[str, Any]`

**pmagent Command:** `python scripts/guards/guard_{name}.py`

**Input Schema:**
```json
{
  "name": "string (guard name, e.g., 'db_health', 'oa_state')"
}
```

**Output Schema Reference:** Guard-specific (varies by guard)

**Allowed Guard Names:**
- `db_health`
- `lm_health`
- `oa_state`
- `agents_md_sync`
- `share_sync`
- `dms_alignment`
- `bootstrap_consistency`

**Allowed Modes:** `["NORMAL", "DEGRADED", "BLOCKED"]`

**Safety Notes:**
- Only guards in allowed list can be run
- Read-only (guards are read-only by design)
- Unknown guard name raises OAToolError

---

### oa.bootstrap_state

**Purpose:** Load and return PM_BOOTSTRAP_STATE.json content.

**Function:** `get_bootstrap_state() -> dict[str, Any]`

**pmagent Command:** Load file: `share/PM_BOOTSTRAP_STATE.json`

**Input Schema:** None

**Output Schema Reference:** `PMBootstrapState` from OA_DATA_MODEL.md

**Allowed Modes:** `["NORMAL", "DEGRADED", "BLOCKED"]`

**Safety Notes:**
- Read-only (loads file, no writes)
- Returns empty dict if file missing

---

### oa.ssot_surface

**Purpose:** Load and return SSOT_SURFACE_V17.json content.

**Function:** `get_ssot_surface() -> dict[str, Any]`

**pmagent Command:** Load file: `share/SSOT_SURFACE_V17.json`

**Input Schema:** None

**Output Schema Reference:** `SSOTSurface` from OA_DATA_MODEL.md

**Allowed Modes:** `["NORMAL", "DEGRADED", "BLOCKED"]`

**Safety Notes:**
- Read-only (loads file, no writes)
- Returns empty dict if file missing

---

### oa.reality_summary

**Purpose:** Load and return REALITY_GREEN_SUMMARY.json content.

**Function:** `get_reality_summary() -> dict[str, Any]`

**pmagent Command:** Load file: `share/REALITY_GREEN_SUMMARY.json`

**Input Schema:** None

**Output Schema Reference:** `RealityGreenSummary` from OA_DATA_MODEL.md

**Allowed Modes:** `["NORMAL", "DEGRADED", "BLOCKED"]`

**Safety Notes:**
- Read-only (loads file, no writes)
- Returns empty dict if file missing

---

### oa.handoff_kernel

**Purpose:** Load and return HANDOFF_KERNEL.json content (kernel bundle for agent handoffs).

**Function:** `get_handoff_kernel() -> dict[str, Any]`

**pmagent Command:** Load file: `share/HANDOFF_KERNEL.json`

**Input Schema:** None

**Output Schema Reference:** `HandoffKernel` from OA_DATA_MODEL.md

**Allowed Modes:** `["NORMAL", "DEGRADED", "BLOCKED"]`

**Safety Notes:**
- Read-only (loads file, no writes)
- Returns empty dict if file missing
- Used for agent handoff context

---

## DSPy Program Integration

The four DSPy reasoning programs (Phase 28) will consume these tools:

| DSPy Program | OA Tools Used |
|--------------|---------------|
| **SafeOPSDecision** | `oa.kernel_status`, `oa.reality_summary` |
| **OPSBlockGenerator** | `oa.kernel_status`, `oa.ssot_surface`, `oa.bootstrap_state` |
| **GuardFailureInterpreter** | `oa.kernel_status`, `oa.guard.run` |
| **PhaseTransitionValidator** | `oa.kernel_status`, `oa.ssot_surface`, `oa.reality_check` |

---

## Forbidden Operations

OA tools MUST NOT:
- Execute arbitrary shell commands
- Write to git (no commits, pushes, or branch changes)
- Write to database (all DB access is read-only)
- Modify kernel surfaces directly
- Call pmagent commands not in this registry

Violations are detected by `guard_oa_tools.py` and block deployment.

---

## Extending the Registry

To add a new OA tool:

1. **Add to this registry** — Define tool_id, function signature, safety notes
2. **Implement wrapper** — Add function to `pmagent/oa/tools.py`
3. **Update OA state** — Add tool_id to `oa_tools.tools` list in `state.py`
4. **Run guard** — Verify with `python scripts/guards/guard_oa_tools.py`

---

## Related Documents

- [OA_API_CONTRACT.md](OA_API_CONTRACT.md) — OA entrypoints and I/O schemas
- [OA_DATA_MODEL.md](OA_DATA_MODEL.md) — Schema definitions
- [PHASE27_D_DSPY_REASONING_OUTLINE.md](../PHASE27_D_DSPY_REASONING_OUTLINE.md) — DSPy program signatures
- [guard_oa_tools.py](file:///home/mccoy/Projects/Gemantria.v2/scripts/guards/guard_oa_tools.py) — Registry/code sync guard
