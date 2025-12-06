# Phase 8 Metadata Enrichment Plan — export_graph.py

## 1. PM Decision

- Option 1 (Metadata Enrichment) is **approved**.
- Phase 8 temporal analytics is **required** for Phase 15 COMPASS structural completion.
- Option 2 (deferring temporal analytics) is **not adopted**; any such change would require a future ADR + SSOT update.

## 2. Current State

- Graph export:
  - `exports/graph_latest.json` has ~1,733 nodes and 14,330 edges (from DB).
  - Nodes currently include:
    - `betweenness`, `cluster`, `degree`, `eigenvector`, `noun_id`, `surface`, etc.
  - Nodes **do not** include:
    - `position`, `chapter`, `verse`, `gematria`.

- Phase 8 (`scripts/temporal_analytics.py`):
  - Requires nodes with:
    - `position` (or `chapter` + `verse`)
    - `gematria`
  - With current metadata, it loads 1,733 nodes but produces:
    - `total_series = 0`, `patterns = 0`.

## 3. Enrichment Requirements

### 3.1 Fields to Add

For verse-based nodes (at minimum for Genesis, ideally all books):

Each node in `exports/graph_latest.json` SHOULD be enriched with:

- `position`: integer verse index (e.g., global or per-book position)
- `chapter`: integer chapter number
- `verse`: integer verse number
- `gematria`: numeric value used by Gematria module

These values MUST come from database/DMS sources, not hard-coded constants.

### 3.2 Data Sources (to be confirmed by OPS)

Candidate DB tables / views (fill in concretely after inspection):

- `bible.verses` (or equivalent) with:
  - `book`, `chapter`, `verse`, `position_index`, `gematria_value`, etc.
- A mapping between graph nodes (`noun_id` or other key) and verses:
  - e.g., `concept_network` or a join table linking `noun_id` → verse_id.

OPS must document:

- **Node key** used for join (e.g., `noun_id`, `verse_id`).
- **Exact table/view names** and column names used for enrichment.

## 4. Implementation Hook

Modify `scripts/export_graph.py` where nodes are fetched/built:

- After node records are loaded from DB, perform a join/enrichment step to attach:
  - `position`
  - `chapter`
  - `verse`
  - `gematria`

Constraints:

- Enrichment must be derived from DB (DMS) tables, not local JSON files.
- For nodes that cannot be mapped to verses:
  - It is acceptable for them to lack these fields; they will simply not participate in Phase 8 temporal patterns.

## 5. Acceptance Criteria

After enrichment and re-export:

1. `exports/graph_latest.json` metadata:
   - `node_count` remains ~1,733 (or higher if new nodes are added).
   - Sample nodes (especially Genesis-related) show the new fields:
     - `position`, `chapter`, `verse`, `gematria`.

2. Phase 8 rerun:
   - `python scripts/temporal_analytics.py` completes without errors.
   - `exports/temporal_patterns.json` shows:
     - `metadata.total_series > 0`
     - `.temporal_patterns | length > 0`
     - At least one pattern object with `timestamps` and `values`.

3. COMPASS readiness:
   - Temporal patterns are structurally present so they can later be mapped into the unified envelope for COMPASS.

## 6. Out of Scope (for this plan)

- Phase 10 correlation analytics (scipy install, `concept_correlations` view).
- Wiring temporal data into the unified envelope (handled in a separate mapping doc).
- Any changes to COMPASS thresholds or scoring weights.
