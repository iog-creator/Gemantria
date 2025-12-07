# PHASE26_OPS_BOOT_SPEC.md — Cursor/OPS Boot & Preflight Behavior

**Phase**: 26.D  
**Status**: Design Complete — Implementation Pending  
**Version**: 1.0  
**Last Updated**: 2025-12-06

---

## 1. Overview

This document defines the **kernel-aware boot and preflight behavior** for Cursor/OPS (the execution agent). Cursor must verify kernel health and guard status before any destructive operation, enforcing the `ops.preflight.kernel_health` hint from Phase 26.A.

### Goals

1. **Prevent destructive ops in degraded state**: Block work when guards fail
2. **Enforce kernel-first preflight**: Always check kernel before mutations
3. **Integrate with existing guards**: DMS alignment, share sync, backup, bootstrap consistency

### Non-Goals

- Changing existing guard implementations (reuse existing)
- Adding new guard types (use current set)
- Implementing wrapper commands (design only)

---

## 2. Role of Cursor/OPS in the System

**What Cursor/OPS Is**:
- **Executor**: Runs commands, edits files, executes make targets
- **Obedient**: Follows PM directives and kernel constraints
- **Guarded**: Verifies health before destructive operations

**What Cursor/OPS Is NOT**:
- **Not Inventor**: Does not decide what to do without PM direction
- **Not Guesser**: Does not infer system state from file paths or assumptions
- **Not Bypass Artist**: Does not skip guards or health checks

---

## 3. Boot & Preflight Steps

### 3.1. Boot Sequence (Start of OPS Session)

When Cursor starts working on a task:

1. **Read Kernel Boot Envelope**:
   - Via `pmagent status handoff --json`
   - Or direct read of `PM_KERNEL.json` + `PM_BOOTSTRAP_STATE.json`

2. **Extract Critical State**:
   - `kernel.current_phase`
   - `kernel.branch`
   - `health.reality_green`
   - `mode` (NORMAL or DEGRADED)

3. **Set Working Context**:
   - Use kernel state for all decisions
   - Never cache across sessions
   - Re-check before destructive ops

### 3.2. Preflight Check (Before Destructive Operations)

**Destructive operations** include:
- Modifying `share/` contents
- Running database migrations
- Bulk data changes
- Schema modifications
- Deleting or regenerating surfaces

**Before ANY destructive operation, Cursor must**:

1. **Run Kernel Preflight**:
   ```bash
   # Load kernel
   cat share/handoff/PM_KERNEL.json
   
   # Confirm branch match
   git rev-parse --abbrev-ref HEAD
   
   # Check guards
   make reality.green
   ```

2. **Verify Guards Pass**:
   - DMS Alignment (`guard_dms_share_alignment.py`)
   - Share Sync Policy (`guard_share_sync_policy.py`)
   - Bootstrap Consistency (`guard_bootstrap_consistency.py`)
   - Backup System (`guard_backup_rotate.py` check)

3. **Check DB Preflight** (if querying DMS):
   ```bash
   python scripts/ops/preflight_db_check.py --mode strict
   ```

4. **Verify Mode**:
   - If `mode == DEGRADED` → STOP
   - Only proceed if `mode == NORMAL` and all guards pass

### 3.3. Enforcement Via Hint

From Phase 26.A, the REQUIRED hint `ops.preflight.kernel_health` encodes:
- Before destructive ops, read kernel and verify guards
- Restrict to remediation-only if degraded
- This spec is the behavioral reference for that hint

---

## 4. Behavior by Mode

### 4.1. NORMAL Mode

**When**: `mode == "NORMAL"` and `health.reality_green == true`

**Cursor May**:
- Execute PM-authorized commands
- Run make targets (after preflight passes)
- Edit files per PM instructions
- Run tests and verification steps

**Cursor Must**:
- Run preflight before destructive ops
- Verify kernel branch matches current git branch
- Check all guards pass before mutations
- Reference kernel constraints

**Cursor Must NOT**:
- Skip preflight checks
- Ignore failing guards
- Run destructive ops "just to see what happens"
- Bypass health gates

### 4.2. DEGRADED Mode

**When**: `mode == "DEGRADED"` or `health.reality_green == false`

**Cursor May ONLY**:
- Run PM-authorized remediation commands
- Execute guard-fixing operations
- Run diagnostic commands (read-only)
- Help PM investigate failures

**Remediation Scope** (allowed):
- Fixing DMS alignment
- Restoring backups
- Correcting bootstrap consistency
- Share sync repairs
- Starting PostgreSQL
- Running `make share.sync`

**Normal Work** (blocked):
- Phase feature development
- New code implementations
- Schema migrations
- SSOT modifications
- Any work not explicitly scoped as remediation

**Cursor Must**:
- Explain degraded status to PM
- List failing guards and remediation docs
- Refuse normal work until PM defines remediation scope
- Only proceed with explicitly approved remediation

**Cursor Must NOT**:
- Continue phase work while degraded
- Suggest "ignoring" or "skipping" failing guards
- Run destructive operations
- Make changes outside remediation scope

---

## 5. Allowed vs Forbidden Patterns

### 5.1. NORMAL Mode Examples

✅ **Allowed**:
```bash
# 1. Check kernel health
pmagent status handoff --json

# 2. Verify guards
make reality.green

# 3. If green, proceed
make share.sync
git add share/
git commit -m "Phase 26.D: Update share surfaces"
```

❌ **Forbidden**:
```bash
# Skip health check entirely
make share.sync  # WRONG: no preflight

# Or ignore failing guards
make reality.green  # Shows failures
make share.sync     # WRONG: proceeding anyway
```

### 5.2. DEGRADED Mode Examples

✅ **Allowed (Remediation)**:
```bash
# PM says: "Fix DMS alignment"

# 1. Check status
pmagent status handoff

# 2. Run specific remediation
make share.sync

# 3. Verify fix
make reality.green

# 4. Report to PM
pmagent status handoff --json
```

❌ **Forbidden (Normal Work)**:
```bash
# System is degraded (DB offline)

# WRONG: Continue phase work anyway
python scripts/phase26/implement_feature.py

# WRONG: "Let's just try it"
make migrations.apply
```

### 5.3. DB Preflight Integration

✅ **Correct Pattern**:
```bash
# Before querying DMS
python scripts/ops/preflight_db_check.py --mode strict

# If passes, proceed
python scripts/governance/check_dms_work_needed.py
```

❌ **Forbidden**:
```bash
# Skip DB preflight
python scripts/governance/check_dms_work_needed.py  # WRONG
```

---

## 6. Guard Integration

### 6.1. Required Guards

**DMS Alignment** (`guard_dms_share_alignment.py`):
- Verifies share/ matches control.doc_registry
- Blocks if unknown files in managed namespaces

**Share Sync Policy** (`guard_share_sync_policy.py`):
- Ensures share/ surfaces are DMS-derived
- Checks for policy violations

**Bootstrap Consistency** (`guard_bootstrap_consistency.py`):
- Verifies PM_BOOTSTRAP_STATE.json matches reality
- Checks missing files, not_in_registry counts

**Backup System** (check via `guard_backup_rotate.py` or manual):
- Ensures recent backup exists
- Verifies rotation policy

### 6.2. Guard Execution Pattern

```bash
# Run all guards via reality.green
make reality.green

# Parse output
# If any guard fails → mode = DEGRADED
# If all pass → mode = NORMAL (pending other health checks)
```

### 6.3. Guard Failure Responses

**DMS Alignment Failure**:
- Remediation: `make share.sync`
- Doc: `DMS_QUERY_PROTOCOL.md`

**DB Health Failure**:
- Remediation: Start PostgreSQL, run DB preflight
- Doc: `docs/hints/HINT-DB-002-postgres-not-running.md`

**Backup Failure**:
- Remediation: Run backup, verify rotation
- Doc: `PHASE24_INDEX.md` (backup section)

**Bootstrap Consistency Failure**:
- Remediation: Regenerate bootstrap, fix registry
- Doc: `PM_BOOTSTRAP_STATE.json` generation script

---

## 7. Integration with Existing Protocols

### 7.1. Kernel Preflight (EXECUTION_CONTRACT Section 5)

**From `EXECUTION_CONTRACT.md`**:
> Before executing any operation that can modify share/, change DB schema, or affect DMS alignment, Cursor/OPS must:
> 1. Read share/handoff/PM_KERNEL.json
> 2. Confirm branch matches kernel.branch
> 3. Verify DMS Alignment, Share Sync, Bootstrap Consistency, Backup guards

**This spec implements that contract.**

### 7.2. DB Preflight (DMS_QUERY_PROTOCOL)

**From `DMS_QUERY_PROTOCOL.md`**:
> Before ANY DMS query, run: `python scripts/ops/preflight_db_check.py --mode strict`

**OPS boot spec enforces**:
- DB preflight before DMS queries
- No bypass allowed
- Clear error messages when DB offline

### 7.3. PM Handoff Protocol (Phase 25)

**From `PM_HANDOFF_PROTOCOL.md`**:
- Kernel is authoritative
- Guards are mandatory
- Degraded mode blocks work

**Cursor's role**:
- Execute PM directives within kernel constraints
- Respect guard failures
- Report status accurately

---

## 8. Future Implementation Notes

### 8.1. Wrapper Commands

Create helper commands that enforce preflight:

```bash
# ops-guarded-make: Wrapper that checks kernel first
ops-guarded-make reality.green
ops-guarded-make share.sync

# Each wrapper:
# 1. Runs pmagent status handoff
# 2. Checks mode
# 3. If DEGRADED, refuses
# 4. If NORMAL, runs make target
```

### 8.2. Pre-Commit Hook

```bash
# .git/hooks/pre-commit
pmagent status handoff --json | jq -e '.mode == "NORMAL"'
if [ $? -ne 0 ]; then
  echo "❌ System is DEGRADED. Commit blocked."
  exit 1
fi
```

### 8.3. Make Integration

```makefile
# Prefix critical targets with kernel check
share.sync: kernel-check
	@python scripts/sync_share.py

kernel-check:
	@pmagent status handoff --json | jq -e '.mode == "NORMAL"' || \
		(echo "❌ Kernel check failed. Aborting."; exit 1)
```

---

## 9. Verification Plan

Since this is **design-only**, verification is documentation review:

1. **SSOT Cross-Links**:
   - [ ] `PHASE26_INDEX.md` references this spec under 26.D
   - [ ] Consistent with `EXECUTION_CONTRACT.md` Section 5
   - [ ] Aligns with `DMS_QUERY_PROTOCOL.md`
   - [ ] Integrates with `PHASE26_PMAGENT_BOOT_SPEC.md`

2. **Guard Coverage**:
   - [ ] All 4 required guards documented
   - [ ] Remediation paths clear
   - [ ] Integration with `make reality.green` specified

3. **Behavioral Clarity**:
   - [ ] NORMAL vs DEGRADED clearly distinguished
   - [ ] Allowed/forbidden patterns concrete
   - [ ] Preflight steps unambiguous

---

## 10. Related Documentation

- **Phase 26.F**: `PHASE26_HANDOFF_KERNEL.md` (kernel format)
- **Phase 26.B**: `PHASE26_PMAGENT_BOOT_SPEC.md` (boot envelope)
- **Phase 26.A**: `EXECUTION_CONTRACT.md` Section 5 (kernel preflight)
- **Phase 25**: `PM_HANDOFF_PROTOCOL.md`
- **DB Preflight**: `DMS_QUERY_PROTOCOL.md`, `PREFLIGHT_DB_CHECK_ROLLOUT.md`
- **Guards**: `guard_dms_share_alignment.py`, `guard_share_sync_policy.py`, etc.
- **Hints**: `ops.preflight.kernel_health` (from hint registry)
- **Index**: `PHASE26_INDEX.md` Section 26.D

---

## 11. Open Questions / Future Work

1. **Wrapper adoption**: Should all make targets use wrappers or inline checks?
2. **Pre-commit enforcement**: Enable by default or opt-in?
3. **Emergency overrides**: Define escape hatch for critical production fixes?

**Decisions**: For Phase 26.D design, focus on standard workflow. Emergency procedures deferred to operational runbooks.

---

## Changelog

- **2025-12-06**: Initial design (Phase 26.D)
