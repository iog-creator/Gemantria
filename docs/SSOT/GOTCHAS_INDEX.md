# GOTCHAS_INDEX — Where Problems Hide and How to Surface Them

**Status**: ACTIVE  
**Related**: Rule 050, 058, 069, 070, EXECUTION_CONTRACT_CURSOR  
**Date**: 2025-12-03

This document is the **Single Source of Truth (SSOT)** for:
- Where "gotchas" live in this repo,
- How to find them,
- How they must be surfaced before doing feature work.

Gotchas are grouped into **three layers**:

1. Codebase gotchas (TODO/FIXME/etc.)
2. SSOT/documentation gotchas (diagnostics, structural gaps)
3. Toolchain/behavioral gotchas (governance breaks, Cursor drift)

Any new class of gotcha MUST be added here.

---

## 1. Layer 1 — Codebase Gotchas (Static Markers)

These are explicit markers in code such as:

- `TODO`
- `FIXME`
- `XXX`
- Comments describing "temporary hack", "workaround", "assumption", etc.

### 1.1 Where they usually live

Typical hot spots (non-exhaustive, update as needed):

- `scripts/export_graph.py`
- `scripts/extract_all.py`
- `scripts/compass/scorer.py`
- `scripts/ops/*.py` (ingestion, analytics, DMS pipeline)
- `scripts/guards/guard_*.py`
- DSN/config modules (`scripts/config/env.py`, `src/*dsn*`)

### 1.2 How to scan for them

Canonical command:

```bash
rg "TODO|FIXME|XXX" scripts src pmagent -n || true
```

This command should be run by:

- Humans, when starting a new phase,
- Cursor, via `scripts/guards/guard_gotchas_index.py` in **pre-work checks**.

---

## 2. Layer 2 — SSOT / Documentation Gotchas

These are **documented conceptual gaps** or "known-bad" states.

Key SSOT docs that currently define gotchas:

- `docs/SSOT/PHASE8_PHASE10_DIAGNOSTIC.md`
  - Explains why Phase 8/10 analytics produced empty or partial outputs.
- `docs/SSOT/PHASE15_COMPASS_STRUCTURAL_GAP.md`
  - Documents missing COMPASS fields (`correlation_weights`, `temporal_patterns`) and structural failure states.
- `docs/SSOT/PHASE10_WIRING_SELF_ASSESSMENT.md`
  - Self-assessment of Phase 10 wiring, ID-space mismatches, and workflow violations.
- `docs/SSOT/PHASE10_CORRELATION_WIRING_COMPLETE.md`
  - What was implemented for Phase 10; includes known data mismatches and next steps.
- `docs/SSOT/HOUSEKEEPING_PERFORMANCE_OPTIMIZATION.md`
  - Notes that housekeeping can run in hermetic/DB-down environments and why that is a potential **false sense of safety**.

As new diagnostics or "gap analysis" docs are created, they MUST be added to this list.

### 2.1 How to interpret these docs

- If you are working on **Phase 8 or 10 analytics**, you MUST read:
  - `PHASE8_PHASE10_DIAGNOSTIC.md`
  - `PHASE10_WIRING_SELF_ASSESSMENT.md`
  - `PHASE10_CORRELATION_WIRING_COMPLETE.md`

- If you are working on **COMPASS or Phase 15**, you MUST read:
  - `PHASE15_COMPASS_STRUCTURAL_GAP.md`
  - Any relevant Wave-3/Wave-n status docs.

- If you are modifying **housekeeping** or AGENTS/docs sync logic, you MUST read:
  - `HOUSEKEEPING_PERFORMANCE_OPTIMIZATION.md`

Failure to consult these before changing code or behavior is a **Rule 070 gotchas violation**.

---

## 3. Layer 3 — Toolchain / Behavioral Gotchas

These are patterns where agents (especially Cursor) tend to drift.

### 3.1 Acting without an OPS block

- Cursor must **never** treat a plain user message as permission to:
  - Modify code,
  - Edit SSOT docs,
  - Optimize housekeeping,
  - Change performance characteristics.

- Any destructive or repo-changing action requires:
  - A valid OPS block from the PM (governance header + Goal/Commands/Evidence/Next gate).

### 3.2 Ignoring DMS / SSOT (Rule 069)

- DMS/Postgres is SSOT for governance and project state.
- Planning and status checks must read from:
  - `doc_registry`, `hint_registry`, COMPASS exports, and SSOT docs.
- Assuming "how things used to be" instead of consulting DMS is a behavioral gotcha.

### 3.3 UI verification drift (Rule 051, 067)

- Any UI/visual work (web UI, Atlas overlays, badges, dashboards) must use:
  - `make browser.verify`
  - `make atlas.webproof`
- Skipping these leads to silent divergence between UI and underlying atlas/exports.

### 3.4 Gematria policy drift

- SSOT law:
  - **Ketiv is primary** for gematria.
  - **Qere** is a **variant** stored as metadata, not primary.
- Any implementation or doc that treats Qere as primary is a serious gotcha.
- Gematria correctness priority:
  1. Code gematria module (deterministic)
  2. bible_db canonical values
  3. LLM guesses (metadata only, never authoritative)

### 3.5 DSN centralization violations

- All DB access must go through centralized DSN loaders.
- Direct `os.getenv("GEMATRIA_DSN")` or raw DSN strings in code are gotchas.
- These patterns must be surfaced and removed.

---

## 4. How Cursor Uses This Index

Cursor (and any OPS agent) must:

1. Verify that `docs/SSOT/GOTCHAS_INDEX.md` exists.
2. Run `scripts/guards/guard_gotchas_index.py` before feature work.
3. If the guard reports **blocking gotchas**:
   - Stop work (NO-OP).
   - Report the issues and wait for PM instructions.

This applies especially to:

- Phase 8/10 analytics work,
- Phase 15/COMPASS work,
- Housekeeping/AGENTS/docs governance changes,
- Any new phase that touches SSOT.

---

## 5. Updating This Index

Whenever a new class of gotcha is discovered:

1. Add a bullet under the appropriate layer.
2. If it's substantial, create a dedicated SSOT doc:
   - `docs/SSOT/<PHASE_OR_SYSTEM>_GOTCHAS.md`
3. Link it here under Layer 2 (SSOT gotchas).
4. Ensure `scripts/guards/guard_gotchas_index.py` surfaces it if relevant.

This file is the **canonical map** of where problems live.
If it's not in here, it doesn't officially exist as a known gotcha.

---

**Last Updated**: 2025-12-03  
**Maintainer**: PM + Cursor Fixer  
**Review Cadence**: After each major phase completion

### 3.6 Namespace Drift (agentpm → pmagent)

- **Canonical namespace**: `pmagent`
- **Legacy namespace**: `agentpm` (DEPRECATED as of 2025-12-03)
- Any occurrence of `agentpm` in code, imports, or docs is a **naming gotcha**
- Must be surfaced by `guard_gotchas_index.py`
- Must be corrected immediately
- **Option B (Hard Rename)**: No shims or aliases permitted
- Fail-closed enforcement: any `agentpm` reference will break until corrected

