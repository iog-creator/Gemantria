# Phase 15 COMPASS Alignment Analysis

## Purpose

This document compares existing COMPASS/blend validation infrastructure with Phase 15 Wave-3 work to identify what's actually new vs. what already exists.

## Executive Summary

**What Already Exists:**
- COMPASS scorer (`scripts/compass/scorer.py`) - validates Rule 045 blend, correlation weights, temporal patterns
- Blend SSOT validator (`scripts/eval/validate_blend_ssot.py`) - validates Rule 045 blend in graph exports
- Blend calculation (`src/rerank/blender.py`) - SSOT function for `edge_strength = 0.5*cosine + 0.5*rerank`
- Graph export (`scripts/export_graph.py`) - already emits `cosine`, `rerank_score`, `edge_strength` with Rule 045 blend
- Pipeline integration - COMPASS already integrated into `pipeline_orchestrator.py` and `schema_validator.py`

**What's New in Phase 15 Wave-3:**
- **RAG spine alignment** - Wiring RAG retrieval (`pmagent/biblescholar/rag_retrieval.py`, `reranker_adapter.py`) to use Rule 045 field names (`cosine`, `rerank_score`, `edge_strength`) instead of legacy names (`embedding_score`, `combined_score`)
- **Extract script gap** - `scripts/extract_all.py` is currently a MOCK/PLACEHOLDER that doesn't read from `graph_latest.json`; it generates dummy data without Rule 045 fields

## Detailed Comparison

### 1. COMPASS Scorer (`scripts/compass/scorer.py`)

**Status:** ✅ **Already Exists and Works**

**What it does:**
- `validate_edge_strength_blend()` - Validates `edge_strength = 0.5*cosine + 0.5*rerank_score` (Rule 045)
- `validate_correlation_weights()` - Validates correlation weights >0.5 threshold
- `validate_temporal_patterns()` - Validates temporal data integrity
- Overall score: weighted average (40% correlation, 40% blend, 20% temporal)
- Threshold: >80% correctness required

**Integration:**
- Already integrated into `scripts/pipeline_orchestrator.py` (envelope-first hardening)
- Already integrated into `src/nodes/schema_validator.py` (pipeline validation)
- Makefile target: `make test.compass`

**Field expectations:**
- Expects `cosine`, `rerank_score`, `edge_strength` fields in envelope edges
- Tolerance: `BLEND_TOL = 0.005` (from Rule 045)

### 2. Blend SSOT Validator (`scripts/eval/validate_blend_ssot.py`)

**Status:** ✅ **Already Exists and Works**

**What it does:**
- Validates Rule 045 blend in `exports/graph_latest.json`
- Formula: `edge_strength = α*cosine + (1-α)*rerank_score` where `α=EDGE_ALPHA=0.5`
- Tolerance: `BLEND_TOL=0.005`
- Handles legacy field aliases:
  - `similarity` → `cosine`
  - `rerank` → `rerank_score`
  - `strength` → `edge_strength`

**Output:**
- `share/eval/edges/blend_ssot_report.json` - JSON report
- `share/eval/edges/blend_ssot_report.md` - Markdown summary

**Current behavior:**
- Non-fatal (emits HINTs) when graph export missing or fields missing
- Checks actual edges in `graph_latest.json` (not envelope)

### 3. Blend Calculation (`src/rerank/blender.py`)

**Status:** ✅ **Already Exists and Works**

**What it does:**
- `blend_strength(cosine, rerank)` - SSOT function for Rule 045
- Formula: `(1 - BLEND_W) * cosine + BLEND_W * rerank` where `BLEND_W=0.5`
- Used by:
  - `scripts/export_graph.py` - graph export
  - `src/nodes/graph_scorer.py` - pipeline scoring
  - `pmagent/tools/rerank.py` - rerank tool

**Configuration:**
- `EDGE_RERANK_BLEND_W` env var (default: 0.5)
- Matches Rule 045: `edge_strength = 0.5*cosine + 0.5*rerank`

### 4. Graph Export (`scripts/export_graph.py`)

**Status:** ✅ **Already Exists and Uses Rule 045**

**What it does:**
- Exports `exports/graph_latest.json` with nodes and edges
- **Already emits Rule 045 fields:**
  ```python
  "cosine": float(r[2] or 0),
  "rerank_score": float(r[3] or 0) if r[3] else None,
  "edge_strength": blend_strength(float(r[2] or 0), float(r[3] or 0)) if r[3] else float(r[2] or 0),
  ```
- Uses `blend_strength()` from `src.rerank.blender`
- Reads from `concept_relations` table (DB)

**Current state:**
- Graph export has 0 edges (stale/empty DB)
- But the code is correct and aligned with Rule 045

### 5. RAG Retrieval (`pmagent/biblescholar/rag_retrieval.py`, `reranker_adapter.py`)

**Status:** ⚠️ **Updated in Phase 15 Wave-3 Step-2**

**What changed:**
- **Before:** Used legacy field names (`embedding_score`, `combined_score`)
- **After:** Uses Rule 045 field names (`cosine`, `rerank_score`, `edge_strength`)

**Implementation:**
- `rag_retrieval.py` - Updated to use `cosine` instead of `embedding_score`
- `reranker_adapter.py` - Updated to compute `edge_strength = 0.5*cosine + 0.5*rerank_score` (Rule 045)
- Tests updated (`test_rag_retrieval.py`, `test_reranker_adapter.py`, `test_rag_live.py`)

**Why this matters:**
- RAG retrieval now produces chunks with Rule 045 fields
- These chunks can flow into graph export and COMPASS validation
- Aligns RAG spine with existing COMPASS/blend infrastructure

### 6. Extract Script (`scripts/extract_all.py`)

**Status:** 🔴 **MOCK/PLACEHOLDER - Not Reading Real Data**

**Current implementation:**
- Generates dummy data (mock nodes/edges)
- Does NOT read from `graph_latest.json`
- Edges use legacy `strength` field (not Rule 045 fields)

**What needs to happen:**
- Update `extract_all.py` to read from `exports/graph_latest.json`
- Extract edges with Rule 045 fields (`cosine`, `rerank_score`, `edge_strength`)
- Build unified envelope that COMPASS can validate

**Impact:**
- Current envelopes fail COMPASS because they don't have Rule 045 fields
- This is why COMPASS scored 0.0% - envelope is mock data, not real graph export

## Key Differences Summary

| Component | Status | Rule 045 Alignment | Notes |
|-----------|--------|-------------------|-------|
| COMPASS scorer | ✅ Exists | ✅ Validates Rule 045 | Already integrated into pipeline |
| Blend validator | ✅ Exists | ✅ Validates Rule 045 | Checks `graph_latest.json` |
| Blend calculation | ✅ Exists | ✅ Implements Rule 045 | SSOT function in `blender.py` |
| Graph export | ✅ Exists | ✅ Emits Rule 045 fields | Code correct, but DB empty |
| RAG retrieval | ⚠️ Updated | ✅ Now uses Rule 045 | Phase 15 Wave-3 Step-2 |
| Extract script | 🔴 Mock | ❌ Not aligned | Needs to read real graph export |

## What Phase 15 Wave-3 Actually Did

**Step-2 (Rule 045 Blend Wiring):**
- ✅ Updated RAG retrieval to use Rule 045 field names (`cosine`, `rerank_score`, `edge_strength`)
- ✅ Updated tests to match new field names
- ✅ Aligned RAG spine with existing COMPASS/blend infrastructure

**Step-3 (Validation):**
- ⚠️ Discovered `extract_all.py` is a mock/placeholder
- ⚠️ Discovered graph export has 0 edges (stale DB)
- ⚠️ Discovered RAG tests use wrong verse_ids (1-10 vs ~101850+)

## What Needs to Happen Next

1. **Fix extract script** - Update `scripts/extract_all.py` to read from `exports/graph_latest.json` and extract Rule 045 fields
2. **Rebuild graph** - Run pipeline to populate `graph_latest.json` with actual edges
3. **Fix test data** - Update RAG tests to use actual verse_ids (~101850+) that have embeddings
4. **Re-run validation** - Run COMPASS on envelope built from real graph export

## Conclusion

**We are NOT redoing COMPASS work.** COMPASS and blend validation already exist and work correctly.

**What we ARE doing:**
- Aligning RAG retrieval (new component) with existing COMPASS/blend infrastructure
- Fixing the extract script gap (mock → real data)
- Ensuring end-to-end flow: RAG → Graph Export → Extract → COMPASS

The confusion came from:
1. Mock extract script producing envelopes without Rule 045 fields
2. Empty graph export (0 edges) making validation appear broken
3. Test data misalignment (wrong verse_ids)

All existing COMPASS/blend infrastructure is correct and aligned with Rule 045. The work is about connecting the new RAG components to that existing infrastructure.

