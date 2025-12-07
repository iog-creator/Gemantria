# PHASE26_PHASE_DONE_PLAN.md — Phase-DONE Enforcement for Kernel-First Handoff

**Phase**: 26.E  
**Status**: Design Complete — Implementation Pending  
**Version**: 1.0  
**Last Updated**: 2025-12-06

---

## 1. Overview

This document defines the **Phase-DONE checklist** for Phase 26 (Kernel-First Enforcement & Agent Boot Automation). It specifies what must be true to declare Phase 26 complete and what can be deferred to later phases.

### Goals

1. **Define completion criteria**: Clear, testable checklist for Phase 26 closure
2. **Enforce kernel-first behavior**: Ensure all design specs are implemented and enforced
3. **Draw boundaries**: Explicitly defer non-critical items to Phase 27+

### Non-Goals

- Implementing all checklist items (this is the plan, not the implementation)
- Defining Phase 27 scope (defer to future planning)

---

## 2. Phase-DONE Checklist (Required for Phase 26 Closure)

### 2.1. Kernel Bundle Health

**Status Check**:
```bash
make kernel.check
```

**Required**:
- [ ] `pmagent handoff kernel-bundle` generates `PM_KERNEL.json` + `PM_SUMMARY.md`
- [ ] Kernel surfaces exist and are valid (via `guard_kernel_surfaces.py`)
- [ ] Kernel ↔ bootstrap consistency verified
- [ ] `PHASE26_INDEX.md` matches kernel state

**Enforcement**: `make kernel.check` must pass in CI before merge

---

### 2.2. Hints Installed

**Status Check**:
```bash
psql "$GEMATRIA_DSN" -c "SELECT logical_name, kind, enabled FROM control.hint_registry WHERE logical_name LIKE '%boot.kernel_first' OR logical_name LIKE '%preflight.kernel_health';"
```

**Required**:
- [ ] `pm.boot.kernel_first` hint exists and enabled
- [ ] `oa.boot.kernel_first` hint exists and enabled  
- [ ] `ops.preflight.kernel_health` hint exists and enabled
- [ ] All hints reference correct SSOT docs in payload

**Enforcement**: Guard script checks hint registry for required entries

---

### 2.3. pmagent Boot Flows Wired

**Status Check**:
```bash
pmagent handoff status-handoff --json
pmagent handoff boot-pm --mode seed
```

**Required**:
- [ ] `pmagent status handoff` command implemented
- [ ] `pmagent boot pm` command implemented
- [ ] Both return envelope schema from `PHASE26_PMAGENT_BOOT_SPEC.md`
- [ ] Envelope includes: kernel, bootstrap, health, mode

**Enforcement**: Smoke test runs both commands and validates JSON schema

---

### 2.4. OA Behavior Grounded

**Status Check**:
```bash
grep -r "PHASE26_OA_BOOT_SPEC" share/orchestrator_assistant/ pmagent/ || echo "Not yet referenced"
```

**Required**:
- [ ] OA system prompts reference `PHASE26_OA_BOOT_SPEC.md`
- [ ] OA instructions include NORMAL vs DEGRADED behavior
- [ ] OA boot envelope integration documented

**Enforcement**: Manual review of OA configuration

**Note**: Full OA implementation may be deferred, but grounding (referencing the spec) is required.

---

### 2.5. OPS Behavior Grounded

**Status Check**:
```bash
grep "PHASE26_OPS_BOOT_SPEC" docs/SSOT/EXECUTION_CONTRACT.md
```

**Required**:
- [ ] `EXECUTION_CONTRACT.md` Section 5 references `PHASE26_OPS_BOOT_SPEC.md`
- [ ] DB preflight rollout complete for high-priority scripts
- [ ] Guards integrated with `make reality.green`

**Enforcement**: Documentation review + DB preflight script count

---

### 2.6. Reality.Green + Kernel Integration

**Status Check**:
```bash
make reality.green STRICT
pmagent handoff kernel-bundle
git diff --exit-code share/handoff/
```

**Required**:
- [ ] `make reality.green` passes in STRICT mode
- [ ] Kernel bundle regeneration is idempotent
- [ ] No uncommitted changes to kernel surfaces after regeneration

**Enforcement**: CI runs `reality.green` + kernel bundle stability check

---

## 3. Optional Items (Deferred to Phase 27+)

These enhance kernel-first enforcement but are NOT required for Phase 26 closure:

### 3.1. Pre-Commit Hooks

**Status**: Deferred

```bash
# .git/hooks/pre-commit (future work)
pmagent status handoff --json | jq -e '.mode == "NORMAL"'
```

**Why deferred**: Adds friction to development workflow. Better to stabilize base enforcement first.

---

### 3.2. OPS Wrapper Commands

**Status**: Deferred

```bash
# ops-guarded-make (future work)
ops-guarded-make share.sync
```

**Why deferred**: Implementation requires wrapper infrastructure not critical for Phase 26.

---

### 3.3. Emergency Override Procedures

**Status**: Deferred to Ops Runbooks

**Examples**:
- Critical production fixes while degraded
- Kernel override for emergency patches

**Why deferred**: Edge cases that need operational experience to define properly.

---

### 3.4. Full OA/OPS Implementation

**Status**: Partially deferred

**Phase 26 requires**:
- Grounding (specs referenced)
- Design complete

**Phase 27+ may include**:
- Full OA chat integration
- Wrapper command ecosystem
- Pre-commit enforcement

---

## 4. Enforcement Mechanisms

### 4.1. CI Integration

**Target**: `.github/workflows/reality-green.yml` (or equivalent)

**Steps**:
1. Run `make reality.green STRICT`
2. Run `make kernel.check`
3. Verify hint registry entries
4. Smoke test `pmagent` boot commands

**Fail conditions**:
- Any guard fails in STRICT mode
- Kernel surfaces missing or inconsistent
- Required hints not found
- Boot commands fail or return malformed JSON

---

### 4.2. Guard Scripts

**New Guard**: `scripts/guards/guard_phase26_complete.py`

**Checks**:
- Kernel bundle exists and valid
- Hints installed and enabled
- Boot commands functional
- SSOT docs cross-referenced

**Modes**:
- `HINT`: Warn if incomplete
- `STRICT`: Fail if incomplete (CI use)

---

### 4.3. Make Targets

```makefile
.PHONY: phase26.check
phase26.check: kernel.check reality.green
	@echo "Checking Phase 26 completion..."
	@python scripts/guards/guard_phase26_complete.py --mode STRICT
	@pmagent handoff status-handoff --json | jq -e '.ok == true'
	@echo "✅ Phase 26 checks passed"

.PHONY: phase26.done
phase26.done: phase26.check
	@echo "Phase 26 complete. Ready for handoff."
```

---

## 5. Validation & Testing

### 5.1. Smoke Tests

```bash
# Test 1: Kernel bundle generation
pmagent handoff kernel-bundle
test -f share/handoff/PM_KERNEL.json
test -f share/handoff/PM_SUMMARY.md

# Test 2: Status handoff
pmagent handoff status-handoff --json | jq -e '.kernel.current_phase'

# Test 3: Boot PM
pmagent handoff boot-pm --mode seed | grep -q "Kernel says"

# Test 4: Hints exist
psql "$GEMATRIA_DSN" -c "SELECT COUNT(*) FROM control.hint_registry WHERE logical_name LIKE '%kernel%'" | grep -q "3"
```

### 5.2. Integration Tests

- Generate kernel with failing guards → verify DEGRADED mode
- Fix guards → verify mode transitions to NORMAL
- Regenerate kernel multiple times → verify idempotency

---

## 6. Rollout Strategy

### Phase 1: Design Complete ✅
- All spec docs exist
- Cross-references in place
- Index updated

### Phase 2: Core Implementation (26.A'/B'/C'/D')
- Install hints in registry
- Implement `pmagent` boot commands
- Wire OA/OPS references
- Create guard scripts

### Phase 3: Enforcement Active
- CI runs `make phase26.check`
- Guards fail PRs if checklist incomplete
- Kernel bundle in CI build artifacts

### Phase 4: Operational (Phase 27+)
- Pre-commit hooks (optional)
- Wrapper commands (optional)
- Emergency procedures (ops runbooks)

---

## 7. Success Criteria

Phase 26 is **DONE** when:

1. ✅ All 6 required checklist items pass
2. ✅ `make phase26.check` passes in CI
3. ✅ `make reality.green STRICT` passes
4. ✅ Kernel bundle generation is stable and tested
5. ✅ All design specs (26.A-F) are SSOT-visible

Phase 26 is **NOT DONE** if:

- ❌ Any required hint is missing or disabled
- ❌ Boot commands return errors or malformed JSON
- ❌ Kernel surfaces are inconsistent
- ❌ Guards fail in STRICT mode
- ❌ Design specs incomplete or not cross-referenced

---

## 8. Related Documentation

- **Phase 26.F**: `PHASE26_HANDOFF_KERNEL.md` (kernel spec)
- **Phase 26.A**: `EXECUTION_CONTRACT.md` Section 5 (hints/contracts)
- **Phase 26.B**: `PHASE26_PMAGENT_BOOT_SPEC.md` (boot commands)
- **Phase 26.C**: `PHASE26_OA_BOOT_SPEC.md` (OA behavior)
- **Phase 26.D**: `PHASE26_OPS_BOOT_SPEC.md` (OPS behavior)
- **Index**: `PHASE26_INDEX.md`
- **Guards**: `scripts/guards/guard_kernel_surfaces.py`, `guard_reality_green.py`

---

## 9. Open Questions

1. **Hint enforcement timing**: Should hints block work immediately or phase in gradually?
   - **Decision**: Phase 26 installs hints as REQUIRED but enforcement ramps up over Phase 27.

2. **Emergency override protocol**: How to handle critical fixes when kernel is degraded?
   - **Decision**: Deferred to operational runbooks (not Phase 26 scope).

3. **OA/OPS full implementation timing**: When to complete vs when to ground?
   - **Decision**: Phase 26 grounds (specs referenced), Phase 27+ implements fully.

---

## Changelog

- **2025-12-06**: Initial Phase-DONE plan (Phase 26.E)
