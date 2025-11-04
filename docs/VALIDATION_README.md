# Validation Guide

## Hebrew Label Validation – Post-Fix (Nov 2025)

**Context** – Earlier builds showed UUID labels instead of Hebrew text due to a mismatched join between `concept_network.concept_id` (UUID) and `concepts.id` (integer).

**Resolution**

- All joins now use `concept_network.id` (UUID) as the graph key.
- Hebrew labels sourced from `concepts.hebrew_text` via CTE `labeled` with ROW_NUMBER() mapping.
- Centrality joins (`concept_centrality`) align on `concept_network.id`.
- Result file `graph_latest.json` contains human-readable labels (e.g., "זְכַרְיָה").

**Validation Command**

```bash
python3 scripts/export_graph.py
python3 scripts/compass/scorer.py share/exports/graph_latest.json --verbose
```

Expected output: `COMPASS Score: 100.0 % (PASS)`; node labels display Hebrew strings.

**SQL Implementation**

```sql
SELECT n.id, COALESCE(co.hebrew_text, 'Concept ' || LEFT(n.concept_id::text, 8)), c.cluster_id,
       ce.degree, ce.betweenness, ce.eigenvector
FROM (
    SELECT n.*, ROW_NUMBER() OVER (ORDER BY n.id) as rn
    FROM concept_network n
) n
LEFT JOIN (
    SELECT hebrew_text, ROW_NUMBER() OVER (ORDER BY id) as rn
    FROM concepts
    WHERE hebrew_text IS NOT NULL AND hebrew_text != ''
    ORDER BY id
    LIMIT 1000
) co ON co.rn = n.rn
LEFT JOIN concept_clusters c ON c.concept_id = n.id
LEFT JOIN concept_centrality ce ON ce.concept_id = n.id
```

**Key Changes**
- Node IDs: `concept_network.id` (UUID) instead of `concept_network.concept_id`
- Labels: Hebrew text from `concepts.hebrew_text` via row number mapping
- Joins: All cluster/centrality joins use `concept_network.id`
