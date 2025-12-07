# PM Share Layout — Phase 15 (Design Stub)

**Date**: 2025-01-XX  
**Status**: Design proposal (not yet implemented)  
**Related**: `SHARE_FOLDER_STRUCTURE.md`, `PM_SHARE_FOLDER_ENHANCEMENTS.md`, Rule 071 (Portable JSON is not Plan SSOT)

---

## 1. Purpose

This document defines the **PM-facing share folder layout** for Phase 15. This layout provides a structured, phase-specific view of DMS data and repo state, designed to reduce cognitive load when managing a specific phase.

**Key Principle**: All files under this layout are **generated from the DMS + repo**, and are **NOT** a new SSOT.

---

## 2. Directory Structure

```text
share/pm/
  phase15/
    00_index.md
    10_plan_snapshot.md
    20_wave1_status.md
    30_wave2_status.md
    40_wave3_status.md
    50_compass_alignment.md
    60_validation_log.md
```

---

## 3. Design Rules

### 3.1 DMS as Single Source of Truth

* **Postgres DMS is the only SSOT.**
* Files in `share/pm/phase15/` are **views** generated from:
  * DMS tables (`control.doc_registry`, `control.doc_version`, `control.doc_sync_state`, `control.hint_registry`, `control.agent_run`, etc.)
  * Current repo docs (`docs/SSOT/PHASE15_PLAN.md`, `docs/SSOT/PHASE15_WAVE3_PLAN.md`, `docs/SSOT/PHASE15_COMPASS_ALIGNMENT_ANALYSIS.md`)
* These files **must not** be manually edited.
* If share and DMS disagree, **DMS wins**; the fix is to regenerate the exports.

### 3.2 Relationship to Existing Share System

This layout **extends** the existing `share/` folder system:

* **Reuses**: Existing DMS export infrastructure (`scripts/db/export_dms_tables.py`, `pmagent plan next`, etc.)
* **Reuses**: DMS-first generation pattern (query Postgres, derive summaries)
* **Extends**: Adds phase-specific subdirectory structure (currently `share/` is flat)
* **Requires**: Modification to `scripts/sync_share.py` to allow `share/pm/` subdirectory (currently enforces flat structure)

### 3.3 Fixed Structure Contract

* Filenames and roles are **fixed** (as defined in Section 4).
* Cursor/PM agents don't drop random markdowns into `share/pm/phase15/`; they fill these **specific slots**.
* Exports must be **DMS-driven**, not "read files and summarize."
* These files are a **navigation layer**, not the whole universe. For deeper detail, query DMS directly or regenerate full exports.

---

## 4. File Roles

### `00_index.md`
* **Purpose**: Human-friendly TOC and quick links for Phase 15 exports.
* **Source**: Generated from DMS tags + `doc_registry` (which docs are tagged "phase15", their latest version summary).
* **Content**: Links to other files in this folder, plus brief summary of Phase 15 scope.

### `10_plan_snapshot.md`
* **Purpose**: Phase 15 plan slice (not full `MASTER_PLAN.md`).
* **Source**: 
  * `docs/SSOT/PHASE15_PLAN.md` (full content)
  * Cross-referenced with `MASTER_PLAN.md` for context, but trimmed to Phase 15 scope.
* **Content**: Phase 15 goals, waves, constraints, acceptance criteria.

### `20_wave1_status.md`, `30_wave2_status.md`, `40_wave3_status.md`
* **Purpose**: Short status per wave (definition of done, what's landed, current blockers, last validation result).
* **Source**: 
  * DMS run records / `hint_registry` / `control.agent_run`
  * Structured status from tagged docs (e.g., `PHASE15_WAVE3_PLAN.md`)
* **Content**: 
  * Wave definition of done
  * Completed items
  * Current blockers
  * Last validation result (PASS/FAIL/BLOCKED)

### `50_compass_alignment.md`
* **Purpose**: Summary of COMPASS/blend alignment and gaps.
* **Source**: 
  * `docs/SSOT/PHASE15_COMPASS_ALIGNMENT_ANALYSIS.md`
  * Verified against DMS (which scripts exist, which latest runs we have).
* **Content**: 
  * What's old infra (already exists)
  * What's new alignment (mechanical fixes)
  * What's still mock (`extract_all.py`) vs real
  * COMPASS score history

### `60_validation_log.md`
* **Purpose**: Chronological log of Wave-3 validation runs and outcomes.
* **Source**: 
  * DMS `agent_run` records filtered by phase15/wave3 tags
  * `reality.green` results
  * RAG live test summaries
  * Graph/export state snapshots
  * COMPASS scores
* **Content**: 
  * Date/time
  * Validation type (reality.green, RAG live, COMPASS, etc.)
  * Result (PASS/FAIL/BLOCKED with reason)
  * Key metrics/scores

---

## 5. Implementation Requirements

### 5.1 Generator Commands

Implementation will add one or more `pmagent`/DMS-driven commands that:

* Query DMS + repo
* Write/update these files under `share/pm/phase15/`
* Ensure no logic reads share as a primary truth source; all reads should go to DMS or the repo, with share as a convenience export.

**Proposed commands** (design only, not yet implemented):

```bash
# Regenerate all Phase 15 PM share files from DMS
pmagent share phase15 generate

# Regenerate specific file
pmagent share phase15 generate --file 40_wave3_status.md

# List available phase folders
pmagent share list-phases
```

### 5.2 Integration with Existing System

* **Makefile target**: Add `make pm.share.phase15` that calls the generator
* **Housekeeping integration**: Optionally run during `make housekeeping` (or keep as on-demand)
* **DMS sync modification**: Update `scripts/sync_share.py` to allow `share/pm/` subdirectory (currently deletes all subdirectories)

### 5.3 Archive Policy

* Old phase folders should be archived or removed when no longer active
* Consider `share/pm/index.md` that only links current active phases
* Keep folder count bounded (don't accumulate 20+ phase folders)

---

## 6. Usage Pattern

With this PM share layer in place, the PM workflow becomes:

1. **Regenerate exports**: `pmagent share phase15 generate` (or `make pm.share.phase15`)
2. **Review status**: Cursor pastes `40_wave3_status.md` + `50_compass_alignment.md` into chat
3. **Treat as dashboard**: PM uses these as phase-local navigation, not scanning 44+ files
4. **Fix discrepancies**: If export contradicts DMS, regenerate (don't edit the file)

---

## 7. Open Questions

* Should this be **on-demand** (regenerate when PM asks) or **automatic** (during `make housekeeping`)?
* Should we support **multiple active phases** simultaneously, or only one at a time?
* How do we **archive** old phase folders? (Move to `share/pm/archive/phase15/`? Delete after N months?)
* Should `share/pm/` be **tracked in DMS** (`control.doc_registry` with `share_path`), or remain as pure exports?

---

## 8. Related Documentation

* `docs/SSOT/SHARE_FOLDER_STRUCTURE.md` - Current share folder structure (flat)
* `docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md` - Previous share folder enhancements
* `docs/SSOT/PM_CONTRACT.md` - PM contract (Sections 2.7, 2.8 on planning context)
* `scripts/sync_share.py` - Current DMS sync script (enforces flat structure)
* `scripts/db/export_dms_tables.py` - DMS table export infrastructure

---

## 9. Next Steps

1. **PM review**: Confirm this design aligns with PM workflow needs
2. **Implementation design**: Design generator commands and DMS queries
3. **Sync script modification**: Update `scripts/sync_share.py` to allow `share/pm/` subdirectory
4. **Makefile integration**: Add `make pm.share.phase15` target
5. **Testing**: Verify DMS-first generation and no manual editing

