# Phase 26 — Handoff Kernel Spec
Status: **IN PROGRESS**

## 1. Purpose

This document defines the **minimal handoff bundle** for a fresh PM instance in Gemantria.
This bundle is the machine-readable "seed" that allows a new agent (PM, OA, or OPS) to reconstruct the system's state, health, and constraints without relying on conversation history or loose file exploration.

The bundle consists of two generated files in `share/handoff/`:
1. `PM_KERNEL.json` — The rigorous machine state.
2. `PM_SUMMARY.md` — The human/LLM narrative summary.

---

## 2. Handoff Kernel Contents

### 2.1. `share/handoff/PM_KERNEL.json`

This JSON file is the **primary boot surface**. It MUST be generated programmatically, never hand-edited.

**Required Schema:**

```json
{
  "current_phase": "26",
  "branch": "feat/phase26-kernel-enforcement",
  "last_completed_phase": "25",
  "next_actions": [
    "Run kernel check",
    "Verify guard status"
  ],
  "ground_truth_files": [
    "share/PM_BOOTSTRAP_STATE.json",
    "share/SSOT_SURFACE_V17.json",
    "share/PHASE26_INDEX.md"
  ],
  "constraints": {
    "backup_required_before_destructive_ops": true,
    "enforced_checks": [
      "reality.green",
      "stress.smoke",
      "phase.done.check"
    ]
  },
  "generated_at_utc": "2025-12-06T00:00:00Z",
  "generator_version": "pmagent.handoff.kernel.v1"
}
```

**Field Semantics:**
- `current_phase`: The active phase identifier.
- `branch`: The Git branch where this kernel was generated.
- `last_completed_phase`: The highest phase number fully marked CONFIRMED/COMPLETE.
- `next_actions`: Contextual "what to do next" derived from the current phase index.
- `ground_truth_files`: A list of absolute or repository-relative paths that constitute the SSOT for this phase.
- `constraints`: Operational rules that the agent must respect (e.g., fail-closed guards).

### 2.2. `share/handoff/PM_SUMMARY.md`

This Markdown file provides a **natural language synthesis** of the kernel.

**Required Sections:**
- **Where we really are**: High-level status (Phase, Branch, Health).
- **What’s green / proven**: Summary of passing guards and last verification results.
- **Known gotchas / sharp edges**: Warnings from the current phase index or bootstrap notes.
- **Next actions for Cursor**: Clear instructions on pending work.
- **How to regenerate this kernel**: Command to run (`pmagent handoff-kernel`).

---

## 3. Source of Truth

The kernel is a **derivative surface**. It does not define truth; it aggregates it from:
1. **DMS (Postgres)**: Registry of documents, hints, and governance rules.
2. **`share/PM_BOOTSTRAP_STATE.json`**: Structural bootstrapping data.
3. **Phase Index Docs**: `share/PHASE*_INDEX.md` (or `docs/SSOT/PHASE*_INDEX.md`).
4. **Agent State**: `share/orchestrator/STATE.json`, `share/orchestrator_assistant/STATE.json`.

**Generation Rule:**
`pmagent handoff-kernel` is the ONLY authorized writer for these files.

---

## 4. Usage Protocol

### 4.1. Human PM Handoff
When starting a new chat session:
1. The user uploads **only** `share/handoff/PM_KERNEL.json` and `share/handoff/PM_SUMMARY.md`.
2. The agent (PM) reads these files to initialize its context.

### 4.2. Machine / pmagent Handoff
1. The `pmagent` tool uses the kernel as a "rehydration snapshot" to verify environment consistency.
2. If the environment (Git branch, file existence) does not match `PM_KERNEL.json`, the agent must halt or warn.

---

## 5. Verification

The integrity of the kernel is enforced by `scripts/guards/guard_kernel_surfaces.py`.
This guard ensures that:
- The JSON is valid and matches the schema.
- The Git branch in the kernel matches the actual repo branch.
- All `ground_truth_files` exist.
- Required sections in `PM_SUMMARY.md` are present.
