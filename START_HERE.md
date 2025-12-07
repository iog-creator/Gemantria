# START HERE — Gemantria Orchestrator / Agent Boot Guide

This repository is **kernel-governed**. Before ANY work:

## Mandatory Boot Sequence

### 1. Read the Execution Contract

**File**: [`docs/SSOT/EXECUTION_CONTRACT.md`](docs/SSOT/EXECUTION_CONTRACT.md)

This document defines:
- Cursor's OPS-only behavior
- Kernel-aware preflight requirements
- Share/ governance rules
- DMS query protocol

### 2. Run Kernel Boot Preflight

**Command**: `make ops.kernel.check`

This executes [`scripts/guards/guard_kernel_boot.py`](scripts/guards/guard_kernel_boot.py) which:
- Calls `pmagent handoff status-handoff --json`
- Validates `ok` status
- Checks kernel health (`current_phase`, `branch`)

**If this fails**:
- **STOP** normal work
- Report the failure and surfaced kernel info to the PM
- **Only run PM-approved remediation OPS blocks**

### 3. Inspect the Kernel

**Command**: `cat share/handoff/PM_KERNEL.json | jq .`

Confirm:
- `current_phase` - What phase is active
- `branch` - Which Git branch should be used
- `mode` - `NORMAL` or `DEGRADED`

### 4. Check System Mode

**Only proceed if `mode == "NORMAL"`**

If `mode == "DEGRADED"`:
- ❌ No feature/phase work allowed
- ❌ No destructive operations
- ✅ Only PM-approved remediation work

Until remediation is complete and mode returns to `NORMAL`.

### 5. Check GitHub Reality (Phase 26.5+)

**Command**: `make github.state.check`

This shows:
- Current branch and tracking info
- Kernel phase vs branch name alignment
- Git status

**Why this matters**:
- Prevents mixing Phase N work onto Phase M branches
- Ensures GitHub (branch, PR, CI) is part of reality checks
- See [`docs/SSOT/GITHUB_WORKFLOW_CONTRACT.md`](docs/SSOT/GITHUB_WORKFLOW_CONTRACT.md) for details

---

## For AI Agents (Cursor, Gemini, etc.)

**You are NOT operating on a normal Python repository.**

This is a **governed system** with:
- Mandatory kernel-first boot sequence
- Strict execution contracts
- DMS-backed hint system
- Phase-driven development

**Before executing ANY OPS block**:
1. Run `make ops.kernel.check` (Section 0 of Rule 050)
2. Read `share/handoff/PM_KERNEL.json`
3. Verify mode is `NORMAL`
4. Follow all instructions in `EXECUTION_CONTRACT.md`

**Failure to follow these steps will break the system.**

---

## Related Documentation

**Core Governance**:
- [`.cursor/rules/050-ops-contract.mdc`](.cursor/rules/050-ops-contract.mdc) - OPS Contract v6.2.3 (Section 0: Mandatory Kernel Boot)
- [`docs/SSOT/EXECUTION_CONTRACT.md`](docs/SSOT/EXECUTION_CONTRACT.md) - Full execution contract
- [`docs/SSOT/ORCHESTRATOR_REALITY.md`](docs/SSOT/ORCHESTRATOR_REALITY.md) - Agent roles and responsibilities

**Phase 26 Specifications**:
- [`docs/SSOT/PHASE26_OPS_BOOT_SPEC.md`](docs/SSOT/PHASE26_OPS_BOOT_SPEC.md) - Detailed boot behavior
- [`docs/SSOT/PHASE26_PMAGENT_BOOT_SPEC.md`](docs/SSOT/PHASE26_PMAGENT_BOOT_SPEC.md) - pmagent boot commands
- [`docs/SSOT/PHASE26_HANDOFF_KERNEL.md`](docs/SSOT/PHASE26_HANDOFF_KERNEL.md) - Kernel format

**Implementation**:
- [`scripts/guards/guard_kernel_boot.py`](scripts/guards/guard_kernel_boot.py) - Kernel boot guard
- [`Makefile`](Makefile) - See `ops.kernel.check` target (lines 118-122)
- [`oa/tools/boot.py`](oa/tools/boot.py) - OA tool wrappers for kernel access

---

## Quick Reference

| Question | Answer |
|---|---|
| Is this a normal Python repo? | ❌ **NO** - It's kernel-governed |
| Can I skip kernel checks? | ❌ **NO** - Mandatory per Rule 050 Section 0 |
| What if `ops.kernel.check` fails? | Enter NO-OP mode, report to PM |
| What if mode is DEGRADED? | Only remediation work allowed |
| Where's the source of truth? | `share/handoff/PM_KERNEL.json` + `PM_BOOTSTRAP_STATE.json` |

---

**Last Updated**: 2025-12-06 (Phase 26 Enforcement)
