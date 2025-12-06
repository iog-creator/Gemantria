# Phase 15 — COMPASS Structural Gap (40% → 100%)

**Date**: 2025-12-02  
**Status**: ⚠️ **BLOCKED ON STRUCTURAL COMPLETION** (not RAG accuracy)  
**Goal**: Wire Phase 8 and Phase 10 outputs into envelope to achieve 100% structural COMPASS score

---

## 1. Current Baseline

**COMPASS Score**: 40% (threshold: 80%) — **FAIL**

**Rule 045 Validation**: ✅ **PASSED**
- All 14,330 edges have `cosine`, `rerank_score`, `edge_strength`
- Blend validator: 0 mismatches, 0 missing fields
- Blend formula: `edge_strength = 0.5 * cosine + 0.5 * rerank_score` (verified)

**Graph Export + Envelope**:
- 14,330 edges in `exports/graph_latest.json`
- 14,330 edges in `ui/out/unified_envelope_10000.json`
- All Rule 045 fields present and validated

---

## 2. Gap Analysis

**COMPASS Score Breakdown**:

| Component | Score | Weight | Status | Issue |
|-----------|-------|--------|--------|-------|
| `edge_strength_blend` | **100%** | 40% | ✅ PASSED | Rule 045 validated |
| `correlation_weights` | **0%** | 40% | ❌ FAILED | `correlation_weight` field missing on edges |
| `temporal_patterns` | **0%** | 20% | ❌ FAILED | Temporal pattern data missing in envelope |

**Conclusion**:

> The 40% COMPASS score reflects **structural incompleteness**, not RAG or Rule 045 math errors. RAG scoring and Rule 045 blend are 100% correct. The gap is purely due to missing Phase 8 (temporal) and Phase 10 (correlation) outputs in the envelope.

---

## 3. Mandatory Structural Actions (Pre-Phase-16)

**Before Phase 15 Wave-3 can be marked complete**, the following structural wiring must be done:

### 3.1 Wire Phase 10 Correlation Analytics

**Action**: Add `correlation_weight` field to each edge in the graph export and envelope.

**Source**: Phase 10 correlation analytics output (likely `exports/correlation_weights.json` or DB table).

**Implementation**:
- Extend `scripts/export_graph.py` or `scripts/extract_all.py` to:
  - Read Phase 10 correlation data
  - Map correlation records to edges (by `source_id`/`target_id` or canonical edge key)
  - Attach `correlation_weight` field to each edge
- Ensure COMPASS scorer sees this field on all relevant edges

**Acceptance**: `correlation_weights` component scores 100% (40% of total COMPASS).

### 3.2 Wire Phase 8 Temporal Analytics

**Action**: Add `temporal_patterns` data to the envelope in the shape expected by `scripts/compass/scorer.py`.

**Source**: Phase 8 temporal analytics output (likely `exports/temporal_patterns.json` or DB table).

**Implementation**:
- If temporal data is edge-aligned: Add `temporal_patterns` field per edge or per edge-group
- If temporal data is global: Include top-level `temporal_patterns` section in envelope
- Ensure envelope shape matches COMPASS scorer expectations

**Acceptance**: `temporal_patterns` component scores 100% (20% of total COMPASS).

### 3.3 Re-run Validation

After structural wiring:

1. Re-run `scripts/extract_all.py` to refresh the envelope with new fields
2. Re-run `scripts/compass/scorer.py` (or `make test.compass`) to confirm:
   - `correlation_weights`: 100% (40% weight)
   - `temporal_patterns`: 100% (20% weight)
   - `edge_strength_blend`: 100% (40% weight)
   - **Total COMPASS score: 100% structurally**

---

## 4. DSPy and Phase-16

**DSPy is not required to close this structural gap.**

**Phase 15's COMPASS gate must be met first via structural completion** (wiring Phase 8 and Phase 10 outputs into the envelope).

**DSPy and advanced tuning** (alpha calibration, ensembles, LLM-as-judge, fine-tune prep) are reserved for **Phase 16+** once structural COMPASS is at or near 100%.

**Non-DSPy optimization techniques** (hybrid retrieval, tool offloading, strict JSON signatures, metric calibration) are valid Phase-16 candidates but should not block Phase 15 completion.

---

## 5. Related Documents

- `docs/SSOT/PHASE15_WAVE3_STEP2_COMPASS_RESULTS.md` — Detailed COMPASS baseline results
- `docs/SSOT/PHASE15_WAVE3_GATE_DECISION.md` — Phase 15 completion criteria
- `docs/SSOT/PHASE15_WAVE3_STEP2_OPS_BLOCK.md` — Step 2 operational plan
- `.cursor/rules/045-rerank-blend-SSOT.mdc` — Rule 045 governance

---

## 6. Next Steps

1. **Design Phase 10 → Envelope Mapping**: Identify correlation data source and define edge mapping strategy
2. **Design Phase 8 → Envelope Mapping**: Identify temporal data source and define envelope shape
3. **Implement Structural Wiring**: Update `export_graph.py` / `extract_all.py` to include Phase 8/10 data
4. **Re-run COMPASS**: Verify 100% structural score
5. **Mark Phase 15 Wave-3 Complete**: Once COMPASS ≥ 80% (or 100% structurally), proceed to Phase 16 planning

