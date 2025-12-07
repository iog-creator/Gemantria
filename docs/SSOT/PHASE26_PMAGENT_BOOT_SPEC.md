# PHASE26_PMAGENT_BOOT_SPEC.md — pmagent Boot & Envelope Design

**Phase**: 26.B  
**Status**: Design Complete — Implementation Pending  
**Version**: 1.0  
**Last Updated**: 2025-12-06

---

## 1. Overview

This document defines the **kernel-aware boot flows** for PM, OA, and OPS agents via new `pmagent` commands. These commands enforce **Phase 25 handoff protocol** and **Phase 26 kernel-first rules** by reading `PM_KERNEL.json` and `PM_BOOTSTRAP_STATE.json` before any work begins.

### Goals

1. **Eliminate manual  boot sequences**: Automate kernel + bootstrap reading via CLI.
2. **Enforce degraded mode**: Block normal work when `reality_green = false` or guards fail.
3. **Standardize envelopes**: Define canonical boot envelope schema consumed by PM/OA/OPS prompts.

### Non-Goals

- Implementing full envelope generation logic (future PR).
- Adding new DB queries (reuse existing DMS flows per `DMS_QUERY_PROTOCOL.md`).
- Changing kernel format (uses existing `PHASE26_HANDOFF_KERNEL.md` spec).

---

## 2. New pmagent Commands

### 2.1. `pmagent status handoff`

**Purpose**: Single command to answer "What does the kernel say right now?"

#### Behavior

**Inputs**:
- `--json`: Emit JSON output (default: human-readable)
- `--mode human|json`: Alias for `--json`

**Reads** (in order):
1. `share/handoff/PM_KERNEL.json`
2. `share/PM_BOOTSTRAP_STATE.json`
3. `share/REALITY_GREEN_SUMMARY.json` (if referenced by kernel)

**Performs**:
- Kernel ↔ bootstrap consistency check:
  - `current_phase`, `last_completed_phase`, `branch`
- File existence check for `kernel.ground_truth_files`
- No mutations — read-only command

**Outputs**:

**JSON mode** (`--json`):
```json
{
  "ok": true,
  "kernel": {
    "current_phase": "26",
    "last_completed_phase": "25",
    "branch": "feat/phase26-kernel-enforcement",
    "generated_at_utc": "2025-12-06T14:49:06Z",
    "ground_truth_files": [
      "docs/SSOT/PHASE26_INDEX.md",
      "share/PM_BOOTSTRAP_STATE.json"
    ]
  },
  "health": {
    "reality_green": true,
    "failed_checks": [],
    "source": "share/REALITY_GREEN_SUMMARY.json"
  },
  "degraded": false,
  "warnings": []
}
```

**Human mode** (default):
```
✅ Handoff Status: GREEN
   Phase: 26 (last completed: 25)
   Branch: feat/phase26-kernel-enforcement
   reality.green: PASS
   
   Next actions:
   - Review Phase 26 objectives
   - Run kernel check (make kernel.check)
```

If degraded:
```
❌ Handoff Status: DEGRADED
   Phase: 26 (last completed: 25)
   Branch: feat/phase26-kernel-enforcement
   reality.green: FAIL
   
   Failed checks:
   - DB Health (see docs/hints/HINT-DB-002-postgres-not-running.md)
   - DMS Alignment (see docs/SSOT/DMS_QUERY_PROTOCOL.md)
   
   ⚠️  Normal work blocked. Define remediation scope only.
```

#### Error Handling

- Missing kernel → `{"ok": false, "error": "PM_KERNEL.json not found", "degraded": true}`
- Missing bootstrap → warning, not fatal (kernel is primary)
- Kernel/bootstrap mismatch → `degraded: true`, emit warning

---

### 2.2. `pmagent boot pm`

**Purpose**: Automate PM handoff protocol from Phase 25 using kernel.

#### Behavior

**Inputs**:
- `--json`: Emit JSON envelope (default)
- `--mode seed|json`: 
  - `seed`: Natural-language seed for new PM chats
  - `json`: Full boot envelope

**Reads**:
1. `PM_KERNEL.json`
2. `PM_BOOTSTRAP_STATE.json`
3. `REALITY_GREEN_SUMMARY.json` (if available)

**Performs**:
- Same checks as `status handoff`
- Computes `mode: "NORMAL" | "DEGRADED"`
- Collects current phase surfaces from bootstrap
- Identifies failed guards and their doc references

**Outputs**:

**JSON mode** (`--json`, default):
```json
{
  "ok": true,
  "mode": "DEGRADED",
  "kernel": {
    "current_phase": "26",
    "last_completed_phase": "25",
    "branch": "feat/phase26-kernel-enforcement",
    "generated_at_utc": "2025-12-06T14:49:06Z",
    "ground_truth_files": [...]
  },
  "bootstrap": {
    "phases": {...},
    "current_phase_surfaces": [
      "docs/SSOT/PHASE26_INDEX.md"
    ]
  },
  "health": {
    "reality_green": false,
    "failed_checks": [
      "DB Health",
      "DMS Alignment"
    ],
    "remediation_docs": [
      "docs/hints/HINT-DB-002-postgres-not-running.md",
      "docs/SSOT/DMS_QUERY_PROTOCOL.md"
    ]
  },
  "recommended_pm_script": [
    "Explain degraded mode to the user.",
    "Do not issue destructive ops.",
    "Define remediation scope only."
  ]
}
```

**Seed mode** (`--mode seed`):
```
You are the PM of Gemantria.

Kernel says: phase 26, branch feat/phase26-kernel-enforcement, mode DEGRADED.

Failed checks:
- DB Health (see docs/hints/HINT-DB-002-postgres-not-running.md)
- DMS Alignment (see docs/SSOT/DMS_QUERY_PROTOCOL.md)

You must halt phase work and only define remediation scope until these are fixed.
```

#### Use Cases

- Orchestrator Assistant runs `pmagent boot pm --mode seed` to generate new PM chat prompts
- PM envelope generators call `pmagent boot pm --json` for structured context

---

### 2.3. `pmagent boot oa` (Optional — Design Only)

**Purpose**: Mirror `boot pm` with OA-specific behavior (focus on explaining state).

#### Behavior

**Inputs**: Same as `boot pm`

**Outputs**: JSON tailored to OA:
- Emphasizes what OA should **explain** to PM
- Which docs to read:
  - `PM_HANDOFF_PROTOCOL.md`
  - `SHARE_FOLDER_ANALYSIS.md`
  - `PHASE26_HANDOFF_KERNEL.md`
- Degraded mode:
  - Advise OA to refuse normal work
  - Help PM define remediation scope

**Implementation**: Deferred to later PR. Design sufficient for Phase 26.B.

---

## 3. Kernel Boot Envelope Schema

Defines the canonical envelope structure emitted by boot commands and consumed by agent prompts.

### 3.1. Schema Definition

```json
{
  "snapshot": {
    "generated_at_utc": "2025-12-06T14:49:06Z",
    "source": "pmagent boot pm",
    "version": "1.0"
  },
  "kernel": {
    "current_phase": "26",
    "last_completed_phase": "25",
    "branch": "feat/phase26-kernel-enforcement",
    "ground_truth_files": [
      "docs/SSOT/PHASE26_INDEX.md",
      "share/PM_BOOTSTRAP_STATE.json"
    ],
    "generated_at_utc": "2025-12-06T14:00:00Z"
  },
  "bootstrap": {
    "phases": {...},
    "current_phase_surfaces": [
      "docs/SSOT/PHASE26_INDEX.md"
    ],
    "kb_registry_path": "share/kb_registry.json"
  },
  "health": {
    "reality_green": false,
    "failed_checks": [
      "DB Health",
      "DMS Alignment"
    ],
    "remediation_docs": [
      "docs/hints/HINT-DB-002-postgres-not-running.md",
      "docs/SSOT/DMS_QUERY_PROTOCOL.md"
    ],
    "source": "share/REALITY_GREEN_SUMMARY.json"
  },
  "mode": "DEGRADED",
  "recommended_behavior": {
    "pm": [
      "Halt phase work.",
      "Define remediation scope only."
    ],
    "oa": [
      "Explain degraded mode to user.",
      "Refuse normal analysis until remediation is defined."
    ],
    "ops": [
      "Run only PM-approved remediation commands.",
      "Do not run destructive targets."
    ]
  }
}
```

### 3.2. Envelope Usage

**PM Boot Envelope**:
- Includes `mode`, `health`, `kernel.current_phase`, `kernel.branch`
- Prompt instructions:
  - If `mode == DEGRADED`: explain degraded mode + ask user for remediation scope
  - If `mode == NORMAL`: proceed to phase docs via `kernel.ground_truth_files`

**OA Boot Envelope**:
- Same data, different instructions:
  - If degraded: OA explains status + suggests minimal remediation plan
  - OA refuses to do normal RAG/analysis until health is restored

**OPS / Cursor Envelope**:
- Uses `mode` and `health` to:
  - Enforce "only remediation when degraded"
  - Cross-check with `ops.preflight.kernel_health` hint
  - Enforce DB preflight protocol (`DMS_QUERY_PROTOCOL.md`)

---

## 4. Integration with Existing Protocols

### 4.1. DB Preflight (Rule 050 + DMS_QUERY_PROTOCOL)

**Boot commands do NOT query DMS directly**:
- Only read from `share/` surfaces (kernel, bootstrap, reality green summary)
- No DB preflight needed for boot commands themselves

**Other pmagent commands that DO query DMS**:
- Must follow `DMS_QUERY_PROTOCOL.md`
- Must run `scripts/ops/preflight_db_check.py --mode strict` before querying `control.*`
- See `PREFLIGHT_DB_CHECK_ROLLOUT.md` for affected scripts

**26.B design is cleanly layered** — no conflict with DB preflight.

### 4.2. Kernel Preflight (ops.preflight.kernel_health)

**From `EXECUTION_CONTRACT.md` Section 5**:

Before destructive ops, Cursor/OPS must:
1. Read `share/handoff/PM_KERNEL.json`
2. Confirm branch matches `kernel.branch`
3. Verify DMS Alignment, Share Sync, Bootstrap Consistency, Backup guards

**Boot commands support this**:
- `pmagent status handoff` provides kernel health snapshot
- Cursor can call before destructive ops to verify `mode: NORMAL`
- Enforced via REQUIRED hint `ops.preflight.kernel_health`

### 4.3. Existing Handoff Commands

**No breaking changes**:
- `pmagent handoff generate` — Unchanged (generates handoff report)
- `pmagent handoff kernel` — Unchanged (legacy kernel generation)
- `pmagent handoff kernel-bundle` — Unchanged (generates kernel bundle)

**New commands complement existing**:
- `status handoff` reads what `kernel-bundle` writes
- `boot pm` uses output of `kernel-bundle` + `PM_BOOTSTRAP_STATE.json`

---

## 5. Implementation Notes

### 5.1. Command Stubs

Add to `pmagent/handoff/commands.py`:

```python
@app.command("status-handoff")
def handoff_status(
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    """
    Check handoff kernel health (Phase 26.B).
    
    Reads PM_KERNEL.json + PM_BOOTSTRAP_STATE.json and emits health status.
    Implementation: Phase 26.B' (TBD).
    """
    print("[TODO] pmagent status handoff not yet implemented", file=sys.stderr)
    sys.exit(1)

@app.command("boot-pm")
def boot_pm(
    mode: str = typer.Option("json", "--mode", help="Output mode: json|seed"),
) -> None:
    """
    Generate PM boot envelope (Phase 26.B).
    
    Reads kernel + bootstrap and emits boot context for PM chat initialization.
    Implementation: Phase 26.B' (TBD).
    """
    print("[TODO] pmagent boot pm not yet implemented", file=sys.stderr)
    sys.exit(1)

@app.command("boot-oa")
def boot_oa(
    mode: str = typer.Option("json", "--mode", help="Output mode: json|seed"),
) -> None:
    """
    Generate OA boot envelope (Phase 26.B — optional).
    
    Reads kernel + bootstrap and emits boot context for OA initialization.
    Implementation: Deferred.
    """
    print("[TODO] pmagent boot oa not yet implemented", file=sys.stderr)
    sys.exit(1)
```

### 5.2. Dependencies

**Reuses existing**:
- `pmagent.handoff.kernel.build_kernel()` — Load kernel data
- `share/PM_BOOTSTRAP_STATE.json` — Via `scripts/pm/generate_pm_bootstrap_state.py`
- `share/REALITY_GREEN_SUMMARY.json` — Via `scripts/guards/guard_reality_green.py`

**No new surfaces required** — all inputs already exist.

### 5.3. Testing Strategy

**Unit tests** (deferred to implementation PR):
- Mock kernel/bootstrap files
- Test consistency checks (phase mismatch, branch mismatch)
- Test degraded mode detection

**Integration tests**:
- Run `pmagent status handoff` with real kernel
- Verify JSON schema matches spec
- Test with degraded state (failing guards)

**Manual verification**:
- Generate kernel: `pmagent handoff kernel-bundle`
- Check status: `pmagent status handoff --json`
- Boot PM: `pmagent boot pm --mode seed`
- Verify output matches expected format

---

## 6. Verification Plan

Since this is **design-only**, verification is documentation review:

1. **SSOT Cross-Links**:
   - [ ] `PHASE26_INDEX.md` references this spec under 26.B
   - [ ] `PM_HANDOFF_PROTOCOL.md` compatible with boot flows
   - [ ] `SHARE_FOLDER_ANALYSIS.md` surfaces align with envelope schema

2. **Command Stubs**:
   - [ ] Added to `pmagent/handoff/commands.py`
   - [ ] Marked as `[TODO]` for implementation
   - [ ] typer signatures match spec

3. **No Breaking Changes**:
   - [ ] Existing `pmagent handoff` commands unchanged
   - [ ] No new DB queries introduced
   - [ ] Boot commands are read-only (no mutations)

---

## 7. Related Documentation

- **Phase 25**: `PM_HANDOFF_PROTOCOL.md`, `SHARE_FOLDER_ANALYSIS.md`
- **Phase 26.F**: `PHASE26_HANDOFF_KERNEL.md` (kernel format spec)
- **Phase 26.A**: `EXECUTION_CONTRACT.md` Section 5 (kernel preflight)
- **DB Preflight**: `DMS_QUERY_PROTOCOL.md`, `PREFLIGHT_DB_CHECK_ROLLOUT.md`
- **Index**: `PHASE26_INDEX.md` Section 26.B

---

## 8. Open Questions / Future Work

1. **OA boot command priority**: Defer to Phase 26.C or implement alongside PM?
2. **Envelope caching**: Should boot envelopes be cached for session reuse?
3. **Guard integration**: Should boot commands run guards directly or just read summaries?

**Decision**: For Phase 26.B design, read-only approach (consume summaries). Guards remain separate concerns run via `make reality.green`.

---

## Changelog

- **2025-12-06**: Initial design (Phase 26.B)
