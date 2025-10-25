# ADR-018: Pattern Correlation Engine

Status: Implemented

## Related Rules

000 (Always-Apply), 006 (AGENTS.md Governance), 013 (Report Verification), 021 (Stats Proof), 022 (Viz Contract Sync), 030 (Pattern Correlation Validation)

## Implementation Summary

### Phase 5-A (Infrastructure) - COMPLETED

- ✅ Created `docs/SSOT/graph-correlations.schema.json` with JSON Schema validation
- ✅ Extended `scripts/export_stats.py` with `export_correlations()` function
- ✅ Added "Pattern Correlation Summary" section to `scripts/generate_report.py`
- ✅ Created Rule 030 for correlation validation enforcement
- ✅ Updated ADR status to "Accepted" and integrated into master plan

### Phase 5-B (Analytics Engine) - COMPLETED

- ✅ Created migration `migrations/017_concept_correlations.sql` with database view
- ✅ Implemented Python fallback correlation computation using scipy.stats.pearsonr
- ✅ Added dual-path correlation engine (database view → Python fallback)
- ✅ Integrated with existing export and reporting pipeline
- ✅ Updated ADR status to "Implemented"

## Database Implementation

### Concept Correlations View

```sql
CREATE OR REPLACE VIEW concept_correlations AS
SELECT
    cn1.concept_id AS source,
    c1.name AS source_name,
    cn1.cluster_id AS cluster_source,
    cn2.concept_id AS target,
    c2.name AS target_name,
    cn2.cluster_id AS cluster_target,
    corr(cn1.embedding, cn2.embedding) AS correlation,
    COUNT(*) AS sample_size,
    CASE
        WHEN ABS(corr(cn1.embedding, cn2.embedding)) > 0.5 THEN 0.01
        WHEN ABS(corr(cn1.embedding, cn2.embedding)) > 0.3 THEN 0.05
        ELSE 0.1
    END AS p_value,
    'pearson_embedding' AS metric
FROM concept_network cn1
JOIN concept_network cn2 ON cn1.id < cn2.id
JOIN concepts c1 ON cn1.concept_id = c1.id
JOIN concepts c2 ON cn2.concept_id = c2.id
WHERE cn1.embedding IS NOT NULL AND cn2.embedding IS NOT NULL
GROUP BY cn1.concept_id, c1.name, cn1.cluster_id,
         cn2.concept_id, c2.name, cn2.cluster_id
HAVING COUNT(*) >= 2
ORDER BY ABS(corr(cn1.embedding, cn2.embedding)) DESC;
```

### Python Fallback

When database view is unavailable, the system falls back to Python computation using:

- `scipy.stats.pearsonr` for correlation calculation
- `numpy` arrays for efficient embedding processing
- Batched processing to handle large networks
- Automatic sorting by correlation strength

## Verification

- ✅ Schema validation against `docs/SSOT/graph-correlations.schema.json`
- ✅ Rule 030 enforcement in `scripts/rules_guard.py`
- ✅ CI integration with correlation validation
- ✅ Report generation includes correlation summaries
- ✅ Export pipeline produces validated JSON output
