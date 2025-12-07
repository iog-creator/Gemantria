# OA API Contract (Phase 27.E)

## Overview

This document defines the API contract for the Orchestrator Assistant (OA) runtime.
OA provides a normalized interface between kernel surfaces and consumers (Console v2, DSPy programs).

## Entrypoints

### 1. `pmagent oa snapshot`

Regenerates OA state from kernel surfaces.

**Usage:**
```bash
pmagent oa snapshot [--format json|text]
```

**Input:** None (reads kernel surfaces directly)

**Output (JSON):**
```json
{
  "success": true,
  "path": "share/orchestrator_assistant/STATE.json",
  "state": { ... }
}
```

**Behavior:**
1. Load `PM_BOOTSTRAP_STATE.json` → extract branch
2. Load `SSOT_SURFACE_V17.json` → extract phase info
3. Load `REALITY_GREEN_SUMMARY.json` → extract health
4. Load `share/oa/CONTEXT.json` → extract task context
5. Write normalized state to `share/orchestrator_assistant/STATE.json`

**Exit Codes:**
- `0`: Success
- `1`: Kernel surface missing or invalid

---

### 2. `pmagent boot oa` (Phase 27.B)

Boots an OA session and returns the boot envelope.

**Usage:**
```bash
pmagent boot oa [--format json|text]
```

**Output (JSON):**
```json
{
  "oa_boot_envelope": {
    "timestamp": "<ISO 8601>",
    "kernel": {
      "phase": "27",
      "branch": "main",
      "mode": "NORMAL"
    },
    "interpretation": {
      "allowed_actions": ["feature_work", "ops_blocks"],
      "forbidden_actions": [],
      "recommended_commands": []
    },
    "session_metadata": {
      "session_id": "oa-session-<uuid>",
      "workspace": "/path/to/repo"
    }
  }
}
```

---

### 3. Guard: `python scripts/guards/guard_oa_state.py`

Verifies OA state coherence with kernel surfaces.

**Usage:**
```bash
python scripts/guards/guard_oa_state.py --mode [STRICT|HINT]
```

**Output (JSON):**
```json
{
  "ok": true,
  "mode": "STRICT",
  "mismatches": [],
  "missing_surfaces": []
}
```

**Exit Codes:**
- `0`: PASS (coherent)
- `1`: FAIL (mismatch in STRICT mode)

---

## I/O Schemas for DSPy Programs

Phase 28 DSPy programs will consume OA surfaces. Here are the canonical schemas:

### SafeOPSDecision Input

```json
{
  "proposed_action": "Implement Phase 27.E",
  "kernel_state": {
    "mode": "NORMAL",
    "phase": "27",
    "branch": "feat/phase27e-oa-runtime",
    "reality_green": true
  },
  "oa_context": {
    "active_goal": "OA Runtime Enhancement",
    "constraints": ["no_db_writes", "no_git_push"]
  }
}
```

### SafeOPSDecision Output

```json
{
  "decision": "ALLOW",
  "reasoning": "Kernel is NORMAL, action is feature work, no conflicting constraints",
  "conditions": [],
  "warnings": []
}
```

### OPSBlockGenerator Input

```json
{
  "goal": "Create OA data model documentation",
  "kernel_state": { ... },
  "ssot_references": [
    "docs/SSOT/PHASE27_B_OA_RUNTIME.md",
    "docs/SSOT/PHASE27_D_DSPY_REASONING_OUTLINE.md"
  ],
  "hints": [
    { "flow_id": "docs.create", "hint": "Always update AGENTS.md" }
  ]
}
```

### OPSBlockGenerator Output

```json
{
  "ops_block": "## 🟦 OPS MODE — Create OA Data Model\n...",
  "commands": [
    "mkdir -p docs/SSOT/oa",
    "echo '...' > docs/SSOT/oa/OA_DATA_MODEL.md"
  ],
  "evidence_required": [
    "First 50 lines of OA_DATA_MODEL.md",
    "make reality.green output"
  ]
}
```

---

## Interface Boundaries

### OA Runtime Rules

1. **OA is read-only** — OA reads kernel surfaces but never modifies them directly
2. **No direct git/db** — OA does not run git or database commands
3. **Kernel-first** — OA always consults kernel state before taking action
4. **Fail-closed** — If kernel is BLOCKED, OA refuses all work

### Consumer Contracts

| Consumer | Consumes | Writes |
|----------|----------|--------|
| Console v2 | `STATE.json` | Nothing |
| DSPy Programs | `STATE.json`, `CONTEXT.json` | `CONTEXT.json` only |
| Guards | All OA surfaces | Nothing |
| PM Bootstrap | `STATE.json` (optional) | Nothing |

### Kernel Surface Contracts

OA depends on these surfaces existing:

| Surface | Required | Fallback |
|---------|----------|----------|
| `PM_BOOTSTRAP_STATE.json` | Yes | Error |
| `SSOT_SURFACE_V17.json` | Yes | Error |
| `REALITY_GREEN_SUMMARY.json` | Yes | Error |
| `share/oa/CONTEXT.json` | No | Empty context |

---

## Guard Integration

### guard_oa_state.py Checks

| Check | Description | Severity |
|-------|-------------|----------|
| Branch match | OA.branch == PM_BOOTSTRAP.branch | FAIL |
| Phase match | OA.phase == SSOT.current_phase | FAIL |
| Reality match | OA.reality_green == REALITY_GREEN | FAIL |
| Surface existence | All referenced surfaces exist | WARN |
| Context validity | `share/oa/CONTEXT.json` is valid JSON | WARN |

### Tri-Surface Coherence

The guard enforces coherence across three surfaces:
1. OA `STATE.json`
2. `REALITY_GREEN_SUMMARY.json`
3. `PM_BOOTSTRAP_STATE.json`

All three must agree on:
- `reality_green` status
- Key check statuses (AGENTS.md Sync, DMS Alignment)
- Branch and phase metadata

---

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

See [OA_TOOLS_REGISTRY.md](OA_TOOLS_REGISTRY.md) for complete specifications.

### DSPy Program → Tool Mapping

Each DSPy reasoning program (Phase 28) has access to specific tools:

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

### Example Usage (Python)

```python
from pmagent.oa.tools import kernel_status, reality_check, OAToolError

# Get kernel state before drafting OPS block
kernel = kernel_status()
if kernel["mode"] == "BLOCKED":
    raise OAToolError("Cannot proceed: kernel is BLOCKED")

# Check reality before executing
reality = reality_check()
if not reality["reality_green"]:
    print(f"Warning: {len(reality['failed_checks'])} checks failed")
```

---

## Reasoning Bridge API (Phase 27.F)

The **Reasoning Bridge** mediates interactions between OA and DSPy programs. In Phase 27.F, this exists as **contracts + scaffolding**; DSPy runtime integration occurs in Phase 28.

### Entrypoints

| Function | Purpose |
|----------|---------|
| `oa.reasoning.build_envelope(program_id, goal, ...)` | Construct a read-only `ReasoningEnvelope` from kernel state. |
| `oa.reasoning.run(envelope)` | Execute a reasoning program (STUB in 27.F). |

### Schemas

The bridge uses typed schemas defined in `pmagent/oa/reasoning_bridge.py`:

- **ReasoningEnvelope**: Immutable input (kernel state + context + goal).
- **ReasoningResult**: Structured output (decision + rationale + tools).

### Program Interactions

How OA interacts with reasoning programs via the bridge:

1. **SafeOPSDecision**
   - **Input**: Envelope with `oa.reality_summary` + `oa.kernel_status`.
   - **Output**: `SafeOPSDecisionResult` (PROCEED/ABORT).

2. **OPSBlockGenerator**
   - **Input**: Envelope with full SSOT index + bootstrap.
   - **Output**: `OPSBlockGeneratorResult` (List of CLI commands).

3. **GuardFailureInterpreter**
   - **Input**: Envelope with `oa.guard.run` permission.
   - **Output**: `GuardFailureInterpreterResult` (Remediation plan).

4. **PhaseTransitionValidator**
   - **Input**: Envelope with SSOT index + reality check.
   - **Output**: `PhaseTransitionValidatorResult` (Transition status).

---

## Future Extensions (Phase 28+)

### Planned Entrypoints

- `pmagent oa decision` — Run SafeOPSDecision reasoning (uses `oa.kernel_status`, `oa.reality_summary`)
- `pmagent oa generate` — Run OPSBlockGenerator reasoning (uses tool registry)
- `pmagent oa interpret <guard_output>` — Run GuardFailureInterpreter (uses `oa.guard.run`)

### DSPy Integration Points

DSPy programs will:
1. Read OA state via `pmagent oa snapshot --format json`
2. Invoke tools via `pmagent.oa.tools` (not arbitrary shell commands)
3. Update context via direct file write to `share/oa/CONTEXT.json`
4. Never modify kernel surfaces directly

---

## Related Documents

- [OA_TOOLS_REGISTRY.md](OA_TOOLS_REGISTRY.md) — Complete tool specifications
- [OA_DATA_MODEL.md](OA_DATA_MODEL.md) — Schema definitions
- [OA_DIAGNOSTICS_CATALOG.md](OA_DIAGNOSTICS_CATALOG.md) — Diagnostic categories
- [PHASE27_B_OA_RUNTIME.md](../PHASE27_B_OA_RUNTIME.md) — Boot sequence
- [PHASE27_D_DSPY_REASONING_OUTLINE.md](../PHASE27_D_DSPY_REASONING_OUTLINE.md) — DSPy programs
