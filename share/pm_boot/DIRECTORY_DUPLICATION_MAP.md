# Directory Duplication Map — Structural Cleanup Analysis

**Status:** ANALYSIS COMPLETE  
**Date:** 2025-12-07  
**Purpose:** Map all duplicate/confusing directory structures for PM planning

---

## Executive Summary

The repository has **significant directory duplication** that creates confusion and maintenance overhead:

- **ADRs**: 2 directories (`docs/adr/` vs `docs/ADRs/`)
- **Schemas**: 3 locations (`docs/schema/`, `docs/schemas/`, root `schemas/`)
- **SQL**: 3 locations (`docs/sql/`, `db/sql/`, `scripts/sql/`)
- **SSOT**: 2 locations (`docs/SSOT/`, `src/ssot/`)
- **Analysis**: 2 directories (case-sensitive: `docs/analysis/` vs `docs/ANALYSIS/`)
- **OPS**: 2 directories (case-sensitive: `docs/ops/` vs `docs/OPS/`)

**Total Impact:** ~200+ files across duplicate directories, unclear ownership, maintenance confusion.

---

## 1. ADR Directories

### `docs/adr/` (5 files)
- **Contents:**
  - `029-remove-legacy-scripts.md`
  - `030-db-seeded-noun-source.md`
  - `ADR-063-code-exec-ts.md`
  - `ADR-064-rfc3339-fast-lane.md`
  - `AGENTS.md`
- **Status:** Appears to be **newer, smaller subset** (ADRs 029-030, 063-064)
- **Last modified:** Nov 12, 2025

### `docs/ADRs/` (35 files)
- **Contents:**
  - Full ADR set: `ADR-000` through `ADR-064+`
  - Includes all numbered ADRs
  - `AGENTS.md` present
- **Status:** Appears to be **canonical, comprehensive** ADR directory
- **Last modified:** Dec 6, 2025

### **Recommendation:**
- **Keep:** `docs/ADRs/` (canonical, comprehensive)
- **Merge:** Move `docs/adr/` files into `docs/ADRs/` (verify no duplicates)
- **Delete:** `docs/adr/` after merge

---

## 2. Schema Directories

### `docs/schema/` (2 files)
- **Contents:**
  - `AGENTS.md`
  - `SCHEMA.md` (documentation)
- **Status:** **Documentation only** (not actual schemas)
- **Purpose:** Schema documentation/guidelines

### `docs/schemas/` (8 files)
- **Contents:**
  - `AGENTS.md`
  - `graph-correlations.schema.md`
  - `graph-patterns.schema.md`
  - `graph-stats.schema.md`
  - `pattern-forecast.schema.md`
  - `SSOT_ai-nouns.v1.schema.md`
  - `SSOT_graph.v1.schema.md`
  - `temporal-patterns.schema.md`
- **Status:** **Markdown schema documentation** (`.schema.md` files)
- **Purpose:** Human-readable schema specs

### `schemas/` (root, ~20+ files)
- **Contents:**
  - `ai-nouns.schema.json`
  - `gematria_output.schema.json`
  - `graph-patterns.schema.json`
  - `graph.schema.json`
  - `graph-stats.schema.json`
  - `mcp_ingest_envelope.v1.schema.json`
  - `mcp_proof_snapshot.v1.schema.json`
  - Subdirectories: `biblescholar/`, `common/`
- **Status:** **JSON Schema files** (actual validation schemas)
- **Purpose:** Machine-readable JSON Schema validation

### **Recommendation:**
- **Keep:** `schemas/` (root) — canonical JSON Schema location
- **Keep:** `docs/schemas/` — human-readable schema documentation (Markdown)
- **Merge:** `docs/schema/` content into `docs/schemas/` (if valuable) or delete if redundant
- **Rationale:** JSON schemas (root) vs documentation (docs) is a valid separation

---

## 3. SQL Directories

### `docs/sql/` (2 files)
- **Contents:**
  - `AGENTS.md`
  - `READONLY_ROLE_TEMPLATE.sql` (template/documentation)
- **Status:** **SQL documentation/templates**
- **Purpose:** SQL reference materials

### `db/sql/` (2 files)
- **Contents:**
  - `078_mcp_knowledge_seed.sql`
  - `078_mcp_knowledge.sql`
- **Status:** **Database seed/initialization SQL**
- **Purpose:** Database setup scripts

### `scripts/sql/` (5+ files)
- **Contents:**
  - `guard_hebrew_export.sql`
  - `ops_ssot_always_apply.sql`
  - `pg/` subdirectory
- **Status:** **Operational SQL scripts** (guards, ops)
- **Purpose:** Runtime SQL utilities

### **Recommendation:**
- **Keep all three** — they serve different purposes:
  - `docs/sql/` — documentation/templates
  - `db/sql/` — database initialization/seeds
  - `scripts/sql/` — operational scripts
- **Rationale:** Different purposes justify separation, but naming could be clearer

---

## 4. SSOT Directories

### `docs/SSOT/` (142 files)
- **Contents:**
  - All SSOT documentation (PM contracts, phase indexes, plans, etc.)
  - `AGENTS.md`
  - Phase documentation
  - Contract files
- **Status:** **Canonical SSOT documentation location**
- **Purpose:** Single Source of Truth for documentation

### `src/ssot/` (2 files)
- **Contents:**
  - `AGENTS.md`
  - `noun_adapter.py` (Python implementation)
- **Status:** **Code-level SSOT** (Python modules)
- **Purpose:** SSOT implementation in code (noun adapter)

### **Recommendation:**
- **Keep both** — they serve different purposes:
  - `docs/SSOT/` — documentation SSOT
  - `src/ssot/` — code implementation of SSOT logic
- **Rationale:** Documentation vs implementation is a valid separation

---

## 5. Case-Sensitive Duplicates

### `docs/analysis/` (10 files)
- **Status:** Lowercase
- **Contents:** Analysis documentation

### `docs/ANALYSIS/` (2 files)
- **Contents:**
  - `AGENTS.md`
  - `rule-enforcement-gaps.md`
- **Status:** Uppercase, minimal content
- **Last modified:** Nov 15, 2025

### **Recommendation:**
- **Merge** `docs/ANALYSIS/` → `docs/analysis/`
- **Check** if `rule-enforcement-gaps.md` is unique or duplicate
- **Delete** `docs/ANALYSIS/` after merge

### `docs/ops/` (6 files)
- **Status:** Lowercase
- **Contents:** OPS documentation

### `docs/OPS/` (2 files)
- **Contents:**
  - `AGENTS.md`
  - `NEXT_STEPS.md`
- **Status:** Uppercase, minimal content
- **Last modified:** Nov 15, 2025

### **Recommendation:**
- **Merge** `docs/OPS/` → `docs/ops/`
- **Check** if `NEXT_STEPS.md` conflicts with root `NEXT_STEPS.md`
- **Delete** `docs/OPS/` after merge

---

## 6. Summary Table

| Category | Directories | Files | Action |
|----------|-------------|-------|--------|
| **ADRs** | `docs/adr/` (5) vs `docs/ADRs/` (35) | 40 | **MERGE** `adr/` → `ADRs/`, delete `adr/` |
| **Schemas** | `docs/schema/` (2) vs `docs/schemas/` (8) vs `schemas/` (20+) | 30+ | **KEEP** `schemas/` + `docs/schemas/`, **MERGE/DELETE** `docs/schema/` |
| **SQL** | `docs/sql/` (2) vs `db/sql/` (2) vs `scripts/sql/` (5+) | 9+ | **KEEP ALL** (different purposes, but document clearly) |
| **SSOT** | `docs/SSOT/` (142) vs `src/ssot/` (?) | 142+ | **KEEP BOTH** (docs vs code) |
| **Analysis** | `docs/analysis/` (10) vs `docs/ANALYSIS/` (2) | 12 | **MERGE** → `analysis/`, delete `ANALYSIS/` |
| **OPS** | `docs/ops/` (6) vs `docs/OPS/` (2) | 8 | **MERGE** → `ops/`, delete `OPS/` |

---

## 7. Recommended Cleanup Plan

### Phase 1: Case-Sensitive Duplicates (Low Risk)
1. **Merge `docs/ANALYSIS/` → `docs/analysis/`**
   - Check for file conflicts
   - Move files
   - Delete `docs/ANALYSIS/`

2. **Merge `docs/OPS/` → `docs/ops/`**
   - Check for file conflicts
   - Move files
   - Delete `docs/OPS/`

### Phase 2: ADR Consolidation (Medium Risk)
1. **Merge `docs/adr/` → `docs/ADRs/`**
   - **Unique files in `adr/`:** `029-remove-legacy-scripts.md`, `030-db-seeded-noun-source.md`, `ADR-063-code-exec-ts.md`, `ADR-064-rfc3339-fast-lane.md`
   - **Check:** Verify these don't exist in `ADRs/` (diff shows they're unique)
   - Move unique files to `docs/ADRs/`
   - Update any references
   - Delete `docs/adr/`

### Phase 3: Schema Documentation Cleanup (Low Risk)
1. **Investigate `docs/schema/` contents**
   - If redundant with `docs/schemas/`, delete
   - If unique, merge into `docs/schemas/`
   - Delete `docs/schema/`

### Phase 4: Documentation & Verification
1. **Update all references** in:
   - `Makefile` targets
   - `scripts/` imports
   - `docs/SSOT/` documentation
   - DMS registry
2. **Run guards:**
   - `make ops.kernel.check`
   - `make reality.green`
   - `make guard.root.surface`
3. **Update SSOT docs** with new structure

---

## 8. Files Requiring Reference Updates

After cleanup, these files may need updates:
- `Makefile` (any targets referencing old paths)
- `scripts/create_agents_md.py` (directory discovery)
- `scripts/guards/guard_dms_share_alignment.py` (path checks)
- `docs/SSOT/SHARE_FOLDER_ANALYSIS.md` (directory structure docs)
- `docs/README.md` (documentation structure)
- DMS registry (if paths are tracked)

---

## 9. Acceptance Criteria

- [ ] All case-sensitive duplicates merged
- [ ] `docs/adr/` merged into `docs/ADRs/`
- [ ] `docs/schema/` resolved (merged or deleted)
- [ ] All references updated (Makefile, scripts, docs)
- [ ] `make ops.kernel.check` passes
- [ ] `make reality.green` passes
- [ ] `make guard.root.surface` passes
- [ ] SSOT documentation updated

---

**End of Map**
