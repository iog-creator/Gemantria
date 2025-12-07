# Phase 8 Bridge Decision — Linking concept_network to Verse Metadata

## PM Decision

1. Canonical Bridge:
   - The official bridge between `concept_network` nodes and verse metadata is the
     **`v_concepts_with_verses`** view.
   - We will NOT mutate `concept_network` to add verse/gematria columns for Phase 15.
   - We will NOT introduce a new mapping table while `v_concepts_with_verses` exists.

2. Rejected Approaches:
   - **Option A (schema mutation)**:
     - ALTER TABLE `concept_network` to add verse metadata is rejected for Phase 15.
   - **Option D (25-concept-only graph)**:
     - Restricting to the 25 legacy concepts with metadata is disallowed.
     - Phase 15 must operate on the full ~1,733-node graph.

3. Optional / Future Work:
   - **Option C (populate `verse_noun_occurrences`)**
     - May be implemented later for richer analytics.
     - It is NOT a prerequisite for Phase 8 metadata enrichment.

## Implementation Strategy

- Node export (in `scripts/export_graph.py`) MUST:
  - Continue to use `concept_network` as the primary node source.
  - LEFT JOIN `v_concepts_with_verses` using the shared concept ID.
  - Extract from the view:
    - `gematria_value` → node `gematria`
    - `book_source`   → node `book`
    - `verses` JSONB  → node `chapter`, `verse`, and computed `position`

- Phase 8 temporal analytics:
  - Will consume `position`, `chapter`, `verse`, and `gematria` from graph nodes
  - Will be considered blocked until the enrichment is implemented and
    `total_series > 0` in `exports/temporal_patterns.json`.

## Governance Alignment

This decision aligns with:

- `PHASE8_METADATA_ENRICHMENT_DB_SCHEMA.md`
- `PHASE8_METADATA_ENRICHMENT_PLAN.md`
- `GEMATRIA_DSN_GOVERNANCE.md`
- Phase 14 DB-first gematria and lexicon rules
- Phase 15 COMPASS structural completeness requirements
- Rule-050/051/052 and Rule-070 (no code-only fallbacks when DB is required)
