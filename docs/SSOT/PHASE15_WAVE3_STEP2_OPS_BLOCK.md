# Phase 15 Wave-3 Step 2: Full RAG Scoring — OPS Block

**Date**: 2025-12-02  
**Status**: ⚠️ **BLOCKED ON TEST DATA ALIGNMENT** (not infrastructure)  
**Goal**: Certify Phase 15 RAG is ready for COMPASS scoring by aligning all test data and confirming Rule 045 compliance

---

## Executive Summary

**All infrastructure is complete.** Gates 1-3 are certified, and Step 2 code-level implementation is complete. The remaining blocker is **test data alignment** to ensure RAG tests use fresh verse_ids with 1024-D embeddings and that the full pipeline exports Rule 045 fields for COMPASS validation.

**Success Criteria:**
- ✅ All RAG tests use real verse_ids (≥42,358) with 1024-D embeddings
- ✅ Rule 045 blend ratio confirmed (0.5/0.5) and validated
- ✅ Graph export includes Rule 045 fields (`cosine`, `rerank_score`, `edge_strength`)
- ✅ COMPASS scorer can validate envelope with >80% score

---

## I. Current State Assessment

### Infrastructure Status: ✅ COMPLETE

| Component | Status | Evidence | Source(s) |
|-----------|--------|----------|-----------|
| **Gate 1 (DMS Ingestion)** | ✅ COMPLETE | 65,243 fragments, 65,238 embeddings (1024-D) | `share/pm_snapshot.md`, `docs/SSOT/KB_REGISTRY_ARCHITECTURAL_COURSE_CORRECTION.md` |
| **Gate 2 (RAG Performance)** | ✅ COMPLETE | IVFFlat index (055), TSVECTOR/GIN index (056) | `migrations/055_*.sql`, `migrations/056_*.sql`, `docs/SSOT/DMS_PERFORMANCE_OPTIMIZATION.md` |
| **Gate 3 (KB Curation)** | ✅ COMPLETE | 40KB registry, 50 documents | `share/kb_registry.json`, `docs/SSOT/KB_REGISTRY_ARCHITECTURAL_COURSE_CORRECTION.md` |
| **Step 1 (LM Wiring)** | ✅ COMPLETE | Live RAG tests pass (with correct verse_ids) | `pmagent/biblescholar/tests/test_rag_live.py`, `docs/SSOT/PHASE15_WAVE3_PLAN.md` |
| **Step 2 (Code-Level)** | ✅ COMPLETE | Rule 045 blend implemented in code | `pmagent/biblescholar/reranker_adapter.py`, `.cursor/rules/045-rerank-blend-SSOT.mdc` |

### Remaining Blockers: ⚠️ TEST DATA ALIGNMENT

| Blocker | Status | Required Action | Source(s) |
|---------|--------|----------------|-----------|
| **Test Data Stale** | ⚠️ BLOCKER | Update RAG tests to use fresh verse_ids (≥42,358) with 1024-D embeddings | `docs/SSOT/PHASE15_WAVE3_PLAN.md` §10.2 |
| **Rule 045 Blend Certification** | ⚠️ ALIGNMENT NEEDED | Confirm authoritative alpha ratio (0.5/0.5) and validate all code paths | `.cursor/rules/045-rerank-blend-SSOT.mdc`, `scripts/eval/validate_blend_ssot.py` |
| **COMPASS Integration** | ⚠️ BLOCKER | Ensure graph export includes Rule 045 fields for COMPASS validation | `docs/SSOT/MASTER_PLAN.md` (COMPASS threshold), `scripts/compass/scorer.py` |

---

## II. Phase 15 Wave-3: Alignment & Baseline Gate

**Phase 15 Wave-3 cannot be called "COMPASS-ready" until all three gates are complete:**

### Gate 1: RAG Tests Aligned to Real Data

**Requirements:**
* All RAG live tests use `verse_id` values that exist in the current `bible.verse_embeddings` 1024-D domain (ID range ~101,850+).
* No tests reference dummy IDs 1–10.
* All tests verify 1024-D embedding dimensionality.

**Verification:**
```bash
pytest pmagent/biblescholar/tests/test_rag_live.py -m live -v
# Expected: All tests pass with real verse_ids
```

**Files to Update:**
- `pmagent/biblescholar/tests/test_rag_retrieval.py` - Uses hardcoded verse_ids (12345, 12346, etc.) - **OK for mocks**
- `pmagent/biblescholar/tests/test_reranker_adapter.py` - Uses mock verse_ids - **OK for mocks**
- `pmagent/biblescholar/tests/test_embedding_adapter.py` - Uses verse_id=1 - **OK for mocks** (tests are mocked)

**Note:** Mock tests are acceptable; only live tests (`@pytest.mark.live`) must use real verse_ids.

**Source(s):**
- `docs/SSOT/PHASE15_WAVE3_PLAN.md` §10.2 - Test data alignment requirements
- `pmagent/biblescholar/tests/test_rag_live.py` - Example of dynamic verse_id lookup

### Gate 2: Graph Export Rebuilt with Real Rule-045 Fields

**Requirements:**
* `exports/graph_latest.scored.json` contains non-zero edges.
* Every edge has `cosine`, `rerank_score`, and `edge_strength = 0.5 * cosine + 0.5 * rerank_score`.

**Verification:**
```bash
# 1. Check graph has edges with Rule 045 fields
python -c "import json; g=json.load(open('exports/graph_latest.json')); e=g.get('edges',[]); print(f'Edges: {len(e)}'); print(f'Has cosine: {sum(1 for x in e if \"cosine\" in x)}'); print(f'Has rerank_score: {sum(1 for x in e if \"rerank_score\" in x)}'); print(f'Has edge_strength: {sum(1 for x in e if \"edge_strength\" in x)}')"

# 2. Run blend validator
python scripts/eval/validate_blend_ssot.py

# 3. Check validator output
cat share/eval/edges/blend_ssot_report.json | jq '.blend_mismatch, .missing_fields'
# Expected: 0 mismatches, 0 missing fields
```

**Source(s):**
- `.cursor/rules/045-rerank-blend-SSOT.mdc` - Rule 045 field requirements
- `scripts/eval/validate_blend_ssot.py` - Blend validator
- `scripts/export_graph.py` - Graph export implementation

### Gate 3: COMPASS Baseline Run Completed

**Requirements:**
* `scripts/extract_all.py` runs on real data (no mocks).
  - It reads `exports/graph_latest.scored.json`.
  - The COMPASS scorer runs and produces a non-zero score.
  - The resulting COMPASS score is recorded in the Phase-15 log / PM share.
* COMPASS score >= 80% (Phase completion threshold).

**Verification:**
```bash
# 1. Re-run extract script
python scripts/extract_all.py --size 10000 --outdir ui/out

# 2. Verify envelope has Rule 045 fields
python -c "import json; e=json.load(open('ui/out/unified_envelope_10000.json')); edges=e.get('edges',[]); print(f'Edges: {len(edges)}'); print(f'Has cosine: {sum(1 for x in edges if \"cosine\" in x)}'); print(f'Has rerank_score: {sum(1 for x in edges if \"rerank_score\" in x)}'); print(f'Has edge_strength: {sum(1 for x in edges if \"edge_strength\" in x)}')"

# 3. Run COMPASS scorer
make test.compass  # or python scripts/compass/scorer.py ui/out/unified_envelope_10000.json --verbose
# Expected: >80% correctness score
```

**Source(s):**
- `docs/SSOT/MASTER_PLAN.md` - COMPASS threshold requirements (>80%)
- `scripts/compass/scorer.py` - COMPASS scorer implementation
- `scripts/extract_all.py` - Envelope extraction (already reads Rule 045 fields)

---

## III. Gematria Governance: Ketiv-Primary Verification

**Policy Mandate:** Gematria calculations used in pipelines must use Ketiv-primary numerics per ADR-002.

**Historical Context:** A Qere-first policy was considered but explicitly rejected in Phase 2. The current governance mandates Ketiv (written form) as primary for all gematria calculations.

**Verification Steps:**

1. **Confirm active code path:**
   * The active Gematria code path used by RAG:
     - reads the Ketiv form from the canonical text source (`surface` field),
     - uses Ketiv values for all Gematria calculations,
     - and does not have any remaining branches or flags that still prefer Qere.

2. **Run governance guard:**
   ```bash
   make guard.ketiv.primary
   # Expected: No violations reported
   ```

3. **Run tests:**
   ```bash
   python -m pytest tests/unit/test_ketiv_primary.py -v
   # Expected: All tests pass
   ```

**Source(s):**
- `docs/ADRs/ADR-002-gematria-rules.md` - Ketiv-primary policy (SSOT)
- `docs/analysis/KETIV_QERE_POLICY_CONFLICT.md` - Policy enforcement details
- `scripts/guards/guard_ketiv_primary.py` - Validation guard
- `tests/unit/test_ketiv_primary.py` - Policy compliance tests
- `src/core/hebrew_utils.py` - `get_ketiv_for_gematria()` helper function

---

## III. Execution Plan

### Step 1: Update Test Data (Priority: HIGH)

**Commands:**
```bash
# 1. Verify current test verse_ids
grep -r "verse_id.*=" pmagent/biblescholar/tests/ | grep -v ">= 42358"

# 2. Update test_rag_retrieval.py to use dynamic verse_id lookup
# 3. Update test_reranker_adapter.py to use dynamic verse_id lookup
# 4. Update test_embedding_adapter.py to use dynamic verse_id lookup

# 5. Run tests to verify
pytest pmagent/biblescholar/tests/test_rag_retrieval.py -v
pytest pmagent/biblescholar/tests/test_reranker_adapter.py -v
pytest pmagent/biblescholar/tests/test_embedding_adapter.py -v
```

**Expected Output:**
- All tests pass with real verse_ids
- No "verse_id not found" errors
- 1024-D embedding verification passes

### Step 2: Certify Rule 045 Blend (Priority: HIGH)

**Commands:**
```bash
# 1. Verify EDGE_ALPHA default
grep -r "EDGE_ALPHA" scripts/ pmagent/biblescholar/ | grep -v "0.5"

# 2. Check blend formula consistency
grep -r "edge_strength.*=" scripts/ pmagent/biblescholar/ | head -20

# 3. Run blend validator (if graph exists)
python scripts/eval/validate_blend_ssot.py

# 4. Check validator output
cat share/eval/edges/blend_ssot_report.json | jq '.blend_mismatch, .missing_fields'
```

**Expected Output:**
- All code paths use `EDGE_ALPHA=0.5` (or env override)
- Blend validator reports 0 mismatches
- All edges have Rule 045 fields

### Step 3: Rebuild Graph with Rule 045 Fields (Priority: HIGH)

**Commands:**
```bash
# 1. Re-run graph build/export (if needed)
# Note: This may require running the full pipeline or a subset
# Check Makefile for graph export targets

# 2. Verify graph_latest.json has Rule 045 fields
python -c "import json; g=json.load(open('exports/graph_latest.json')); e=g.get('edges',[]); print(f'Edges: {len(e)}'); print(f'Has cosine: {sum(1 for x in e if \"cosine\" in x)}'); print(f'Has rerank_score: {sum(1 for x in e if \"rerank_score\" in x)}'); print(f'Has edge_strength: {sum(1 for x in e if \"edge_strength\" in x)}')"

# 3. Re-run extract script
python scripts/extract_all.py --size 10000 --outdir ui/out

# 4. Verify envelope has Rule 045 fields
python -c "import json; e=json.load(open('ui/out/unified_envelope_10000.json')); edges=e.get('edges',[]); print(f'Edges: {len(edges)}'); print(f'Has cosine: {sum(1 for x in edges if \"cosine\" in x)}'); print(f'Has rerank_score: {sum(1 for x in edges if \"rerank_score\" in x)}'); print(f'Has edge_strength: {sum(1 for x in edges if \"edge_strength\" in x)}')"
```

**Expected Output:**
- `graph_latest.json` contains edges with Rule 045 fields
- `unified_envelope.json` contains Rule 045 fields
- Edge counts match expectations

### Step 4: Run COMPASS Validation (Priority: HIGH)

**Commands:**
```bash
# 1. Run COMPASS scorer on envelope
make test.compass  # or python scripts/compass/scorer.py ui/out/unified_envelope_10000.json --verbose

# 2. Check COMPASS score
# Expected: >80% correctness score
```

**Expected Output:**
- COMPASS score >80%
- No critical violations reported
- Edge strength blend validation passes

---

## IV. Acceptance Checklist

- [ ] **Gate 1: RAG Tests Aligned to Real Data**
  - [ ] All RAG live tests (`@pytest.mark.live`) use verse_ids ≥ 101,850
  - [ ] All live tests verify 1024-D embedding dimensionality
  - [ ] `pytest pmagent/biblescholar/tests/test_rag_live.py -m live -v` passes

- [ ] **Gate 2: Graph Export with Rule-045 Fields**
  - [ ] `exports/graph_latest.json` contains non-zero edges
  - [ ] Every edge has `cosine`, `rerank_score`, and `edge_strength` fields
  - [ ] `edge_strength = 0.5 * cosine + 0.5 * rerank_score` (verified by blend validator)
  - [ ] `python scripts/eval/validate_blend_ssot.py` reports 0 mismatches

- [ ] **Gate 3: COMPASS Baseline Run**
  - [ ] `scripts/extract_all.py` runs on real data (reads `graph_latest.scored.json`)
  - [ ] `unified_envelope.json` contains Rule 045 fields
  - [ ] COMPASS scorer runs and produces non-zero score
  - [ ] COMPASS score >= 80% (recorded in Phase-15 log / PM share)

- [ ] **Gematria Governance: Ketiv-Primary**
  - [ ] `make guard.ketiv.primary` passes (no violations)
  - [ ] `python -m pytest tests/unit/test_ketiv_primary.py -v` passes
  - [ ] Active code path confirmed to use Ketiv (surface field) for gematria

---

## V. Next Gate

Once all acceptance criteria are met:

1. **Step 3 (Full Validation Harness)** can proceed:
   - Run three-tier harness (Tier 1: Gematria, Tier 2: RAG, Tier 3: COMPASS)
   - Verify COMPASS score >80%
   - Mark Phase 15 Wave-3 as **production-ready**

2. **Documentation Updates:**
   - Update `PHASE15_WAVE3_PLAN.md` to mark Step 2 as complete
   - Update `MASTER_PLAN.md` with Phase 15 status
   - Generate `share/gate_status.md` with explicit gate completion status

---

## VI. Related Documents

- `docs/SSOT/PHASE15_WAVE3_PLAN.md` - Full Wave-3 plan
- `docs/SSOT/PHASE15_COMPASS_ALIGNMENT_ANALYSIS.md` - COMPASS alignment analysis
- `docs/SSOT/SHARE_FOLDER_GATE_STATUS_GAP.md` - Gate status gap analysis
- `docs/SSOT/KB_REGISTRY_ARCHITECTURAL_COURSE_CORRECTION.md` - KB curation gates

---

## VII. Notes

- **Test data alignment is the primary blocker**, not infrastructure
- **Rule 045 blend is already implemented** in code; need to certify consistency
- **COMPASS integration requires fresh graph export** with Rule 045 fields
- **All gates are complete**; this is the final alignment step before Step 3 validation

