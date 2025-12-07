# PHASE25_INDEX.md — Handoff Protocol & Operator Surfaces

## 25.0 — Phase Summary

**Goal:** Turn the new bootstrap surfaces  
- `share/PM_BOOTSTRAP_STATE.json`  
- `share/HANDOFF_KERNEL.json`  

into a **clear, documented, repeatable boot protocol** for:
- New PM chats
- Orchestrator Assistant (OA)
- Cursor / OPS agents

**Out of scope:** New DB schemas, new kernel logic, or major console rewrites. Phase 25 is primarily **documentation + guard wiring planning**, not implementation.

**Prereqs:** Phase 24 complete and green on `main` (reality.green == true, kernel healthy).

---

## 25.A — PM Handoff Protocol Doc

### Problem

We now have a deterministic kernel (`HANDOFF_KERNEL.json`) but  
there is **no single, canonical doc** that tells a new PM chat:
- Which files to load first
- In what order
- What checks to run
- How to react if `reality_green` is false

### Objectives

1. Maintain **`docs/SSOT/PM_HANDOFF_PROTOCOL.md`** that defines:
   - Minimal surfaces to load on a new PM chat:
     - `share/PM_BOOTSTRAP_STATE.json`
     - `share/HANDOFF_KERNEL.json`
   - Step-by-step "New Chat Boot Sequence" for PM:
     1. Read kernel → confirm `current_phase` and `branch`.
     2. Check `health.reality_green` and key checks.
     3. If any critical check is false, read the relevant guard docs before acting.
     4. Load phase docs from `docs/SSOT/` and `share/PHASE*_INDEX.md` as needed.
   - How PM should interact with Cursor and OA using these surfaces.

2. Ensure the doc is **SSOT-grade**:
   - Lives under `docs/SSOT/`
   - Referenced from this index
   - Linked from RULES/AGENTS docs in a later phase.

### Deliverables

- `docs/SSOT/PM_HANDOFF_PROTOCOL.md` (canonical, filled)
- Reference to this doc in `PHASE25_INDEX.md`.

---

## 25.B — SHARE Folder Analysis & Layout Doc

### Problem

Guards already refer to a conceptual share layout and expect documentation, but these docs were only skeletons prior to Phase 25.

### Objectives

1. Maintain **`docs/SSOT/SHARE_FOLDER_ANALYSIS.md`** to describe:
   - The intended `share/` layout (phases 18–24, orchestrator, OA, atlas, exports).  
   - Which parts are:
     - Generated from DMS
     - Generated from scripts
     - Human-maintained
   - How DMS alignment + share sync policy (from Phase 24) work together.

2. Clarify relationships between:
   - `SSOT_SURFACE_V17.json`
   - `PM_BOOTSTRAP_STATE.json`
   - `HANDOFF_KERNEL.json`
   - Orchestrator / OA dirs (`share/orchestrator/`, `share/orchestrator_assistant/`).

### Deliverables

- `docs/SSOT/SHARE_FOLDER_ANALYSIS.md`
- Updated `PHASE25_INDEX.md` section summarizing the doc’s purpose.

---

## 25.C — Agent Usage Patterns (PM / OA / Cursor)

This section defines **how all agents must use the Handoff Kernel**, beginning in Phase 25.  
It establishes behavioral norms that later phases (26+) will codify into hints and envelopes.

### 25.C.1 — Universal Rule

All agents must begin every new session by reading:

1. `share/HANDOFF_KERNEL.json`
2. `share/PM_BOOTSTRAP_STATE.json`

No agent may assume the phase, branch, health status, or share layout without these surfaces.

---

### 25.C.2 — PM Usage Pattern

1. Load kernel → extract `current_phase`, `health.reality_green`.  
2. If `health.reality_green == false` → enter degraded mode and halt work.  
3. Load Bootstrap → confirm agreement with kernel.  
4. Only then load SSOT phase docs as needed.  
5. All instructions to Cursor must reference kernel metadata explicitly.

---

### 25.C.3 — Orchestrator Assistant (OA) Usage Pattern

OA must:

1. Read kernel at session start.  
2. Never infer phase or system health from memory.  
3. Warn PM if kernel is stale or missing.  
4. Use kernel’s `required_surfaces` to decide which files need to be checked before reasoning.  
5. Never bypass guards (only PM can authorize guard bypassing).

---

### 25.C.4 — Cursor / OPS Usage Pattern

Cursor must:

1. Begin every run by loading kernel.  
2. Refuse destructive operations unless:  
   - Kernel says healthy  
   - Backup guard passes  
   - Share Sync & DMS Alignment guards pass  
3. Use kernel’s branch + phase metadata to select correct PR targets.  
4. Output evidence compatible with kernel regeneration.

---

### 25.C.5 — Degraded Mode Behavior

If:

- DMS Alignment fails  
- Share Sync Policy fails  
- Bootstrap Consistency fails  
- Backup missing  
- Kernel mismatch

Then:

- PM must halt  
- OA must halt  
- Cursor must halt  
- Only remediation steps explicitly allowed by PM may run

No phase work may continue until kernel → bootstrap → SSOT are fully aligned.

---

### 25.C.6 — Future Work (Phase 26+)

Phase 26 will:

- Add hint registry entries (“always read kernel first”)  
- Add envelope logic for pmagent flows  
- Add OA hint flows  
- Add Cursor “handoff-aware” initialization routines  

Phase 25 documents the policy; Phase 26 will enforce it programmatically.

---

## 25.D — Phase-DONE Additions (Planning Only)

Phase 25 does not implement new guards. It documents what future “handoff-ready” phases must ensure.

Future phases should extend the Phase-DONE checklist with a **Handoff section**:

- “Kernel exists and passes STRICT guard.”
- “PM_HANDOFF_PROTOCOL.md and SHARE_FOLDER_ANALYSIS.md are current.”
- “DMS/share alignment and backup guards are green.”

Actual guard updates happen in a later phase (Phase 26+).
