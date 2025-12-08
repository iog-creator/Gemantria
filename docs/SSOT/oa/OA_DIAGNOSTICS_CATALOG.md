# OA Diagnostics Catalog (Phase 27.E)

## Overview

This catalog defines the diagnostic categories and reporting schema for OA state validation.
Diagnostics are produced by `guard_oa_state.py` and consumed by Console v2 and PM.

## Diagnostic Categories

### Category: `kernel_mismatch`

**Description:** OA state disagrees with kernel surfaces.

| Subcategory | Check | Severity |
|-------------|-------|----------|
| `branch_mismatch` | OA.branch != PM_BOOTSTRAP.branch | ERROR |
| `phase_mismatch` | OA.phase != SSOT.current_phase | ERROR |
| `reality_mismatch` | OA.reality_green != REALITY_GREEN | ERROR |
| `check_mismatch` | Individual check status differs | WARN |

**Remediation:** `pmagent oa snapshot`

---

### Category: `config_drift`

**Description:** Configuration surfaces have drifted from expected state.

| Subcategory | Check | Severity |
|-------------|-------|----------|
| `stale_oa_state` | STATE.json older than kernel surfaces | WARN |
| `stale_context` | CONTEXT.json has outdated kernel_mode | WARN |
| `orphan_ops_block` | Pending OPS block with no session | INFO |

**Remediation:** Regenerate OA state and context

---

### Category: `missing_surface`

**Description:** Required or optional surfaces are absent.

| Surface | Required | Severity |
|---------|----------|----------|
| `PM_BOOTSTRAP_STATE.json` | Yes | ERROR |
| `SSOT_SURFACE_V17.json` | Yes | ERROR |
| `REALITY_GREEN_SUMMARY.json` | Yes | ERROR |
| `share/oa/CONTEXT.json` | No | WARN |
| Atlas surfaces | No | INFO |

**Remediation:** Run appropriate generation commands

---

### Category: `schema_violation`

**Description:** Surface exists but fails schema validation.

| Subcategory | Check | Severity |
|-------------|-------|----------|
| `invalid_json` | Surface is not valid JSON | ERROR |
| `missing_version` | version field absent | WARN |
| `missing_required` | Required field absent | ERROR |
| `type_mismatch` | Field has wrong type | WARN |

**Remediation:** Regenerate surface or fix manually

---

### Category: `tri_surface_incoherence`

**Description:** The three authoritative surfaces disagree.

**Surfaces checked:**
1. `OA STATE.json`
2. `REALITY_GREEN_SUMMARY.json`
3. `PM_BOOTSTRAP_STATE.json`

| Check | Description | Severity |
|-------|-------------|----------|
| `reality_green_conflict` | All three must agree on reality_green | ERROR |
| `agents_sync_conflict` | AGENTS.md Sync status must match | WARN |
| `dms_alignment_conflict` | DMS Alignment status must match | WARN |
| `health_coherence` | PM_BOOTSTRAP.health must match REALITY_GREEN | ERROR |

**Remediation:** Run `make reality.green` then `pmagent oa snapshot`

---

## Diagnostic Report Schema

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "ok": { "type": "boolean" },
    "mode": { "enum": ["STRICT", "HINT"] },
    "timestamp": { "type": "string", "format": "date-time" },
    "mismatches": {
      "type": "array",
      "items": { "type": "string" }
    },
    "missing_surfaces": {
      "type": "array",
      "items": { "type": "string" }
    },
    "diagnostics": {
      "type": "array",
      "items": { "$ref": "#/definitions/diagnostic" }
    }
  },
  "required": ["ok", "mode", "mismatches", "missing_surfaces"],
  "definitions": {
    "diagnostic": {
      "type": "object",
      "properties": {
        "type": { "enum": ["issue", "warn", "blocker"] },
        "category": { "type": "string" },
        "severity": { "enum": ["info", "warn", "error", "block"] },
        "message": { "type": "string" },
        "details": { "type": "object" },
        "remediation": { "type": ["string", "null"] }
      },
      "required": ["type", "category", "severity", "message"]
    }
  }
}
```

### Example Report

```json
{
  "ok": false,
  "mode": "STRICT",
  "timestamp": "2024-12-07T15:30:00Z",
  "mismatches": [
    "branch mismatch: OA='feature-x' vs kernel='main'"
  ],
  "missing_surfaces": [],
  "diagnostics": [
    {
      "type": "issue",
      "category": "kernel_mismatch",
      "severity": "error",
      "message": "OA branch mismatches kernel branch",
      "details": {
        "oa_branch": "feature-x",
        "kernel_branch": "main"
      },
      "remediation": "pmagent oa snapshot"
    }
  ]
}
```

---

## Guard Mapping

### guard_oa_state.py → Diagnostic Categories

| Guard Check | Category |
|-------------|----------|
| OA STATE.json missing | `missing_surface` |
| PM_BOOTSTRAP missing | `missing_surface` |
| SSOT_SURFACE missing | `missing_surface` |
| REALITY_GREEN missing | `missing_surface` |
| Branch mismatch | `kernel_mismatch` |
| Phase mismatch | `kernel_mismatch` |
| Reality mismatch | `tri_surface_incoherence` |
| Health mismatch | `tri_surface_incoherence` |
| Check status mismatch | `tri_surface_incoherence` |

### guard_reality_green.py → Diagnostic Categories

| Guard Check | Category |
|-------------|----------|
| AGENTS.md Sync | `config_drift` |
| DMS Alignment | `config_drift` |
| Bootstrap Consistency | `tri_surface_incoherence` |

---

## Console v2 Integration

Console v2 displays diagnostics in the OA Status tile:

| Severity | Display |
|----------|---------|
| `block` | 🔴 Red banner, blocks workflow |
| `error` | 🟠 Orange badge with count |
| `warn` | 🟡 Yellow badge with count |
| `info` | 🔵 Blue (collapsed by default) |

---

## Related Documents

- [OA_DATA_MODEL.md](OA_DATA_MODEL.md) — Schema definitions
- [OA_API_CONTRACT.md](OA_API_CONTRACT.md) — Entrypoints and I/O
- [guard_oa_state.py](file:///home/mccoy/Projects/Gemantria.v2/scripts/guards/guard_oa_state.py) — Implementation
