# Phase 27.E Batch 3 — OA Tooling Interface Standardization

## Status

✅ **COMPLETE** — All deliverables implemented and verified.

- **Branch:** `feat/phase27l-agents-dms-contract`
- **Commit:** `8573a435 feat(27.E): OA tooling interface standardization (Phase 27.E Batch 3)`
- **Reality Green:** 18/18 checks passing

---

## Summary

This batch standardized the OA tooling interface by:

1. Creating explicit tool registry documentation
2. Implementing thin Python wrappers for pmagent commands
3. Updating OA API contract with tools interface section
4. Adding tools catalog to OA state for DSPy discovery
5. Creating guard for registry/code sync verification

---

## Evidence

### 1. OA_TOOLS_REGISTRY.md (First ~80 Lines)

```markdown
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
```

---

### 2. OA_API_CONTRACT.md — OA Tools Interface Section

```markdown
## OA Tools Interface (Phase 27.E Batch 3)

OA invokes pmagent commands exclusively through the **OA Tools API** defined in
`pmagent/oa/tools.py`. OA must not call arbitrary shell commands.

### Available Tools

| tool_id | Function | Purpose |
|---------|----------|---------|
| `oa.kernel_status` | `kernel_status()` | Get kernel mode, health, interpretation |
| `oa.reality_check` | `reality_check()` | Get normalized reality check results |
| `oa.guard.run` | `run_guard(name)` | Run a specific guard script |
| `oa.bootstrap_state` | `get_bootstrap_state()` | Load PM_BOOTSTRAP_STATE.json |
| `oa.ssot_surface` | `get_ssot_surface()` | Load SSOT_SURFACE_V17.json |
| `oa.reality_summary` | `get_reality_summary()` | Load REALITY_GREEN_SUMMARY.json |
| `oa.handoff_kernel` | `get_handoff_kernel()` | Load HANDOFF_KERNEL.json |

### DSPy Program → Tool Mapping

| DSPy Program | Tools Used |
|--------------|------------|
| **SafeOPSDecision** | `oa.kernel_status`, `oa.reality_summary` |
| **OPSBlockGenerator** | `oa.kernel_status`, `oa.ssot_surface`, `oa.bootstrap_state` |
| **GuardFailureInterpreter** | `oa.kernel_status`, `oa.guard.run` |
| **PhaseTransitionValidator** | `oa.kernel_status`, `oa.ssot_surface`, `oa.reality_check` |

### Invocation Contract

1. **All tool invocations go via `pmagent.oa.tools` wrappers**
2. OA must not call arbitrary `subprocess.run()` or shell commands
3. Tools are pure read-only — no writes to git, DB, or kernel surfaces
4. Unknown tool IDs raise `OAToolError`
```

---

### 3. pmagent/oa/tools.py (First ~100 Lines)

```python
#!/usr/bin/env python3
"""
OA Tools Interface (Phase 27.E Batch 3)

Thin, typed wrappers for pmagent commands that OA is allowed to invoke.
All functions are pure read-only; no DSPy imports.

OA must use these wrappers rather than arbitrary shell commands.
Each function corresponds 1:1 with an entry in docs/SSOT/oa/OA_TOOLS_REGISTRY.md.

Safety constraints:
- No writes to git, DB, or kernel surfaces
- No direct subprocess calls except via existing pmagent helpers
- All functions return typed dict structures for DSPy consumption
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


# Paths relative to repo root
ROOT = Path(__file__).resolve().parents[2]
SHARE = ROOT / "share"

# Kernel surface paths
PM_BOOTSTRAP_STATE = SHARE / "PM_BOOTSTRAP_STATE.json"
SSOT_SURFACE = SHARE / "SSOT_SURFACE_V17.json"
REALITY_GREEN_SUMMARY = SHARE / "REALITY_GREEN_SUMMARY.json"
HANDOFF_KERNEL = SHARE / "HANDOFF_KERNEL.json"

# Guards directory
GUARDS_DIR = ROOT / "scripts" / "guards"

# Allowed guard names for oa.guard.run
ALLOWED_GUARDS = frozenset({
    "db_health",
    "lm_health",
    "oa_state",
    ...
})


class OAToolError(Exception):
    """Raised when an OA tool invocation fails."""
    pass


def kernel_status() -> dict[str, Any]:
    """
    OA tool: oa.kernel_status

    Get current kernel mode, health, and interpretation.
    Wraps `pmagent handoff kernel-interpret --format json`.
    """
    ...

def reality_check() -> dict[str, Any]:
    """
    OA tool: oa.reality_check

    Run reality.green validation and return structured results.
    """
    ...

def run_guard(name: str) -> dict[str, Any]:
    """
    OA tool: oa.guard.run

    Run a specific guard script and return results.
    Only guards in ALLOWED_GUARDS can be run.
    """
    ...
```

---

### 4. OA State — `oa_tools` Section

From `share/orchestrator_assistant/STATE.json`:

```json
{
  "version": 1,
  "source": "kernel",
  "generated_at": "2025-12-07T22:38:52.xxx+00:00",
  "branch": "feat/phase27l-agents-dms-contract",
  "current_phase": "24",
  "reality_green": true,
  "oa_context": {
    "active_goal": null,
    "kernel_mode": null,
    "constraints": [],
    "pending_ops_blocks": [],
    "session_metadata": {}
  },
  "oa_tools": {
    "version": 1,
    "tools": [
      "oa.kernel_status",
      "oa.reality_check",
      "oa.guard.run",
      "oa.bootstrap_state",
      "oa.ssot_surface",
      "oa.reality_summary",
      "oa.handoff_kernel"
    ],
    "interface": "pmagent.oa.tools",
    "registry": "docs/SSOT/oa/OA_TOOLS_REGISTRY.md"
  }
}
```

---

### 5. Guard Output

```
[guard_oa_tools] Mode: HINT
[guard_oa_tools] Registry tools: 7
[guard_oa_tools] Module tools: 7
[guard_oa_tools] ✅ OA Tools registry in sync with implementation
{
  "ok": true,
  "mode": "HINT",
  "issues": [],
  "details": {
    "registry_tools": [
      "oa.bootstrap_state",
      "oa.guard.run",
      "oa.handoff_kernel",
      "oa.kernel_status",
      "oa.reality_check",
      "oa.reality_summary",
      "oa.ssot_surface"
    ],
    "registry_count": 7,
    "module_tools": [
      "oa.bootstrap_state",
      "oa.guard.run",
      "oa.handoff_kernel",
      "oa.kernel_status",
      "oa.reality_check",
      "oa.reality_summary",
      "oa.ssot_surface"
    ],
    "module_count": 7
  }
}
```

---

### 6. Reality Green Health

```
✅ REALITY GREEN: All checks passed - system is ready

This system is up to date and consistent for the next agent.
DB is healthy, AGENTS.md is synced, share/ is synced, exports are present.

📄 Full details: share/REALITY_GREEN_SUMMARY.json

✅ PASSED:
   • DB Health
   • Control-Plane Health
   • AGENTS.md Sync
   • Share Sync & Exports
   • Ledger Verification
   • Ketiv-Primary Policy
   • DMS Hint Registry
   • Repo Alignment (Layer 4)
   • DMS Alignment
   • DMS Metadata
   • AGENTS–DMS Contract
   • Bootstrap Consistency
   • Root Surface
   • Share Sync Policy
   • Backup System
   • WebUI Shell Sanity
   • OA State
   • Handoff Kernel

📊 STATUS: 18/18 checks passed
```

---

### 7. Git Status

```
$ git log -1 --oneline
8573a435 (HEAD -> feat/phase27l-agents-dms-contract) feat(27.E): OA tooling interface standardization (Phase 27.E Batch 3)

$ git status -sb
## feat/phase27l-agents-dms-contract
 M scripts/governance/ingest_docs_to_db.py
```

---

## Files Changed

| File | Change |
|------|--------|
| [OA_TOOLS_REGISTRY.md](file:///home/mccoy/Projects/Gemantria.v2/docs/SSOT/oa/OA_TOOLS_REGISTRY.md) | NEW — Tool specifications |
| [tools.py](file:///home/mccoy/Projects/Gemantria.v2/pmagent/oa/tools.py) | NEW — Python wrappers |
| [OA_API_CONTRACT.md](file:///home/mccoy/Projects/Gemantria.v2/docs/SSOT/oa/OA_API_CONTRACT.md) | MODIFIED — Added Tools Interface section |
| [state.py](file:///home/mccoy/Projects/Gemantria.v2/pmagent/oa/state.py) | MODIFIED — Added oa_tools to state |
| [guard_oa_tools.py](file:///home/mccoy/Projects/Gemantria.v2/scripts/guards/guard_oa_tools.py) | NEW — Registry/code sync guard |
| [AGENTS.md](file:///home/mccoy/Projects/Gemantria.v2/pmagent/oa/AGENTS.md) | NEW — Module documentation |

---

## Next Steps

**Phase 27.E (OA Runtime Enhancement) is COMPLETE.**

Ready for **Phase 28 — DSPy Implementation**:
- Kernel + OA + Console green and coherent
- OA runtime documented (data model, API, diagnostics)
- OA tools interface standardized and ready as DSPy execution substrate
