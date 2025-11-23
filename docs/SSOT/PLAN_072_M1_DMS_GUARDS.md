# PLAN-072 M1: DMS Guard Fixes (Hermetic + CI-Ready)

**Status**: 📋 PLANNING/DESIGN  
**Related**: PLAN-072 (Resume Docs Management System), Rule-027 (Docs Sync Gate), Rule-055 (Auto-Docs Sync Pass), Rule-050/051/052 (OPS Contract)  
**Goal**: Ensure all DMS (Documentation Management System) guards are hermetic, pass in CI, and support HINT/STRICT modes for DB-off tolerance.

---

## Overview

PLAN-072 M1 fixes DMS-related guards to ensure they are:
1. **Hermetic** — No network/DB dependencies in PR CI (HINT mode)
2. **CI-ready** — All guards pass in default (HINT) posture
3. **Mode-aware** — Support HINT (advisory) and STRICT (fail-closed) modes
4. **Clear errors** — Emit actionable error messages when validation fails

This milestone focuses on **guard fixes only**; it does not add new DMS features or change DMS behavior.

---

## Scope: DMS Guards

### In-Scope Guards

1. **`guard_docs_consistency.py`** ✅
   - **Status**: Already hermetic, passes
   - **Action**: Verify CI wiring, add tests if missing
   - **Location**: `scripts/guards/guard_docs_consistency.py`

2. **`guard_docs_db_ssot.py`** ⚠️
   - **Status**: DB-dependent, needs HINT/STRICT mode support
   - **Action**: Add HINT/STRICT mode, ensure DB-off tolerance in HINT mode
   - **Location**: `scripts/guards/guard_docs_db_ssot.py`

3. **`guard_docs_presence.py`** (if exists)
   - **Status**: TBD (verify hermetic behavior)
   - **Action**: Ensure hermetic, add HINT/STRICT if needed
   - **Location**: `scripts/ci/guard_docs_presence.py`

4. **`guard_docs_fragments.py`** (if exists)
   - **Status**: TBD (verify hermetic behavior)
   - **Action**: Ensure hermetic, add HINT/STRICT if needed
   - **Location**: `scripts/guards/guard_doc_fragments.py`

5. **`guard_docs_embeddings.py`** (if exists)
   - **Status**: TBD (verify hermetic behavior)
   - **Action**: Ensure hermetic, add HINT/STRICT if needed
   - **Location**: `scripts/guards/guard_doc_embeddings.py`

### Out-of-Scope

- New DMS features or schema changes
- DMS ingestion logic changes
- Documentation content changes
- New guards (only fixes to existing guards)

---

## HINT vs STRICT Mode Behavior

### HINT Mode (Default / PR CI)

**Purpose**: Advisory validation that tolerates missing DB/external services.

**Behavior**:
- **DB-off tolerance**: If DB is unreachable, guard reports `mode="db_off"`, `ok=false`, but **exits 0** (non-blocking)
- **File-only validation**: Guards that can validate without DB should still run (e.g., schema validation, pattern checks)
- **Clear hints**: Emit actionable hints about what's missing or misconfigured
- **CI-friendly**: Never blocks PR CI; failures are advisory only

**Output Contract**:
```json
{
  "ok": false,
  "mode": "db_off" | "partial" | "ready",
  "reason": "human-readable explanation",
  "details": { ... },
  "hints": ["actionable hint 1", "actionable hint 2"]
}
```

**Exit Code**: Always `0` (non-blocking)

### STRICT Mode (Tag Builds / Production)

**Purpose**: Fail-closed validation that requires all components to be present and correct.

**Behavior**:
- **DB required**: If DB is unreachable, guard reports `mode="db_off"`, `ok=false`, and **exits 1** (blocking)
- **Full validation**: All checks must pass; no tolerance for missing components
- **Clear failures**: Emit specific error messages about what failed
- **Production-ready**: Blocks tag builds and production deployments

**Output Contract**:
```json
{
  "ok": false,
  "mode": "db_off" | "partial" | "ready",
  "reason": "human-readable explanation",
  "details": { ... },
  "errors": ["error 1", "error 2"]
}
```

**Exit Code**: `0` if `ok=true`, `1` if `ok=false`

### Mode Selection

- **Default (HINT)**: `STRICT_MODE` env var unset or `0`
- **STRICT**: `STRICT_MODE=1` or `STRICT_MODE=STRICT`
- **CI**: PR CI runs in HINT mode by default; tag builds run in STRICT mode

---

## Guard Contracts

### `guard_docs_consistency.py`

**Purpose**: Validate documentation consistency patterns across governance files.

**Current Status**: ✅ Hermetic, passes

**Inputs**:
- File system: `AGENTS.md`, `RULES_INDEX.md`, `GPT_REFERENCE_GUIDE.md`, `MASTER_PLAN.md`, `README.md`, `README_FULL.md`, `.cursor/rules/*.md`

**Outputs**:
- JSON verdict to stdout: `{ "scanned": int, "ok": int, "fails": int, "fail_list": [...], "errors": [...] }`
- Evidence file: `evidence/guard_docs_consistency.json` (optional)

**Mode Behavior**:
- **HINT**: Emits hints for missing/forbidden patterns, exits 0
- **STRICT**: Fails on missing/forbidden patterns, exits 1

**Make Target**: `guard.docs.consistency`

**CI Wiring**: Should run in PR CI (HINT mode)

---

### `guard_docs_db_ssot.py`

**Purpose**: Validate that control-plane doc registry in Postgres is in sync with local canonical docs.

**Current Status**: ⚠️ DB-dependent, needs HINT/STRICT mode support

**Inputs**:
- File system: Local canonical docs (via `scripts/governance/ingest_docs_to_db.py` discovery)
- Database: `control.doc_registry`, `control.doc_version` tables (via `get_control_engine()`)

**Outputs**:
- JSON verdict to stdout: `{ "ok": bool, "mode": "ready" | "db_off" | "partial", "reason": str, "details": {...} }`
- Evidence file: `evidence/guard_docs_db_ssot.json` (optional)

**Mode Behavior**:
- **HINT (DB-off)**: Reports `mode="db_off"`, `ok=false`, lists missing docs, **exits 0**
- **HINT (DB-on, partial)**: Reports `mode="partial"`, `ok=false`, lists missing docs/versions, **exits 0**
- **HINT (DB-on, sync)**: Reports `mode="ready"`, `ok=true`, **exits 0**
- **STRICT (DB-off)**: Reports `mode="db_off"`, `ok=false`, **exits 1** (blocking)
- **STRICT (DB-on, partial)**: Reports `mode="partial"`, `ok=false`, **exits 1** (blocking)
- **STRICT (DB-on, sync)**: Reports `mode="ready"`, `ok=true`, **exits 0`

**Required Changes**:
1. Add `STRICT_MODE` env var support (default: HINT)
2. Change exit code logic: exit 1 only in STRICT mode when `ok=false`
3. Add `hints` array to output when in HINT mode
4. Ensure DB connection errors are caught and handled gracefully

**Make Target**: `guard.docs.db.ssot`

**CI Wiring**: Should run in PR CI (HINT mode, non-blocking)

---

### Other DMS Guards (TBD)

**`guard_docs_presence.py`**, **`guard_docs_fragments.py`**, **`guard_docs_embeddings.py`**:
- Verify hermetic behavior (no DB/network dependencies)
- Add HINT/STRICT mode support if missing
- Ensure clear error messages
- Wire Make targets and CI

---

## Acceptance Criteria

### Overall

- ✅ All DMS guards pass in PR CI (HINT mode, non-blocking)
- ✅ All DMS guards support HINT/STRICT modes
- ✅ Guards emit clear, actionable error messages
- ✅ No external dependencies in guard execution (hermetic)
- ✅ Make targets exist for all guards
- ✅ CI wiring verified (guards run in PR CI)

### Per Guard

1. **`guard_docs_consistency.py`**:
   - ✅ Already hermetic, passes
   - ✅ Verify CI wiring
   - ✅ Add tests if missing

2. **`guard_docs_db_ssot.py`**:
   - ✅ Add HINT/STRICT mode support
   - ✅ DB-off tolerance in HINT mode (exits 0)
   - ✅ STRICT mode fails when DB-off or partial (exits 1)
   - ✅ Clear error messages and hints
   - ✅ Tests for HINT/STRICT behavior

3. **Other guards**:
   - ✅ Verify hermetic behavior
   - ✅ Add HINT/STRICT if needed
   - ✅ Tests and CI wiring

### Test Coverage

- Unit tests for each guard (HINT/STRICT modes)
- Integration tests for DB-off scenarios
- CI smoke tests (hermetic, no DB)

---

## Implementation Checklist

### Phase 1: Discovery & Assessment

- [ ] Audit all DMS guards (`scripts/guards/guard_docs*.py`, `scripts/ci/guard_docs*.py`)
- [ ] Identify which guards are DB-dependent vs. hermetic
- [ ] Document current behavior and gaps

### Phase 2: Fix `guard_docs_db_ssot.py`

- [x] Add `STRICT_MODE` env var support (default: HINT)
- [x] Update exit code logic (exit 1 only in STRICT when `ok=false`)
- [x] Add `hints` array to output in HINT mode
- [x] Ensure DB connection errors are handled gracefully
- [x] Add tests for HINT/STRICT modes
- [x] Verify Make target `guard.docs.db.ssot` works

### Phase 3: Verify Other Guards

- [ ] Verify `guard_docs_consistency.py` CI wiring
- [ ] Check `guard_docs_presence.py` hermetic behavior
- [ ] Check `guard_docs_fragments.py` hermetic behavior
- [ ] Check `guard_docs_embeddings.py` hermetic behavior
- [ ] Add HINT/STRICT mode support to any guards that need it
- [ ] Add tests for all guards

### Phase 4: CI Wiring & Documentation

- [ ] Verify all guards run in PR CI (HINT mode)
- [ ] Verify all guards run in tag builds (STRICT mode)
- [ ] Update `AGENTS.md` with guard contracts
- [ ] Update `scripts/AGENTS.md` with guard documentation
- [ ] Add guard evidence files to `.gitignore` if needed

---

## Make Targets

### Existing Targets

```makefile
guard.docs.consistency:    # Runs guard_docs_consistency.py
guard.docs.db.ssot:        # Runs guard_docs_db_ssot.py
guard.docs.presence:       # Runs scripts/ci/guard_docs_presence.py
guard.docs.fragments:      # Runs guard_doc_fragments.py (STRICT mode)
guard.docs.embeddings:     # Runs guard_doc_embeddings.py (STRICT mode)
docs.audit:                # Runs guard.docs.consistency
```

### Required Changes

- Ensure all targets support `STRICT_MODE` env var
- Document mode behavior in Makefile comments
- Add `ci.guards.docs` target that runs all DMS guards in HINT mode

---

## CI Integration

### PR CI (HINT Mode)

```yaml
# .github/workflows/ci.yml
- name: DMS Guards (HINT)
  run: |
    make guard.docs.consistency
    make guard.docs.db.ssot
    # Other DMS guards...
```

**Expected**: All guards exit 0 (non-blocking), may report `ok=false` with hints

### Tag Builds (STRICT Mode)

```yaml
# .github/workflows/tagproof.yml
- name: DMS Guards (STRICT)
  env:
    STRICT_MODE: 1
  run: |
    make guard.docs.consistency
    make guard.docs.db.ssot
    # Other DMS guards...
```

**Expected**: All guards exit 0 only if `ok=true`; failures block tag build

---

## Evidence & Artifacts

### Guard Evidence Files

- `evidence/guard_docs_consistency.json` (optional)
- `evidence/guard_docs_db_ssot.json` (optional)
- Other guard evidence files as needed

### Test Evidence

- `agentpm/tests/docs/test_guard_docs_consistency.py` (if missing)
- `agentpm/tests/docs/test_guard_docs_db_ssot.py` (new)
- Other guard tests as needed

---

## Related Documentation

- **PLAN-072**: `docs/plans/PLAN-072-resume.md` — Full PLAN-072 spec
- **PM Contract**: `docs/SSOT/PM_CONTRACT_STRICT_SSOT_DMS.md` — DMS usage in PM workflow
- **Rule-027**: `.cursor/rules/027-docs-sync-gate.mdc` — Docs sync gate requirements
- **Rule-055**: `.cursor/rules/055-auto-docs-sync.mdc` — Auto-docs sync pass
- **OPS Contract**: `.cursor/rules/050-ops-contract.mdc` — OPS v6.2.3 contract

---

## Next Steps

After PLAN-072 M1 is complete:

1. **PLAN-072 M2**: Extraction agents correctness (TVs E01–E05)
2. **PLAN-072 M3**: Visualization hooks (wire extraction → visualization)

---

## Acceptance Checklist

- [x] All DMS guards support HINT/STRICT modes (guard_docs_db_ssot.py implemented)
- [x] `guard_docs_db_ssot.py` is DB-off tolerant in HINT mode
- [ ] All guards pass in PR CI (HINT mode, non-blocking) — pending CI verification
- [x] All guards fail appropriately in STRICT mode (guard_docs_db_ssot.py verified)
- [x] Tests exist for all guards (HINT/STRICT scenarios) — test_dms_guards.py created
- [x] Make targets work for all guards (guard.docs.db.ssot, guard.docs.db.ssot.strict)
- [ ] CI wiring verified (PR CI and tag builds) — pending CI verification
- [ ] Documentation updated (`AGENTS.md`, `scripts/AGENTS.md`) — pending
- [ ] Evidence files generated and validated — pending

