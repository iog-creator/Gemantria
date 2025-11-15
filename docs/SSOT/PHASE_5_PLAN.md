# Phase-5 — StoryMaker & BibleScholar LM Integration

Status: PLANNING (initial scaffolding)  
Scope: Safe, hermetic LM status consumption + app-level components  
Upstream Dependencies: Phase-4 complete on `main` (indicator export + UX status page + governance)

## Objective

Provide downstream apps (StoryMaker, BibleScholar) with a safe, hermetic,
consistent LM-status integration using the canonical signal:
`share/atlas/control_plane/lm_indicator.json`.

Apps MUST NOT implement new heuristics; logic is centralized.

## Deliverables

1. **LM Indicator Widget Contract (Locked)**  

   Already defined in Phase-4D output:

   - Fields: status, reason, color, icon, label, tooltip_lines, metrics{...}

   - Hermetic: file-only, no DB, no LM calls

   - Fail-closed default: treat missing/invalid indicator as offline-safe mode

2. **Shared Adapter Module** (Gemantria-level)

   - Function: `load_lm_indicator_widget_props()`

   - Input: lm_indicator.json

   - Output: props dict strictly matching widget contract

   - Guarantees:

     - Hermetic

     - db_off-safe and LM-off-safe

     - Missing-file safe

   - Add full tests (healthy, degraded, offline, missing-file, invalid-JSON)

3. **StoryMaker Integration Plan**

   - A tiny tile component using the widget props (not in this PR)

   - Tooltip rendering guidelines

   - Color/icon mapping table (app-specific, not part of Gemantria SSOT)

   - File-watcher optional: re-read props on change

4. **BibleScholar Integration Plan**

   - Header badge using same props

   - Tooltip with metrics

   - Offline-safe fallback screen note

   - Color/icon mapping table

5. **Guidance for App Repos**

   - DO NOT reclassify LM health

   - DO NOT read metrics directly

   - MUST consume the adapter or mirror its logic exactly

6. **Compliance & Governance Requirements**

   - No DB/LM calls in downstream adapters

   - No "smart" interpretation; Gemantria owns logic

   - New section in MASTER_PLAN with Phase-5 description

   - Add reference in AGENTS.md

   - Add to CHANGELOG under "Unreleased"

## PR Staging for Phase-5

PR #1 (this PR):

- Add PHASE_5_PLAN.md

- Add LM_WIDGETS.md (contract summary)

- Add code stub + tests placeholder for adapter

- Update MASTER_PLAN, AGENTS, CHANGELOG

PR #2:

- Implement adapter + full tests

PR #3:

- StoryMaker integration (external repo)

PR #4:

- BibleScholar integration (external repo)

