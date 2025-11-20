# DM-002 — Canonical vs Archive Classification Plan

## Purpose

DM-001 created a Postgres-backed doc registry (`control.kb_document`) and a
duplicates report (`docs/analysis/DOC_DUPLICATES_REPORT.md`).

DM-002 defines how we:

- Decide which docs are CANONICAL vs ARCHIVE candidates.
- Keep a small human review surface for ambiguous cases.
- Eventually move/archive non-canonical docs safely.

This document is the SSOT for DM-002 behavior.

## Inputs

1. `control.kb_document` (DM-001):

   - path
   - title
   - doc_type guess
   - content_hash
   - size_bytes
   - mtime
   - status (initially unreviewed, etc.)

2. `docs/analysis/DOC_DUPLICATES_REPORT.md`:

   - Groups of files that share the same content_hash.
   - Human-readable structure (Group N headings, path lists).

## Desired Outputs

1. Classification rules (conceptual):

   - `is_canonical` (boolean)
   - `status` enum concepts:
     - `canonical`
     - `archive_candidate`
     - `archived`
     - `needs_review`
     - `unreviewed`

2. Preview report:

   - `docs/analysis/DOC_DM002_CANONICAL_PREVIEW.md`
   - Shows duplicate groups with:
     - Proposed canonical doc path.
     - Proposed archive_candidate docs.
     - Reasoning (based on heuristics).

3. Future DB integration (later migration):

   - Add `is_canonical` + `status` to `control.kb_document`.
   - Persist canonical/archive decisions from the preview.

4. Future archival tool (DM-00X):

   - `pmagent docs apply-archive-plan`
   - Reads DB decisions and moves archive docs into `archive/docs/...`
   - Writes a receipt (what moved, counts, etc.)

## Heuristics (first pass)

For each duplicate group:

1. Prefer paths under `docs/SSOT/` as canonical.
2. Otherwise prefer paths NOT under `archive/`.
3. If still tied, prefer shorter paths (fewer segments).
4. If still tied, pick lexicographically smallest path.

All non-canonical members of a group become `archive_candidate` for preview.

Special cases:

- 0-byte duplicates (empty files) are likely archive or noise.
- Files under known archive or evidence directories default to archive_candidate
  unless clearly marked as current/SSOT.

## Constraints

- DM-002 PREVIEW MUST NOT:

  - Change the DB.
  - Move or delete files.
  - Update status fields.

- DM-002 PREVIEW MUST:

  - Be deterministic with respect to the current report.
  - Be intelligible to the Orchestrator (plain-English reasoning where possible).
  - Produce a file small enough to skim in sections.

