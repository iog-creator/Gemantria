# ADR-029: Schema Normalization & Staging Infrastructure

## Status
Accepted

## Context
During the Genesis pipeline run, critical data corruption was discovered where:
- `concept_relations` table had NULL `dst_concept_id` values (edges had no destination)
- `relation_type` contained timestamps instead of relation types
- Database export was correct but insertion logic failed catastrophically
- Pipeline completed successfully but produced unusable graph data

This exposed fundamental gaps in data integrity protection within the pipeline architecture.

## Decision
Implement a comprehensive **Schema Normalization & Staging Infrastructure** that provides fail-closed data integrity protection through:

### 1. Staging Schema Layer
- `staging.*_norm` tables with strict constraints (NOT NULL, CHECK constraints)
- Canonical field mappings and data types
- Pre-validation before production writes

### 2. JSON Export Normalization
- `scripts/normalize_exports.py` for canonical field mappings
- Handles variant field names (`source`/`src`, `target`/`dst`, etc.)
- Produces `exports/graph_latest.normalized.json`

### 3. Runtime Insertion Guards
- `scripts/guard_relations_insert.py` validates relations before DB insertion
- Checks for NULL endpoints, invalid weights, proper field presence
- Fails fast on data integrity violations

### 4. Makefile Integration
- `make schemas.normalize` - canonical JSON export normalization
- `make exports.guard` - pre-insertion validation
- Integrated into CI pipeline for automated protection

## Implementation Details

### Staging Schema Structure
```sql
-- Canonical concepts with strict validation
CREATE TABLE staging.concepts_norm (
  concept_id    TEXT PRIMARY KEY,
  lemma         TEXT NOT NULL,
  surface       TEXT,
  book          TEXT NOT NULL,
  metadata      JSONB DEFAULT '{}'::jsonb
);

-- Relations with enforced constraints
CREATE TABLE staging.concept_relations_norm (
  src_concept_id  TEXT NOT NULL,
  dst_concept_id  TEXT NOT NULL,
  relation_type   TEXT NOT NULL CHECK (relation_type IN ('semantic','cooccur','lemma','theology','other')),
  weight          DOUBLE PRECISION NOT NULL CHECK (weight >= 0 AND weight <= 1),
  cosine          DOUBLE PRECISION CHECK (cosine >= 0 AND cosine <= 1),
  rerank_score    DOUBLE PRECISION CHECK (rerank_score >= 0 AND rerank_score <= 1),
  class           TEXT NOT NULL CHECK (class IN ('strong','weak','very_weak')),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Normalization Logic
```python
def norm_edge(e):
    return {
        "src_concept_id": e.get("source") or e.get("src") or e.get("from"),
        "dst_concept_id": e.get("target") or e.get("dst") or e.get("to"),
        "relation_type": (e.get("relation_type") or e.get("type") or "semantic").lower(),
        "weight": float(e.get("weight") or e.get("strength") or e.get("edge_strength") or 0),
        "cosine": float(e.get("cosine") or e.get("similarity") or 0),
        "rerank_score": float(e.get("rerank_score") or e.get("rerank") or 0),
        "class": "strong" if weight >= 0.90 else "weak" if weight >= 0.75 else "very_weak"
    }
```

### Guard Validation
```python
# Pre-insert validation
bad = [r for r in relations if not r.get("src_concept_id") or not r.get("dst_concept_id")]
if bad:
    sys.exit(2)  # Fail closed on integrity violations
```

## Alternatives Considered

### Alternative 1: Post-Processing Validation Only
- Only validate after insertion
- **Rejected**: Too late to prevent corruption; requires expensive rollback operations

### Alternative 2: Inline Validation in Pipeline
- Add validation directly in pipeline nodes
- **Rejected**: Increases pipeline complexity; harder to test; couples validation with processing

### Alternative 3: Database Triggers
- Use PostgreSQL triggers for constraint enforcement
- **Rejected**: Limited to DB-level checks; can't validate complex business rules; harder to test

### Alternative 4: Schema Migration Only
- Fix production schema constraints
- **Rejected**: Doesn't prevent future column mapping errors; no pre-validation of exports

## Consequences

### Positive
- **Fail-closed safety**: Pipeline stops on data integrity violations
- **Early detection**: Issues caught before DB writes
- **Reproducible normalization**: Canonical JSON format for all exports
- **CI integration**: Automated validation prevents regression
- **Debugging support**: Clear error messages for data issues

### Negative
- **Performance overhead**: Additional validation steps
- **Maintenance complexity**: More moving parts to maintain
- **Storage duplication**: Staging tables require additional space

### Neutral
- **No breaking changes**: Existing pipeline continues to work
- **Incremental adoption**: Can be added gradually to other books
- **Testing coverage**: New test cases for normalization logic

## Testing Evidence

### Staging Integrity Validation
```sql
-- All checks pass
bad_nodes=0, bad_edges=0, orphan_src=0, orphan_dst=0
```

### Guard Script Validation
```
RELATIONS_INSERT_GUARD_OK
```

### Production Data Integrity
```sql
-- Clean relations with proper constraints
SELECT relation_type, COUNT(*) FROM concept_relations GROUP BY relation_type;
-- semantic | 1855

SELECT COUNT(*) FROM concept_relations WHERE dst_concept_id IS NULL;
-- 0 (fixed from 1855 corrupted records)
```

## Compliance
- **Rule 029 (ADR Coverage)**: ✅ Documented architectural change
- **Rule 027 (Docs Sync)**: ✅ AGENTS.md updated with staging approach
- **Rule 037 (Data Persistence)**: ✅ Schema normalization ensures data completeness
- **Rule 038 (Exports Smoke)**: ✅ Guards prevent invalid exports

## References
- [AGENTS.md Pipeline Architecture](AGENTS.md#integrated-pipeline-architecture)
- [Rule 029 ADR Coverage](.cursor/rules/029-adr-coverage.mdc)
- [Genesis Data Corruption Audit](scripts/audit_genesis_db.py)
- [Schema Normalization Scripts](scripts/normalize_exports.py)
- Related: ADR-016 (Data Persistence), ADR-017 (Schema Validation)

## Notes
This infrastructure provides the foundation for fail-safe data pipelines. Future pipeline runs should route through staging validation before production writes, preventing the type of corruption seen in the Genesis incident.
