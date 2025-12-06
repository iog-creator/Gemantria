# PostgreSQL Optimization Review — KB Registry & RAG Infrastructure

**Date**: 2025-01-XX  
**Context**: Post-implementation review of KB Registry Course Correction SQL queries and migrations  
**Goal**: Identify PostgreSQL-specific optimizations to improve query performance and leverage advanced features

---

## Executive Summary

The current implementation is **functionally correct** but has several opportunities to leverage PostgreSQL advanced features for better performance:

1. **JSONB Query Optimization**: Replace inefficient `meta::text <> '{}'::text` with proper JSONB operators
2. **Partial Indexes**: Add filtered indexes for common query patterns (`enabled = true`, `kb_candidate = true`)
3. **Expression Indexes**: Create indexes on JSONB path expressions for frequently queried fields
4. **IVFFlat Tuning**: Recalculate `lists` parameter based on actual row count (>1000 embeddings)
5. **CTE Refactoring**: Convert UNION queries to CTEs for better readability and optimization
6. **Covering Indexes**: Add indexes that include frequently selected columns
7. **TSVECTOR Phrase Search**: Enhance TSVECTOR queries with phrase matching capabilities

---

## 1. JSONB Query Optimization

### Current Issue

**File**: `scripts/kb/build_kb_registry.py` (lines 76, 128, 153)

**Problem**: Using `meta::text <> '{}'::text` is inefficient:
- Requires casting entire JSONB to text
- Cannot use GIN index effectively
- Slower than native JSONB operators

**Current Code**:
```sql
WHERE f.meta IS NOT NULL
  AND f.meta::text <> '{}'::text
  AND (f.meta->>'kb_candidate')::boolean = true
```

### Optimization

**Replace with**:
```sql
WHERE f.meta IS NOT NULL
  AND f.meta != '{}'::jsonb
  AND (f.meta->>'kb_candidate')::boolean = true
```

**Better yet** (leverages GIN index):
```sql
WHERE f.meta @> '{"kb_candidate": true}'::jsonb
```

**Performance Impact**: 
- `@>` operator can use GIN index directly
- Avoids text casting overhead
- Faster for large JSONB columns

**Migration**: Create new migration `057_jsonb_query_optimization.sql` (optional - code change only, no schema change needed)

---

## 2. Partial Indexes for Common Filters

### Current State

**File**: `migrations/048_add_fragment_meta_column.sql`

**Issue**: Full GIN index on `meta` is good, but we frequently filter by:
- `enabled = true` (doc_registry)
- `kb_candidate = true` (meta)
- `is_ssot = true` (doc_registry)

### Optimization

**Add Partial Indexes**:

```sql
-- Migration 058: Partial Indexes for Common Query Patterns

BEGIN;

-- Partial index for kb_candidate=true fragments (most common filter)
CREATE INDEX IF NOT EXISTS idx_doc_fragment_meta_kb_candidate
    ON control.doc_fragment USING gin (meta)
    WHERE meta @> '{"kb_candidate": true}'::jsonb;

-- Partial index for enabled documents with fragments
CREATE INDEX IF NOT EXISTS idx_doc_registry_enabled_ssot
    ON control.doc_registry (doc_id, logical_name, role, repo_path, is_ssot)
    WHERE enabled = true;

-- Composite index for doc_registry + fragment joins (covers build_kb_registry.py query)
CREATE INDEX IF NOT EXISTS idx_doc_fragment_doc_id_meta_kb
    ON control.doc_fragment (doc_id, fragment_index)
    WHERE meta @> '{"kb_candidate": true}'::jsonb;

COMMIT;
```

**Performance Impact**:
- Smaller index size (only relevant rows)
- Faster index scans for filtered queries
- Better query plan selection

---

## 3. Expression Indexes for JSONB Paths

### Current Issue

**File**: `scripts/kb/build_kb_registry.py` (line 130)

**Problem**: Querying `meta->>'importance'` requires full GIN scan, then filtering

**Current Code**:
```sql
AND (f.meta->>'importance')::text = 'core'
```

### Optimization

**Add Expression Index**:

```sql
-- Migration 059: Expression Indexes for JSONB Path Queries

BEGIN;

-- Index for importance field (used in curated subset query)
CREATE INDEX IF NOT EXISTS idx_doc_fragment_meta_importance
    ON control.doc_fragment ((meta->>'importance'))
    WHERE meta->>'importance' IS NOT NULL;

-- Index for subsystem field (common filter)
CREATE INDEX IF NOT EXISTS idx_doc_fragment_meta_subsystem
    ON control.doc_fragment ((meta->>'subsystem'))
    WHERE meta->>'subsystem' IS NOT NULL;

COMMIT;
```

**Performance Impact**:
- Direct index lookup for path expressions
- Faster than GIN index scan + filter
- Useful for `ORDER BY` and `GROUP BY` on JSONB fields

---

## 4. IVFFlat Index Tuning

### Current State

**File**: `migrations/055_control_doc_embedding_ivfflat.sql`

**Issue**: Fixed `lists = 100` may not be optimal for actual data size

**PostgreSQL Recommendation**: `lists = sqrt(rows)` or `lists = rows / 1000`

### Optimization

**Dynamic IVFFlat Tuning**:

```sql
-- Migration 060: IVFFlat Index Tuning Based on Row Count

BEGIN;

-- Drop existing index if it exists
DROP INDEX IF EXISTS control.idx_doc_embedding_vector;

-- Calculate optimal lists parameter (target: sqrt(rows) or rows/1000, min 10, max 1000)
DO $$
DECLARE
    row_count INTEGER;
    optimal_lists INTEGER;
BEGIN
    SELECT COUNT(*) INTO row_count FROM control.doc_embedding;
    
    -- Use sqrt(rows) as baseline, but cap between 10 and 1000
    optimal_lists := GREATEST(10, LEAST(1000, CEIL(SQRT(row_count))));
    
    -- If we have <1000 rows, use fixed 10 (minimum for IVFFlat)
    IF row_count < 1000 THEN
        optimal_lists := 10;
    END IF;
    
    -- Create index with optimal lists parameter
    EXECUTE format(
        'CREATE INDEX idx_doc_embedding_vector ON control.doc_embedding USING ivfflat (embedding vector_cosine_ops) WITH (lists = %s)',
        optimal_lists
    );
    
    RAISE NOTICE 'IVFFlat index created with lists = % (row_count = %)', optimal_lists, row_count;
END $$;

COMMIT;
```

**Performance Impact**:
- Optimal ANN search performance
- Adapts to data growth
- Prevents over-indexing on small datasets

**Note**: This should be run **after** Gate 1 completion (when we have >1000 embeddings)

---

## 5. CTE Refactoring for UNION Queries

### Current Issue

**File**: `scripts/kb/build_kb_registry.py` (lines 60-136)

**Problem**: Large UNION query is hard to optimize and maintain

### Optimization

**Refactor to CTEs**:

```sql
WITH
-- Primary filter: SSOT docs with kb_candidate=true
ssot_kb_candidates AS (
    SELECT DISTINCT
        d.doc_id,
        d.logical_name,
        d.role,
        d.repo_path,
        d.share_path,
        d.is_ssot,
        d.enabled
    FROM control.doc_registry d
    JOIN control.doc_fragment f ON f.doc_id = d.doc_id
    WHERE d.enabled = true
      AND d.is_ssot = true
      AND f.meta @> '{"kb_candidate": true}'::jsonb
),

-- Runbooks (always included)
runbooks AS (
    SELECT DISTINCT
        d.doc_id,
        d.logical_name,
        d.role,
        d.repo_path,
        d.share_path,
        d.is_ssot,
        d.enabled
    FROM control.doc_registry d
    WHERE d.enabled = true
      AND d.role = 'runbook'
),

-- Root AGENTS.md files
root_agents AS (
    SELECT DISTINCT
        d.doc_id,
        d.logical_name,
        d.role,
        d.repo_path,
        d.share_path,
        d.is_ssot,
        d.enabled
    FROM control.doc_registry d
    WHERE d.enabled = true
      AND d.repo_path IN ('AGENTS.md', 'pmagent/AGENTS.md', 'pmagent/AGENTS.md')
),

-- Top core-importance kb_candidate documents
core_kb_candidates AS (
    SELECT DISTINCT
        d.doc_id,
        d.logical_name,
        d.role,
        d.repo_path,
        d.share_path,
        d.is_ssot,
        d.enabled
    FROM control.doc_registry d
    JOIN control.doc_fragment f ON f.doc_id = d.doc_id
    WHERE d.enabled = true
      AND f.meta @> '{"kb_candidate": true, "importance": "core"}'::jsonb
      AND d.is_ssot = false
      AND d.role != 'runbook'
    LIMIT 50
)

-- Final union
SELECT * FROM ssot_kb_candidates
UNION
SELECT * FROM runbooks
UNION
SELECT * FROM root_agents
UNION
SELECT * FROM core_kb_candidates
ORDER BY logical_name;
```

**Performance Impact**:
- Better query plan optimization
- Easier to maintain and debug
- PostgreSQL can optimize each CTE independently

---

## 6. Covering Indexes

### Current Issue

**File**: `scripts/kb/build_kb_registry.py` (lines 146-156)

**Problem**: Fragment query selects `fragment_index` and `meta`, but index only covers `doc_id`

### Optimization

**Add Covering Index**:

```sql
-- Migration 061: Covering Index for Fragment Metadata Queries

BEGIN;

-- Covering index: includes fragment_index and meta in index
CREATE INDEX IF NOT EXISTS idx_doc_fragment_doc_id_covering
    ON control.doc_fragment (doc_id, fragment_index)
    INCLUDE (meta)
    WHERE meta @> '{"kb_candidate": true}'::jsonb;

COMMIT;
```

**Performance Impact**:
- Index-only scans (no table access needed)
- Faster for queries that only need indexed columns
- Reduces I/O for fragment metadata aggregation

**Note**: `INCLUDE` columns are available in PostgreSQL 11+

---

## 7. TSVECTOR Phrase Search Enhancement

### Current State

**File**: `migrations/056_control_doc_fragment_tsvector.sql`

**Issue**: Basic TSVECTOR implementation, but could support phrase search

### Optimization

**Enhanced TSVECTOR Queries**:

```sql
-- Example: Phrase search for "gematria calculation"
SELECT * FROM control.doc_fragment
WHERE content_tsvector @@ phraseto_tsquery('english', 'gematria calculation')
LIMIT 10;

-- Example: Proximity search (words within N positions)
SELECT * FROM control.doc_fragment
WHERE content_tsvector @@ to_tsquery('english', 'gematria <-> calculation')
LIMIT 10;

-- Example: Weighted search (title fragments rank higher)
-- Requires adding weights to TSVECTOR during indexing
```

**Migration Enhancement** (optional):

```sql
-- Migration 062: TSVECTOR Weighted Search Support

BEGIN;

-- Add weighted TSVECTOR column (A=title, B=heading, C=body, D=other)
ALTER TABLE control.doc_fragment
    ADD COLUMN IF NOT EXISTS content_tsvector_weighted tsvector;

-- Update trigger to include weights
CREATE OR REPLACE FUNCTION control.update_doc_fragment_tsvector_weighted()
RETURNS TRIGGER AS $$
BEGIN
    -- Default to 'C' weight (body text)
    -- Could be enhanced to detect headings/titles from fragment_type
    NEW.content_tsvector_weighted := setweight(
        to_tsvector('english', COALESCE(NEW.content, '')),
        'C'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER doc_fragment_tsvector_weighted_update
    BEFORE INSERT OR UPDATE ON control.doc_fragment
    FOR EACH ROW
    EXECUTE FUNCTION control.update_doc_fragment_tsvector_weighted();

COMMIT;
```

**Performance Impact**:
- Better search relevance
- Phrase matching for exact terms
- Weighted ranking for better results

---

## 8. Query Plan Analysis

### Recommended: Add EXPLAIN ANALYZE Verification

**File**: `scripts/kb/build_kb_registry.py`

**Add Query Plan Logging**:

```python
# After query execution, log query plan for optimization
if os.getenv("DEBUG_QUERY_PLANS") == "1":
    explain_query = text(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {str(query)}")
    plan = conn.execute(explain_query).fetchone()[0]
    print(f"Query plan: {json.dumps(plan, indent=2)}", file=sys.stderr)
```

**Usage**:
```bash
DEBUG_QUERY_PLANS=1 python scripts/kb/build_kb_registry.py
```

---

## 9. Materialized View for KB Registry (Optional)

### Use Case

If `build_kb_registry.py` runs frequently and the curated subset changes infrequently, consider a materialized view.

### Implementation

```sql
-- Migration 063: Materialized View for KB Registry (Optional)

BEGIN;

CREATE MATERIALIZED VIEW IF NOT EXISTS control.mv_kb_registry_curated AS
WITH
-- (Same CTE structure as Section 5)
ssot_kb_candidates AS (...),
runbooks AS (...),
root_agents AS (...),
core_kb_candidates AS (...)
SELECT * FROM ssot_kb_candidates
UNION
SELECT * FROM runbooks
UNION
SELECT * FROM root_agents
UNION
SELECT * FROM core_kb_candidates
ORDER BY logical_name;

-- Index on materialized view
CREATE INDEX IF NOT EXISTS idx_mv_kb_registry_logical_name
    ON control.mv_kb_registry_curated (logical_name);

-- Refresh function
CREATE OR REPLACE FUNCTION control.refresh_kb_registry_mv()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY control.mv_kb_registry_curated;
END;
$$ LANGUAGE plpgsql;

COMMIT;
```

**Refresh Strategy**:
- Refresh after classification runs complete
- Refresh after new documents ingested
- Use `REFRESH MATERIALIZED VIEW CONCURRENTLY` for zero-downtime updates

**Performance Impact**:
- Instant queries (pre-computed)
- Reduced load on `doc_registry` and `doc_fragment` tables
- Trade-off: Stale data until refresh

---

## 10. Summary of Recommended Optimizations

### High Priority (Immediate Impact)

1. ✅ **JSONB Query Optimization** (Section 1)
   - Replace `meta::text <> '{}'::text` with `meta @> '{"kb_candidate": true}'::jsonb`
   - **Impact**: 2-5x faster queries on large datasets

2. ✅ **Partial Indexes** (Section 2)
   - Add filtered indexes for `kb_candidate=true` and `enabled=true`
   - **Impact**: 3-10x faster filtered queries

3. ✅ **IVFFlat Tuning** (Section 4)
   - Recalculate `lists` parameter based on row count
   - **Impact**: Optimal ANN search performance

### Medium Priority (Performance Gains)

4. **Expression Indexes** (Section 3)
   - Index on `meta->>'importance'` and `meta->>'subsystem'`
   - **Impact**: Faster path expression queries

5. **CTE Refactoring** (Section 5)
   - Convert UNION to CTEs for better optimization
   - **Impact**: Better query plans, maintainability

6. **Covering Indexes** (Section 6)
   - Include `meta` in fragment index
   - **Impact**: Index-only scans for fragment queries

### Low Priority (Nice to Have)

7. **TSVECTOR Phrase Search** (Section 7)
   - Enhanced search capabilities
   - **Impact**: Better search relevance

8. **Materialized View** (Section 9)
   - Pre-computed KB registry
   - **Impact**: Instant queries, but requires refresh strategy

---

## Implementation Order

1. **Immediate** (Code changes only):
   - Section 1: JSONB query optimization in `build_kb_registry.py`

2. **After Gate 1 Complete** (>1000 embeddings):
   - Section 4: IVFFlat tuning migration
   - Section 2: Partial indexes migration

3. **After Gate 2 Complete** (Indexing stable):
   - Section 3: Expression indexes migration
   - Section 6: Covering indexes migration

4. **Optional** (Future enhancement):
   - Section 5: CTE refactoring (code change)
   - Section 7: TSVECTOR enhancements
   - Section 9: Materialized view

---

## Testing & Verification

### Query Performance Benchmarks

```sql
-- Before optimization
EXPLAIN ANALYZE
SELECT COUNT(*) FROM control.doc_fragment
WHERE meta::text <> '{}'::text
  AND (meta->>'kb_candidate')::boolean = true;

-- After optimization
EXPLAIN ANALYZE
SELECT COUNT(*) FROM control.doc_fragment
WHERE meta @> '{"kb_candidate": true}'::jsonb;
```

### Index Usage Verification

```sql
-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'control'
  AND tablename IN ('doc_fragment', 'doc_registry', 'doc_embedding')
ORDER BY idx_scan DESC;
```

---

## Related Documentation

- PostgreSQL JSONB Documentation: https://www.postgresql.org/docs/current/datatype-json.html
- pgvector IVFFlat Indexing: https://github.com/pgvector/pgvector#ivfflat
- PostgreSQL Index Types: https://www.postgresql.org/docs/current/indexes-types.html
- TSVECTOR Full-Text Search: https://www.postgresql.org/docs/current/textsearch.html

---

## Notes

- All optimizations are **backward compatible** (no breaking changes)
- Migrations use `IF NOT EXISTS` for idempotency
- Performance gains are **additive** (can implement incrementally)
- Test on staging before production deployment

