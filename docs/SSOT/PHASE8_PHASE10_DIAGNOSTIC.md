# Phase 8 & 10 Diagnostic — Data Generation Gap Analysis

**Date**: 2025-12-02  
**Status**: 🟡 **DIAGNOSTIC COMPLETE** — Root cause identified, fix required before mapping  
**Mandate**: Per Rule-070 Gotchas Check and PM approval, diagnose why Phase 8/10 exports are empty

---

## Executive Summary

**Finding**: Phase 8 and Phase 10 scripts **exist and contain correct logic**, but:
1. **Phase 8 (temporal)**: Script expects `exports/graph_latest.json` but processes empty node lists
2. **Phase 10 (correlation)**: Script expects `concept_network` table with embeddings but finds insufficient data
3. **Root Cause**: Scripts are **not being run** as part of standard pipeline, OR they're running against insufficient data

**Conclusion**: This is a **workflow/orchestration gap**, not broken code.

---

## 1. Current State (Empty Outputs)

### Phase 8: Temporal Patterns
- **File**: `exports/temporal_patterns.json`
- **Schema**: ✅ Correct (`temporal_patterns: []`, valid metadata)
- **Data**: ❌ **Zero series** (`total_series: 0`)
- **Date**: `2025-11-08T21:13:10` (last generated 24 days ago)

### Phase 10: Correlations
- **File**:  `exports/graph_correlations.json`
- **Schema**: ✅ Correct (`correlations: []`, valid metadata)
- **Data**: ❌ **Zero correlations** (`total_correlations: 0`)
- **Date**: `2025-11-08T21:13:10` (last generated 24 days ago)

**Observation**: Both files were generated at the same timestamp on Nov 8, suggesting they were part of a single export run that found no data to analyze.

---

## 2. Script Analysis

### Phase 8: `scripts/temporal_analytics.py`

**Purpose**: Rolling window temporal analytics over sequential biblical text (ADR-025)

**Logic Flow**:
1. Load `exports/graph_latest.json` (line 264)
2. Extract nodes with `position`, `verse`, `chapter` fields (lines 52-69)
3. Compute rolling statistics over position indices (lines 75-92)
4. Generate temporal patterns array with series metadata (lines 110-155)
5. Write to `exports/temporal_patterns.json` (line 291)

**Input Requirements**:
- ✅ `exports/graph_latest.json` must exist
- ✅ Nodes must have `position` OR (`chapter`, `verse`) fields
- ❌ **CRITICAL**: Nodes need enriched metadata that includes positional information

**Why It Produced Empty Output**:
```python
# Line 272-274
print(f"[Phase-8] Loaded graph with {len(graph_data.get('nodes', []))} nodes")
```
**Hypothesis**: The script ran but found **nodes without position/chapter/verse** metadata, OR the rolling window logic filtered everything out due to missing `gematria` values.

**Verification Needed**:
- Check if `exports/graph_latest.json` nodes contain `position`/`chapter`/`verse` fields
- Check if `gematria` values are present on nodes (line 65: `node.get("gematria", 0)`)

### Phase 10: `scripts/export_stats.py::export_correlations()`

**Purpose**: Pattern correlation analysis using concept embeddings (ADR-018)

**Logic Flow**:
1. **First**: Query `concept_correlations` DB view (lines 351-381)
   - View definition: `migrations/017_concept_correlations.sql` or `migrations/038_concept_correlations.sql`
   - Requires `concept_network` table with `embedding` field populated
   - Computes Pearson correlation between embedding vectors
2. **Fallback**: Python scipy.stats.pearsonr (lines 410-502)
   - Requires `concept_network.embedding IS NOT NULL`
   - Computes pairwise correlations (batched to 100 pairs for performance)

**Input Requirements**:
- ✅ `concept_network` table must exist
- ✅ `concept_network.embedding` must be populated (1024-D vectors)
- ✅ At least 2 concepts with embeddings
- ❌ **CRITICAL**: Database view/query returned zero rows

**Why It Produced Zero Correlations**:
```python
# Line 434-436
if len(concept_data) < 2:
    LOG.warning("Insufficient concept data for correlation analysis")
    return []
```
**Hypothesis**: Either:
- A) `concept_network` table is empty or has <2 rows
- B) `embedding` field is NULL for all/most concepts
- C) DB view `concept_correlations` doesn't exist or is broken

**Verification Needed**:
```sql
SELECT COUNT(*) FROM concept_network WHERE embedding IS NOT NULL;
SELECT COUNT(*) FROM concept_correlations LIMIT 1;
```

---

## 3. Root Cause Analysis

### **CONFIRMED ROOT CAUSE: ai_nouns.json Has Only 1 Node**

**Discovery**: 
- `exports/ai_nouns.json` contains only **1 node** (the test node "seed-ps30-isa43" with gematria 222)
- `scripts/export_graph.py` lines 262-273 **prioritize** `ai_nouns.json` over database
- Edges are fetched separately from `concept_relations` DB table → 14,330 edges
- Result: **Orphan edges** - edges reference UUIDs not in the nodes array

**Evidence**:
```bash
# ai_nouns.json has 1 node
jq ".nodes | length" exports/ai_nouns.json  # Returns: 1

# That node has ID "seed-ps30-isa43" (not a UUID)
jq ".nodes[0].noun_id" exports/ai_nouns.json  # Returns: "seed-ps30-isa43"

# But edges reference different UUIDs
jq ".edges[0].source" exports/graph_latest.json  # Returns: "875bbf17-7b2e-4626-813a-ec51cd644b3f"
```

**Why This Breaks Phase 8/10**:
1. Phase 8 temporal analysis needs ≥10 nodes with position/gematria fields → only gets 1
2. Phase 10 correlation needs ≥2 concepts with embeddings → only gets 1
3. Both produce empty outputs correctly (not a script bug, a data availability issue)

**Solution**:
- **Option A** (Quick Fix): Delete or rename `exports/ai_nouns.json` to force DB fallback
- **Option B** (Proper Fix): Regenerate `ai_nouns.json` with full node set from pipeline
- **Option C** (Investigation): Determine why `ai_nouns.json` only has 1 node (development artifact?)

---

### Hypothesis A: **Missing Pipeline Integration** (SUPERSEDED)
- **Evidence**: No Makefile targets found for `run_phase8_analysis` or `export_correlations`
- **Impact**: Scripts exist but are never called in normal workflow
- **Fix**: Add to `make eval.*` or `make export.*` targets

### Hypothesis B: **Insufficient Input Data**
- **Evidence**: Last successful run was Nov 8 (24 days ago, likely before recent data changes)
- **Impact**: `graph_latest.json` may have nodes but lack required fields (position, gematria, embeddings)
- **Fix**: Ensure `export_graph.py` includes all metadata fields needed by Phase 8/10

### Hypothesis C: **Database Schema Mismatch**
- **Evidence**: Phase 10 fallback uses `concept_network` table which may not match current schema
- **Impact**: Queries fail silently, produce empty results
- **Fix**: Verify schema migrations are applied, check table existence

### Hypothesis D: **Thresholds Too Strict**
- **Evidence**: Phase 10 limits to 1000 correlations, batches to 100 pairs (line 358, 440)
- **Impact**: If data set is small, may filter out everything
- **Likelihood**: LOW (empty != filtered)

---

## 4. Git History Review

**Relevant Commits**:
- `1fe876c8`: "feat(api): add temporal endpoints for patterns/forecasts" (Phase 8 API integration)
- `78b20797`: "feat(temporal): integrate DB series extraction + pipeline wiring" (Phase 8 DB integration)

**Observation**: Commits show Phase 8 was actively developed but don't show evidence of integration with main export pipeline.

**Missing Evidence**:
- No commits showing `make export.*` or standard pipeline calling these scripts
- No commits showing successful non-empty `temporal_patterns.json` or `graph_correlations.json`

---

## 5. Minimal Fix Recommendations

### Fix 1: **Verify Data Prerequisites** (Immediate)
```bash
# Check if graph export has required fields
jq '.nodes[0] | keys' exports/graph_latest.json

# Check if embeddings exist in DB
psql "$GEMATRIA_DSN" -c "SELECT COUNT(*) FROM concept_network WHERE embedding IS NOT NULL;"

# Check if correlation view exists
psql "$GEMATRIA_DSN" -c "SELECT COUNT(*) FROM concept_correlations LIMIT 1;"
```

### Fix 2: **Manual Script Execution** (Validation)
```bash
# Run Phase 8 manually
python scripts/temporal_analytics.py --book Genesis

# Run Phase 10 manually (via export_stats)
python -c "
from scripts.export_stats import export_correlations
from src.infra.db import get_gematria_rw
import json
db = get_gematria_rw()
result = export_correlations(db)
print(json.dumps(result, indent=2))
" > exports/graph_correlations.json
```

### Fix 3: **Pipeline Integration** (Long-term)
Add to `Makefile` or `scripts/export_all.sh`:
```makefile
eval.analytics: eval.temporal eval.correlation

eval.temporal:
	python scripts/temporal_analytics.py --book $(BOOK)

eval.correlation:
	python scripts/export_stats.py --mode=correlations
```

### Fix 4: **Export Graph Enrichment** (If metadata missing)
Ensure `scripts/export_graph.py` includes:
- Node `position` field (calculated from chapter/verse)
- Node `chapter` and `verse` fields from Bible DB
- Node `gematria` field from calculations

---

## 6. Acceptance Criteria for "Fixed"

Before proceeding to Phase B (Mapping Docs):

1. ✅ **Phase 8 produces non-empty output**:
   - `exports/temporal_patterns.json` has `total_series > 0`
   - At least one series with `values` array length > 0

2. ✅ **Phase 10 produces non-empty output**:
   - `exports/graph_correlations.json` has `total_correlations > 0`
   - At least one correlation record with valid `source`, `target`, `correlation` fields

3. ✅ **Data Shape Confirmation**:
   - Temporal patterns match `scripts/compass/scorer.py` expectations (lines 122-149):
     - Fields: `series`, `timestamps`, `values`
   - Correlation records ready for per-edge `correlation_weight`:
     - Fields: `source`, `target`, `correlation`, `p_value`

4. ✅ **Repeatable Workflow**:
   - Clear Makefile target or script that regenerates both exports deterministically
   - Integration into standard pipeline (e.g., `make eval.analytics` or similar)

---

## 7. Next Steps

### Immediate (PM Approval Required)
1. Run Fix 1 (verification commands) to confirm hypotheses
2. Report findings back to PM with specific data gaps identified
3. Decide on quick fix vs comprehensive pipeline integration

### After Data Validation
1. Execute Fix 2 (manual run) to generate real Phase 8/10 data
2. Inspect actual output shapes to confirm COMPASS compatibility
3. Proceed to **Phase B: Create Mapping Docs** with real examples

### Long-term Integration
1. Implement Fix 3 (Makefile targets)
2. Implement Fix 4 (export graph enrichment) if needed
3. Wire into `make reality.green` or standard export verification

---

## 8. PM Guidance Incorporated

**Decision**: Treat empty outputs as **defect, not acceptable state**  
- No synthetic defaults (e.g., `correlation_weight = 0.5`)
- No marking COMPASS components as "N/A"
- Must fix data generation before wiring

**Temporal Granularity**: Envelope-level structure (per scorer.py)  
- `temporal_patterns` is an array of series objects, not per-edge fields
- Each series has: `series`, `timestamps`, `values`, `metadata`

**Correlation Granularity**: Per-edge scalar  
- Each edge needs `correlation_weight` field (0.0 to 1.0)
- Derived from Phase 10 correlation analysis between concept pairs

---

## Appendix: Key Files Reference

### Phase 8
- **Script**: `scripts/temporal_analytics.py` (355 lines)
- **ADR**: `docs/ADRs/ADR-025-multi-temporal-analytics.md`
- **Schema**: `docs/SSOT/temporal-patterns.schema.json`
- **Output**: `exports/temporal_patterns.json`

### Phase 10
- **Script**: `scripts/export_stats.py::export_correlations()` (lines 337-407)
- **Fallback**: `scripts/export_stats.py::_compute_correlations_python()` (lines 410-502)
- **ADR**: `docs/ADRs/ADR-018-pattern-correlation.md`
- **Schema**: `docs/SSOT/graph-correlations.schema.json`
- **Migration**: `migrations/017_concept_correlations.sql` or `migrations/038_concept_correlations.sql`
- **Output**: `exports/graph_correlations.json`

### COMPASS
- **Scorer**: `scripts/compass/scorer.py` (225 lines)
- **Temporal Validation**: Lines 109-149 (expects `temporal_patterns` array with specific fields)
- **Correlation Validation**: Lines 28-65 (expects `correlation_weight` per edge)
- **DOC**: `docs/SSOT/PHASE15_COMPASS_STRUCTURAL_GAP.md`
