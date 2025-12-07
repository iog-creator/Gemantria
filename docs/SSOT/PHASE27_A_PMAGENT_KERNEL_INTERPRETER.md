# PHASE27_A_PMAGENT_KERNEL_INTERPRETER.md — pmagent as Default Kernel Interpreter

## Problem Statement

Phase 26 established that the kernel **must be checked**, but doesn't specify what to **do** with the kernel data.

Currently:
- `pmagent status handoff` dumps JSON
- PM manually reads `mode: NORMAL` or `mode: DEGRADED`
- Cursor receives kernel status but doesn't derive behavior
- No canonical "kernel interpreter" that says "given this state, do this"

**Result:** Kernel is a data surface, not a behavioral contract.

---

## Objectives

Transform `pmagent` from a data loader into a **kernel interpreter** that:

1. **Reads kernel state** (`PM_KERNEL.json` + `PM_BOOTSTRAP_STATE.json`)
2. **Interprets mode semantics** (NORMAL/DEGRADED/BLOCKED)
3. **Returns actionable directives**:
   - "Feature work allowed"
   - "Remediation only"
   - "Run these commands to fix degraded state"
   - "Escalate to PM"

---

## Mode Semantics Matrix

| Mode | Health Status | Allowed Actions | Forbidden Actions | Escalation |
|------|---------------|-----------------|-------------------|------------|
| **NORMAL** | All guards green | Feature work, OPS blocks, migrations | None (all actions allowed) | None |
| **DEGRADED** | 1+ guards yellow/red | Remediation commands only | Feature work, schema changes, new phases | Warn PM on boot |
| **BLOCKED** | Critical failure | Diagnostic commands only | All destructive ops | Block work, escalate immediately |

### Mode Definitions

- **NORMAL**: Standard operating mode
  - `reality.green` passes
  - DMS aligned
  - Backups fresh
  - Share sync clean
  
- **DEGRADED**: Partial system health
  - 1+ guards failed but system usable
  - Can run remediation (e.g., `make housekeeping`, `make backup`)
  - Cannot start new feature work
  
- **BLOCKED**: Critical system failure
  - Kernel missing or corrupted
  - Database unreachable
  - Major SSOT inconsistency
  - Only diagnostic commands allowed

---

## Command Design: `pmagent kernel interpret`

### Signature

```bash
pmagent kernel interpret [--format json|human]
```

### Inputs (Auto-Read)

- `share/handoff/PM_KERNEL.json`
- `share/handoff/PM_BOOTSTRAP_STATE.json`
- Guard outputs (if available):
  - `make reality.green` status
  - `make ops.kernel.check` status
  - Individual guard outputs

### Output Schema (JSON)

```json
{
  "kernel_version": "2024-12-06T15:30:00Z",
  "mode": "NORMAL" | "DEGRADED" | "BLOCKED",
  "health": {
    "overall": "green" | "yellow" | "red",
    "guards": {
      "reality_green": "pass" | "warn" | "fail",
      "dms_alignment": "pass" | "warn" | "fail",
      "backup_fresh": "pass" | "warn" | "fail",
      "share_sync": "pass" | "warn" | "fail"
    }
  },
  "interpretation": {
    "summary": "System is healthy. Feature work allowed.",
    "allowed_actions": [
      "feature_work",
      "ops_blocks",
      "migrations",
      "phase_transitions"
    ],
    "forbidden_actions": [],
    "recommended_commands": []
  },
  "escalation": {
    "required": false,
    "reason": null,
    "severity": "none" | "warn" | "block"
  }
}
```

### Example Output (NORMAL Mode)

```json
{
  "mode": "NORMAL",
  "health": {"overall": "green", "guards": {"reality_green": "pass"}},
  "interpretation": {
    "summary": "All systems green. Proceed with planned work.",
    "allowed_actions": ["feature_work", "ops_blocks", "migrations"],
    "forbidden_actions": [],
    "recommended_commands": []
  },
  "escalation": {"required": false, "severity": "none"}
}
```

### Example Output (DEGRADED Mode)

```json
{
  "mode": "DEGRADED",
  "health": {
    "overall": "yellow",
    "guards": {
      "reality_green": "fail",
      "dms_alignment": "pass",
      "backup_fresh": "warn"
    }
  },
  "interpretation": {
    "summary": "System degraded: reality.green failed. Remediation required before feature work.",
    "allowed_actions": ["remediation", "diagnostic"],
    "forbidden_actions": ["feature_work", "migrations", "phase_transitions"],
    "recommended_commands": [
      "make housekeeping",
      "make reality.green",
      "pmagent status handoff"
    ]
  },
  "escalation": {
    "required": true,
    "reason": "reality.green failed: 3 lint errors, 1 missing hint",
    "severity": "warn"
  }
}
```

### Human-Readable Output (`--format human`)

```
Kernel Interpretation (2024-12-06T15:30:00Z)
===========================================

Mode:        DEGRADED
Health:      YELLOW (⚠️)

Guard Status:
  ✅ DMS Alignment:  PASS
  ❌ Reality Green:  FAIL (3 lint errors, 1 missing hint)
  ⚠️  Backup Fresh:   WARN (last backup 25h ago)

Allowed Actions:
  - Remediation commands
  - Diagnostic queries

Forbidden Actions:
  - Feature work
  - Schema migrations
  - Phase transitions

Recommended Next Steps:
  1. Run: make housekeeping
  2. Run: make reality.green
  3. Verify: pmagent status handoff

Escalation: ⚠️ WARN
Reason: System degraded, remediation required before feature work.
```

---

## Integration Points

### 1. `make ops.kernel.check`

**Before (Phase 26):**
```bash
make ops.kernel.check
# Output: "Kernel exists, mode=NORMAL" (raw data)
```

**After (Phase 27.A):**
```bash
make ops.kernel.check
# Internally calls: pmagent kernel interpret --format human
# Output: Full interpretation with allowed/forbidden actions
```

### 2. OA Boot Sequence

**OA startup:**
```python
# OA runtime calls:
result = subprocess.run(["pmagent", "kernel", "interpret", "--format", "json"], capture_output=True)
interpretation = json.loads(result.stdout)

if interpretation["mode"] == "DEGRADED":
    notify_pm(f"⚠️ System degraded: {interpretation['escalation']['reason']}")
    refuse_feature_work()
elif interpretation["mode"] == "BLOCKED":
    notify_pm(f"🛑 System blocked: {interpretation['escalation']['reason']}")
    shutdown()
else:
    proceed_normally()
```

### 3. Console V2 Kernel Panel

**Console queries:**
```typescript
// Console Kernel Panel fetches:
const interpretation = await fetch('/api/kernel/interpret').then(r => r.json());

// Display:
// - Mode badge (green/yellow/red)
// - Health summary
// - Allowed/forbidden actions
// - Recommended commands (as clickable buttons)
```

---

## Implementation Plan

### File Structure

```
pmagent/
  kernel/
    __init__.py
    interpreter.py         # Core interpretation logic
    mode_semantics.py      # Mode definitions + rules
  cli.py                   # Add 'kernel interpret' subcommand
  
scripts/
  guards/
    guard_kernel_boot.py   # Update to use pmagent kernel interpret
```

### Core Logic (`interpreter.py`)

```python
from typing import Literal, TypedDict
from pathlib import Path
import json

Mode = Literal["NORMAL", "DEGRADED", "BLOCKED"]
Health = Literal["green", "yellow", "red"]
GuardStatus = Literal["pass", "warn", "fail"]

class Interpretation(TypedDict):
    mode: Mode
    health: dict
    interpretation: dict
    escalation: dict

def interpret_kernel() -> Interpretation:
    """
    Main entry point for kernel interpretation.
    
    Reads:
    - share/handoff/PM_KERNEL.json
    - share/handoff/PM_BOOTSTRAP_STATE.json
    - Guard outputs (if available)
    
    Returns:
    - Interpretation dict with mode, health, allowed actions, escalation
    """
    kernel = load_kernel()
    bootstrap = load_bootstrap_state()
    guards = check_guards()
    
    mode = determine_mode(kernel, bootstrap, guards)
    health = assess_health(guards)
    allowed, forbidden = derive_actions(mode, health)
    commands = recommend_commands(mode, guards)
    escalation = determine_escalation(mode, health, guards)
    
    return {
        "mode": mode,
        "health": health,
        "interpretation": {
            "summary": generate_summary(mode, health),
            "allowed_actions": allowed,
            "forbidden_actions": forbidden,
            "recommended_commands": commands
        },
        "escalation": escalation
    }
```

### CLI Wiring (`cli.py`)

```python
@cli.group()
def kernel():
    """Kernel management commands."""
    pass

@kernel.command()
@click.option("--format", type=click.Choice(["json", "human"]), default="human")
def interpret(format: str):
    """Interpret kernel state and return actionable directives."""
    from pmagent.kernel.interpreter import interpret_kernel
    from pmagent.kernel.formatters import format_interpretation
    
    interpretation = interpret_kernel()
    output = format_interpretation(interpretation, format)
    click.echo(output)
```

---

## Testing Strategy

### Test Vectors

**TV-27A-01: NORMAL Mode (All Guards Green)**
- Input: `PM_KERNEL.json` with `mode: NORMAL`, all guards pass
- Expected: `mode=NORMAL`, `allowed_actions=["feature_work", "ops_blocks"]`, `escalation.required=false`

**TV-27A-02: DEGRADED Mode (reality.green Failed)**
- Input: `PM_KERNEL.json` with `mode: NORMAL`, `reality.green` fails
- Expected: `mode=DEGRADED`, `forbidden_actions=["feature_work"]`, `recommended_commands=["make housekeeping"]`, `escalation.required=true`

**TV-27A-03: BLOCKED Mode (Kernel Missing)**
- Input: `PM_KERNEL.json` missing or corrupted
- Expected: `mode=BLOCKED`, `allowed_actions=["diagnostic"]`, `escalation.severity="block"`

**TV-27A-04: Human Format Output**
- Input: `--format human`, mode=DEGRADED
- Expected: Multi-line human-readable output with emoji indicators

### Integration Tests

- `make ops.kernel.check` calls `pmagent kernel interpret` successfully
- OA boot sequence reacts correctly to DEGRADED mode
- Console Kernel Panel displays interpretation (manual verification)

---

## Success Criteria

27.A is DONE when:

1. ✅ `pmagent kernel interpret` command exists
2. ✅ JSON and human output formats work
3. ✅ Mode semantics correctly determine allowed/forbidden actions
4. ✅ All test vectors pass
5. ✅ `make ops.kernel.check` uses interpreter
6. ✅ Documentation updated (`AGENTS.md`, this spec merged to `docs/SSOT/`)

---

## Open Questions for PM

1. **BLOCKED Mode Triggers:**
   - Should BLOCKED mode be auto-detected (e.g., kernel missing), or manually set?
   - Recommendation: Auto-detect for Phase 27, manual override in Phase 28.

2. **Guard Polling:**
   - Should `pmagent kernel interpret` re-run guards, or trust cached results?
   - Recommendation: Trust cached guard outputs for performance, re-run on explicit `--fresh` flag.

3. **Escalation Notifications:**
   - Should escalation trigger automatic PM notifications (e.g., email, Slack)?
   - Recommendation: Defer to Phase 28; Phase 27 just returns escalation data.

---

## Dependencies

- Phase 26: Kernel enforcement complete
- `pmagent status handoff` command exists
- Guard scripts (`guard_kernel_boot.py`, etc.) operational
- `PM_KERNEL.json` and `PM_BOOTSTRAP_STATE.json` format stable

---

## PM Approval Required

Before implementation:
- PM reviews this spec
- PM approves mode semantics matrix
- PM resolves open questions
- PM confirms success criteria
