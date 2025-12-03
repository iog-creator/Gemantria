# Phase 15 Wave-3 Gate — Baseline Before DSPy

**Date**: 2025-12-02  
**Status**: Active Governance  
**Source**: PM Decision + OPS Block Alignment

---

## 1. Phase Completion

**Phase 15 Wave-3 is complete when:**

* COMPASS score >= 80% on real data, and
* Rule 045 edge fields (`cosine`, `rerank_score`, `edge_strength`) are present and validated.

**Source(s):**
- `docs/SSOT/MASTER_PLAN.md` - COMPASS threshold requirements
- `.cursor/rules/045-rerank-blend-SSOT.mdc` - Rule 045 field requirements
- `docs/SSOT/PHASE15_WAVE3_PLAN.md` - Wave-3 completion criteria

---

## 2. Tool Dependency

**DSPy is not a governance-mandated dependency for Phase 15 completion.**

* DSPy is a candidate framework for Phase 16+ reliability tuning after a baseline COMPASS score exists.
* Phase 15 completion requires **measurement first** (baseline COMPASS score), then optimization decisions can be made.

**Source(s):**
- `docs/SSOT/POSTGRES_OPTIMIZATION_PRIORITY.md` - "Measure first, then optimize" pattern
- `docs/SSOT/DMS_PERFORMANCE_OPTIMIZATION.md` - Optimization framework decisions

---

## 3. Mandatory Next Steps (Wave-3 Alignment)

**Phase 15 Wave-3 cannot be called "COMPASS-ready" until:**

1. **RAG tests aligned to real data**
   * All RAG live tests use `verse_id` values that exist in the current `bible.verse_embeddings` 1024-D domain (ID range ~101,850+).
   * No tests reference dummy IDs 1–10.
   * **Verification**: `pytest pmagent/biblescholar/tests/test_rag_live.py -m live -v` passes with real verse_ids.

2. **Graph export rebuilt with real Rule-045 fields**
   * `exports/graph_latest.scored.json` contains non-zero edges.
   * Every edge has `cosine`, `rerank_score`, and `edge_strength = 0.5 * cosine + 0.5 * rerank_score`.
   * **Verification**: `python scripts/eval/validate_blend_ssot.py` reports 0 mismatches.

3. **COMPASS baseline run completed**
   * `scripts/extract_all.py` runs on real data (no mocks).
     - It reads `exports/graph_latest.scored.json`.
     - The COMPASS scorer runs and produces a non-zero score.
     - The resulting COMPASS score is recorded in the Phase-15 log / PM share.
   * **Verification**: `make test.compass` or `python scripts/compass/scorer.py ui/out/unified_envelope_10000.json --verbose` reports >80% score.

**Source(s):**
- `docs/SSOT/PHASE15_WAVE3_STEP2_OPS_BLOCK.md` - Detailed execution plan
- `scripts/eval/validate_blend_ssot.py` - Rule 045 blend validator
- `scripts/compass/scorer.py` - COMPASS scorer

---

## 4. Gematria Governance (Ketiv Primary)

**Gematria calculations used in pipelines must use Ketiv-primary numerics.**

* RAG tests that exercise the Gematria Module must not rely on any legacy Qere-primary policy.
* All gematria calculations must use the Ketiv (written form) from the `surface` field, not Qere (read form) from `variant_surface`.

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

---

## 5. Next Gate

Once all mandatory steps are complete:

* **Step 3 (Full Validation Harness)** can proceed:
  - Run three-tier harness (Tier 1: Gematria, Tier 2: RAG, Tier 3: COMPASS)
  - Verify COMPASS score >80%
  - Mark Phase 15 Wave-3 as **production-ready**

* **Phase 16 (or later reliability phase):**
  - Decide if DSPy is needed based on baseline COMPASS score
  - If COMPASS ≥ 80% and stable: DSPy is "nice to have"
  - If COMPASS < 80% or fragile: DSPy becomes systematic tuning framework

