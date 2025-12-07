# PHASE26_INDEX.md — Kernel-First Enforcement & Agent Boot Automation

## 26.0 — Phase Summary

**Goal:** Enforce kernel-first boot behavior and automate agent initialization so that:
- PM, OA, and Cursor always start from:
  - `share/HANDOFF_KERNEL.json`
  - `share/PM_BOOTSTRAP_STATE.json`
- No agent can "forget" to check phase, branch, or system health.
- Degraded modes (failed guards) block work until explicitly remediated.

**Scope:** Enforcement & automation only.
- In-scope:
  - Hint registry updates for kernel-first behavior.
  - Envelope and pmagent flow wiring for handoff-aware boot.
  - OA and OPS boot patterns.
- Out of scope:
  - New kernel formats.
  - Major console UI redesign (future phases).

**Prereqs:** 
- Phase 24: DMS alignment, backup, share sync, kernel, and guards are in place.
- Phase 25: Handoff protocol and share analysis SSOT docs are complete and on main.

---

## 26.F — Handoff Kernel Spec (COMPLETE)

See **[`docs/SSOT/PHASE26_HANDOFF_KERNEL.md`](docs/SSOT/PHASE26_HANDOFF_KERNEL.md)** for the structural definition of the Handoff Kernel.

- **Kernel Bundle**:
  - `share/handoff/PM_KERNEL.json` (Machine Seed)
  - `share/handoff/PM_SUMMARY.md` (Human/LLM Narrative)
- **Generation**:
  - `pmagent handoff kernel-bundle`
- **Validation**:
  - `make kernel.check` (runs `scripts/guards/guard_kernel_surfaces.py`)
  - Integrated into Phase-DONE checks for Phase 26+.

---

## 26.A — Hint Registry: Kernel-First Rules (IN PROGRESS)

### Status: Core Kernel Implemented
Core kernel generation and validation logic is ready. Hint registry updates pending.

### Objectives
... (rest of section)

We have a documented protocol (Phase 25) but nothing forces agents to follow it.
Hints exist, but none encode "always read kernel first".

### Objectives

1. Introduce REQUIRED hints that capture:
   - PM boot behavior:
     - Read kernel → read bootstrap → verify health.
   - OA boot behavior:
     - Read kernel and warn if degraded.
   - OPS/pmagent behavior:
     - Run kernel-aware preflight before destructive operations.

2. Ensure hints reference:
   - `PM_HANDOFF_PROTOCOL.md`
   - `SHARE_FOLDER_ANALYSIS.md`
   - `HANDOFF_KERNEL.json`

3. Keep implementation small and focused:
   - Reuse existing hint registry patterns.
   - No new DB tables.

### Deliverables

- New hint entries in the registry (names TBD in implementation).
- Updated documentation referencing these hints.

---

## 26.B — Envelopes & pmagent Boot Flows

### Problem

pmagent flows currently do not guarantee that:
- Kernel is read before operations.
- Health is checked before acting.
- Evidence emitted is kernel-consistent.

### Objectives

1. Define kernel-aware pmagent flows:
   - `pmagent status handoff`
   - `pmagent boot pm`
   - (Possibly) `pmagent boot oa`

2. Update envelope generators so that:
   - Kernel + bootstrap surfaces are part of the standard context.
   - Health flags inform behavior (e.g., degraded vs green).

3. Keep envelope wiring minimal, focused on:
   - Reading kernel and bootstrap.
   - Checking `reality_green` and key health checks.

### Deliverables

- **Design Spec**: [`PHASE26_PMAGENT_BOOT_SPEC.md`](docs/SSOT/PHASE26_PMAGENT_BOOT_SPEC.md)
  - Command behaviors for `status handoff`, `boot pm`, `boot oa`
  - Kernel boot envelope schema
  - Integration with DB preflight and kernel preflight protocols
- Command stubs in `pmagent/handoff/commands.py` (implementation in later PR)

---

## 26.C — OA Boot Behavior

### Problem

The Orchestrator Assistant currently relies on conventions and past chats rather than a formal boot sequence.

### Objectives

1. Define OA’s required boot steps:
   - Read kernel.
   - Read bootstrap.
   - If degraded:
     - Surface explanation to PM.
     - Refuse to proceed with normal work.

2. Specify how OA should:
   - Use `HANDOFF_KERNEL.json` to decide which docs to read.
   - Escalate when guards fail.

### Deliverables

- **Design Spec**: [`PHASE26_OA_BOOT_SPEC.md`](docs/SSOT/PHASE26_OA_BOOT_SPEC.md)
  - OA role definition (interpreter, not executor)
  - Boot steps (kernel-first, never infer from memory)
  - NORMAL vs DEGRADED mode behaviors
  - Allowed/forbidden pattern examples
  - Integration with `oa.boot.kernel_first` hint and kernel boot envelope

---

## 26.D — Cursor / OPS Boot Behavior

### Problem

Cursor runs commands when asked, but is not yet strictly governed by kernel health.

### Objectives

1. Define baseline OPS preflight behavior:
   - Read kernel.
   - Verify:
     - DMS Alignment
     - Share Sync Policy
     - Bootstrap Consistency
     - Backup System

2. Specify when Cursor must:
   - Refuse destructive operations.
   - Ask PM for explicit override.

3. Integrate with:
   - backup guard
   - share sync guard
   - DMS alignment guard
   - handoff kernel guard

### Deliverables

- **Design Spec**: [`PHASE26_OPS_BOOT_SPEC.md`](docs/SSOT/PHASE26_OPS_BOOT_SPEC.md)
  - Cursor/OPS role definition (executor, not inventor)
  - Boot & preflight steps (kernel-first, guard verification)
  - NORMAL vs DEGRADED mode behaviors
  - Allowed/forbidden pattern examples
  - Integration with `ops.preflight.kernel_health` hint, guards, and DB preflight

---

## 26.E — Phase-DONE Handoff Enforcement (Planning)

### Problem

Phase-DONE currently checks many invariants but does not yet enforce kernel-aware behavior.

### Objectives

1. Draft additional Phase-DONE items:
   - "Kernel-first hints present and enabled."
   - "Kernel-aware envelopes wired for pmagent flows."
   - "OA and OPS boot behaviors documented and partially enforced."

2. Decide which items:
   - Must be enforced in Phase 26.
   - Can be deferred to later phases.

### Deliverables

- **Design Spec**: [`PHASE26_PHASE_DONE_PLAN.md`](docs/SSOT/PHASE26_PHASE_DONE_PLAN.md)
  - Required checklist (6 items): kernel bundle, hints, pmagent commands, OA/OPS grounding, reality.green
  - Deferred items: pre-commit hooks, wrapper commands, emergency overrides
  - Enforcement mechanisms: CI integration, guard scripts, make targets
  - Clear boundary between Phase 26 closure and Phase 27+ work
