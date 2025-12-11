# PM State Package — Specification

## Purpose

The PM State Package is the **only** format the Orchestrator should paste into a
new PM chat. It is a **neutral description of state**, not a meta-handoff or a
set of instructions.

The PM must treat it as **data**, not as a request to generate another handoff.

## Required Sections

1. Role

   - Example:

     - `Role: Project Manager (PM) of Gemantria`

   - Must clearly say the assistant *is* the PM.

2. Truth Sources

   - Explicit list of kernel + SSOT surfaces the PM must load:

     - `HANDOFF_KERNEL.json`

     - `PM_KERNEL.json`

     - `PM_BOOTSTRAP_STATE.json`

     - `REALITY_GREEN_SUMMARY.json`

   - May also list SSOT docs already mirrored in pm_boot.

3. Governance Contracts

   - List of contracts the PM must obey:

     - `PM_CONTRACT.md`

     - `PM_BEHAVIOR_CONTRACT.md`

     - `PM_AND_OPS_BEHAVIOR_CONTRACT.md`

     - `PM_BOOT_CONTRACT.md`

     - `PM_CONTRACT_STRICT_SSOT_DMS.md`

     - `EXECUTION_CONTRACT.md`

     - `CURSOR_WORKFLOW_CONTRACT.md`

     - OPS rules 050 / 051 / 052

4. Active Phase & Branch

   - Current phase and branch:

     - Phase (e.g. `Phase 27`)

     - Subphase/batches if relevant (e.g. `27.H`, `27.I Batch 2`)

     - Current working branch (e.g. `feat/phase27i-schemas-namespace-cleanup`)

5. Planning Surfaces

   - Key planning docs the PM must consult:

     - `PHASE27_INDEX.md` (or relevant phase index)

     - `PHASE27I_DIRECTORY_UNIFICATION_PLAN.md` (if active)

     - `DIRECTORY_DUPLICATION_MAP.md`

     - Any other phase-specific plans

6. System Health Snapshot

   - A short summary derived from `REALITY_GREEN_SUMMARY.json`:

     - Structural checks (DMS, root, AGENTS, pm_boot, share) — green/red

     - Operational checks (Backup System) — note that backup is time-windowed

7. Next Required Work (High Level)

   - One or two sentences stating what Phase/Batch needs to happen next.

   - No options, no questions.

   - Example:

     - "Next required work: create a PR for Phase 27.I Batch 2 (Schemas) from

        `feat/phase27i-schemas-namespace-cleanup`."

## Behavioral Rules

- The PM **must not** respond to a State Package by generating another

  handoff-like wall of text.

- The PM must:

  1. Load kernel, pm_boot, and contracts.

  2. Reconstruct the mental model from the State Package.

  3. Immediately move to **confirmation + OPS**, not more boot text.

- The Orchestrator **must not** paste older "handoff" formats into new chats.

  Only PM State Packages should be used going forward.
