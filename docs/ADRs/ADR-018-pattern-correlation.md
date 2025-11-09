# ADR-018: Pattern Correlation Engine

## Status

Accepted

## Context

The project needs to identify meaningful relationships between concepts beyond simple co-occurrence. While basic network analysis shows connections, correlation analysis reveals statistically significant patterns in embedding spaces that indicate conceptual relationships. This enables deeper insights into thematic connections and semantic structures within the biblical text.

## Decision

Implement a pattern correlation engine that analyzes relationships between concept embeddings using statistical correlation methods, with both database-optimized and Python fallback implementations.

## Rationale

- **Statistical Rigor**: Correlation analysis provides mathematically grounded relationship detection
- **Semantic Depth**: Embedding correlations reveal conceptual similarities beyond surface connections
- **Scalability**: Database implementation for performance, Python fallback for flexibility
- **Validation**: Statistical significance testing ensures meaningful relationships
- **Integration**: Seamless integration with existing export and visualization pipelines

## Alternatives Considered

1. **Cosine Similarity Only**: Simple vector similarity without statistical testing
   - Pros: Simpler implementation, faster computation
   - Cons: No statistical significance, potentially misleading results

2. **Graph-based Correlations**: Network analysis without embedding correlations
   - Pros: Works with existing graph structure
   - Cons: Misses semantic relationships not captured in graph edges

3. **External ML Services**: Cloud-based correlation analysis
   - Pros: Advanced algorithms, managed infrastructure
   - Cons: External dependencies, data privacy concerns, cost

## Consequences

### Implementation Requirements
- Create database view for correlation calculations
- Implement Python fallback using scipy.stats.pearsonr
- Add correlation export and reporting functions
- Integrate with existing pipeline and validation

### Positive Outcomes
- Enhanced pattern discovery capabilities
- Statistically validated concept relationships
- Improved visualization and analysis insights
- Robust fallback mechanisms for reliability

### Risks and Mitigations
- **Performance**: Correlation calculations on large datasets (mitigated by database optimization)
- **Statistical Assumptions**: Pearson correlation assumptions (mitigated by validation and alternatives)
- **Complexity**: Dual implementation maintenance (mitigated by clear abstraction layers)

## Related Rules

000 (Always-Apply), 006 (AGENTS.md Governance), 013 (Report Verification), 021 (Stats Proof), 022 (Viz Contract Sync), 030 (Pattern Correlation Validation)
<!-- alwaysapply.sentinel: 050,051,052 source=fallback-default -->
- Rule-050
- Rule-051
- Rule-052
<!-- alwaysapply.sentinel: 050,051,052 source=fallback-default -->
- Rule-050
- Rule-051
- Rule-052
<!-- alwaysapply.sentinel: 050,051,052 source=fallback-default -->
- Rule-050
- Rule-051
- Rule-052
<!-- alwaysapply.sentinel: 050,051,052 source=fallback-default -->
- Rule-050
- Rule-051
- Rule-052
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
