# OA Data Model (Phase 27.E)

## Overview

This document defines the formal data model for the Orchestrator Assistant (OA) runtime.
OA acts as a **read-only kernel consumer**, normalizing kernel surfaces for Console v2 and
future DSPy reasoning programs.

## Core Types

### OAState (STATE.json Schema)

The primary OA state surface, written to `share/orchestrator_assistant/STATE.json`.

```json
{
  "version": 1,
  "source": "kernel",
  "generated_at": "<ISO 8601 timestamp>",
  "branch": "<current git branch>",
  "current_phase": "<current phase number>",
  "last_completed_phase": "<last completed phase>",
  "reality_green": true,
  "checks_summary": [
    { "name": "Check Name", "passed": true }
  ],
  "dms_hint_summary": {
    "total_hints": 4,
    "flows_with_hints": 2
  },
  "surfaces": {
    "pm_bootstrap_state": "share/PM_BOOTSTRAP_STATE.json",
    "ssot_surface": "share/SSOT_SURFACE_V17.json",
    "reality_green_summary": "share/REALITY_GREEN_SUMMARY.json"
  },
  "surface_status": {
    "pm_bootstrap_state": true,
    "ssot_surface": true
  },
  "oa_context": {}
}
```

| Field | Type | Source |
|-------|------|--------|
| `version` | int | Hardcoded (schema version) |
| `source` | string | Always `"kernel"` |
| `generated_at` | ISO 8601 | Runtime timestamp |
| `branch` | string | `PM_BOOTSTRAP_STATE.json` |
| `current_phase` | string | `SSOT_SURFACE_V17.json` |
| `last_completed_phase` | string | `SSOT_SURFACE_V17.json` |
| `reality_green` | bool | `REALITY_GREEN_SUMMARY.json` |
| `checks_summary` | array | Normalized from reality checks |
| `dms_hint_summary` | object | Extracted from DMS Hint check |
| `surfaces` | object | Repo-relative paths |
| `surface_status` | object | Existence checks |
| `oa_context` | object | From `share/oa/CONTEXT.json` |

---

### OAContext (CONTEXT.json Schema)

The OA context surface provides task-level state for DSPy programs.
Location: `share/oa/CONTEXT.json`

```json
{
  "version": 1,
  "context": {
    "active_goal": null,
    "kernel_mode": "NORMAL",
    "constraints": [],
    "pending_ops_blocks": [],
    "session_metadata": {}
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `version` | int | Schema version |
| `context.active_goal` | string\|null | Current PM goal (if any) |
| `context.kernel_mode` | string | Derived from kernel interpret |
| `context.constraints` | array[string] | Active constraints/hints |
| `context.pending_ops_blocks` | array[string] | OPS blocks awaiting execution |
| `context.session_metadata` | object | Ephemeral session info |

---

### OADiagnostic

Structured diagnostic output for guard failures and issues.

```json
{
  "type": "issue",
  "category": "kernel_mismatch",
  "severity": "warn",
  "message": "OA branch mismatches kernel branch",
  "details": {
    "oa_branch": "feature-x",
    "kernel_branch": "main"
  },
  "remediation": "Run: pmagent oa snapshot"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | enum | `issue`, `warn`, `blocker` |
| `category` | string | Diagnostic category (see catalog) |
| `severity` | enum | `info`, `warn`, `error`, `block` |
| `message` | string | Human-readable description |
| `details` | object | Diagnostic-specific data |
| `remediation` | string\|null | Suggested fix command |

---

## Workspace Surfaces

OA manages these surfaces under `share/orchestrator_assistant/`:

| Surface | Purpose |
|---------|---------|
| `STATE.json` | Primary OA state (normalized kernel view) |
| `NOTES.md` | OA research notes and observations |
| `DECISION_LOG.json` | Structured decision records |
| `RESEARCH_INDEX.md` | Links to relevant SSOT docs |
| `ACTIVE_PROMPTS.md` | Current conversation anchors |

Additional surfaces under `share/oa/`:

| Surface | Purpose |
|---------|---------|
| `CONTEXT.json` | Task context for DSPy programs |

---

## Kernel Surface References

OA reads (but never writes) these kernel surfaces:

| Surface | Purpose | Used For |
|---------|---------|----------|
| `PM_BOOTSTRAP_STATE.json` | PM boot envelope | branch, phase discovery |
| `SSOT_SURFACE_V17.json` | Phase index | current_phase, last_completed |
| `REALITY_GREEN_SUMMARY.json` | Health status | reality_green, checks_summary |
| `HANDOFF_KERNEL.json` | Kernel bundle | Mode, hints, constraints |

---

## Invariants

1. **OA is read-only**: OA never modifies kernel surfaces directly
2. **Kernel-first**: OA state is always derived from kernel surfaces
3. **Coherence**: OA state must match kernel (enforced by guard_oa_state.py)
4. **Versioned schemas**: All OA surfaces include schema version
5. **ISO 8601 timestamps**: All timestamps use ISO 8601 format

---

## Related Documents

- [OA_API_CONTRACT.md](OA_API_CONTRACT.md) — OA entrypoints and I/O
- [OA_DIAGNOSTICS_CATALOG.md](OA_DIAGNOSTICS_CATALOG.md) — Diagnostic categories
- [PHASE27_B_OA_RUNTIME.md](../PHASE27_B_OA_RUNTIME.md) — OA boot sequence spec
- [PHASE27_D_DSPY_REASONING_OUTLINE.md](../PHASE27_D_DSPY_REASONING_OUTLINE.md) — DSPy program signatures
