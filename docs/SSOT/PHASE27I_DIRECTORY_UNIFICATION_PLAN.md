# Phase 27.I — Directory Namespace Cleanup (Planning Doc)

## 1. Problem Statement

The repository has significant directory-level duplication and namespace drift,
as documented in docs/SSOT/DIRECTORY_DUPLICATION_MAP.md. This affects:

- ADRs (docs/adr/ vs docs/ADRs/)
- Schemas (docs/schema/, docs/schemas/, root schemas/)
- SQL (docs/sql/, db/sql/, scripts/sql/)
- And other areas called out in the duplication map.

DMS alignment and pm_boot address *file-level* truth and boot surfaces but do
not enforce directory semantics. As a result, agents (PM, OA, Cursor) are
forced to guess which directory is canonical for a given concept.

Phase 27.I introduces a canonical directory model for key namespaces and a
guard to prevent future drift.

## 2. Inputs

Primary input:

- docs/SSOT/DIRECTORY_DUPLICATION_MAP.md

Secondary inputs:

- docs/SSOT/SHARE_FOLDER_ANALYSIS.md
- docs/SSOT/PHASE27_INDEX.md (27.H and prior)
- SSOT_SURFACE exports (for DMS view of tracked docs)

## 3. Target Canonical Directories (Initial Proposal)

This section is an initial proposal and may be refined during implementation.

- ADRs:
  - Canonical: docs/ADRs/
  - Legacy: docs/adr/ (to be archived or merged)

- Schemas:
  - Canonical machine schemas: `schemas/` (JSON Schema files for validation)
  - Canonical documentation: `docs/schemas/` (human-readable schema docs, Markdown)
  - Legacy: `docs/schema/` (pure docs only; merged into `docs/schemas/` or removed)
  - **Out of scope for 27.I:** `docs/SSOT/*.schema.json` (SSOT/domain-specific schemas, governed by existing OPS/temporal rules)

- SQL:
  - Canonical DB SQL: db/sql/
  - Canonical tooling SQL (if needed): scripts/sql/
  - Legacy: docs/sql/ (examples; either moved into docs/ or removed)

(Additional pairs/triples to be filled in from DIRECTORY_DUPLICATION_MAP.md.)

## 4. Phase Deliverables

- A concrete, merged list of canonical directories per concept.
- All shadow/duplicate directories either:
  - removed,
  - moved under archive/,
  - or reduced to pointer docs referencing the canonical location.
- A new guard, e.g. scripts/guards/guard_directory_namespace_policy.py,
  integrated into reality.green, that verifies:
  - No new duplicate directory trees for known concepts.
  - No reintroduction of legacy dirs once cleaned.

## 5. Constraints

- No destructive deletions without:
  - DMS and SSOT verification that nothing canonical lives only in the legacy dir.
  - At least one backup.surfaces run before large moves.
- Changes must be one-feature-per-branch and one-feature-per-PR:
  - Phase 27.I gets its own branch and PR.
  - Phase 27.H remains scoped to pm_boot + DMS + root + AGENTS.

## 6. Execution Plan (High-Level)

1. Cut new branch from main after Phase 27.H merges:
   - Branch name: feat/phase27i-directory-namespace-cleanup

2. Use existing introspection tools (semantic_inventory, reunion_plan) to
   validate which files live under each duplicate directory.

3. Implement the canonicalization moves (per concept) in small steps:
   - ADRs → unify.
   - Schemas → unify.
   - SQL → unify.

4. Add guard_directory_namespace_policy.py and wire into reality.green.

5. Update SHARE_FOLDER_ANALYSIS.md and PHASE27_INDEX.md with final directory
   model and guard behavior.

## 7. Status

- This document is the planning SSOT for Phase 27.I.
- No directory moves have been performed yet; implementation will occur on
  feat/phase27i-directory-namespace-cleanup after Phase 27.H is merged.
