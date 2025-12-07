# Phase 15 — Wave-3 Plan: Live RAG Validation & LM Wiring

## 1. Purpose

Wave-3 takes the hermetically complete Advanced RAG Engine from Wave-2 and:

* Wires it to real DB + LM infrastructure.

* Performs live end-to-end validation (per PM Contract §6.6).

* Closes the remaining governance gaps (e.g., venv hint behavior).

* Brings Phase 15 to full production-ready status.

## 2. Scope

Wave-3 includes:

1. **Live DB+LM Validation**

   * Run RAG retrieval against real Postgres with pgvector embeddings.

   * Wire `compute_query_embedding(query)` to a real BGE-M3 endpoint.

   * Wire `RerankerAdapter` to a live reranker model (Granite or BGE).

   * Capture evidence of:

     * successful retrieval,

     * non-empty, ranked chunks,

     * reranker actually changing rankings,

     * 5-verse windows behaving as expected.

2. **Query Embedding Wiring**

   * Implement `EmbeddingAdapter.compute_query_embedding(query)`:

     * Use BGE-M3 1024-D model via LM Studio / local inference.

   * Add tests that:

     * verify dimensionality (1024-D),

     * validate basic similarity behavior on simple queries (sanity checks).

3. **Reranker LM Wiring**

   * Implement `_ensure_lm()` and `_compute_rerank_score()` in `RerankerAdapter`.

   * Choose primary reranker (Granite or BGE) with a fallback.

   * Add tests that:

     * mock LM responses,

     * verify combined scoring still uses 0.7 × embedding + 0.3 × reranker,

     * confirm reranker is invoked and can change ordering.

4. **Context Window Metadata Completion**

   * Ensure `context_window` metadata is fully populated in RAG results, consistent with:

     * 5-verse window (±2 verses from seed),

     * Phase 14 enrichment metadata (proper names, Greek words, cross-language hints).

   * Add tests that check:

     * window size,

     * presence of seed verse,

     * enrichment metadata coverage across the window.

5. **Performance & Caching (Non-blocking)**

   * Measure end-to-end latency for common queries.

   * Introduce caching or batch strategies if needed.

   * Document performance characteristics and any constraints.

6. **VEnv Governance Hardening**

   * Address the venv hint gap identified in `evidence/venv_hint_gap_analysis.md`:

     * Add `scripts/guards/guard_venv.py` or equivalent.

     * Enhance `scripts/check_venv.sh` with loud HINT emission.

     * Add `check.venv` Makefile target.

     * Update PM contract / docs to clearly require venv usage for test runs.

## 3. Definition of Done (Wave-3)

Wave-3 is complete when:

* Live DB+LM RAG tests have been run and recorded as evidence.

* `compute_query_embedding` uses a real model and passes tests.

* `RerankerAdapter` is wired to a real reranker and passes tests.

* Context window metadata is fully populated and tested.

* A minimal performance assessment has been recorded.

* VEnv governance guard is implemented and enforced via CI/guards.

* MASTER_PLAN and Phase 15 docs are updated to mark Phase 15 as **production-ready**.

## 4. Out of Scope

* External API gateway for RAG (Wave-4).

* UI integration and dashboards (future phases).

* Non-Bible corpora or cross-project RAG integrations.


## 5. Live Validation Tiers (Wave-3)

Wave-3 validation is organized into three tiers. The goal is to separate:

* deterministic math (Gematria module),

* probabilistic retrieval (AgentPM RAG spine),

* and envelope-level correctness (COMPASS + Rule 045).

All tiers treat `db_off` or `lm_off` as **LOUD FAIL** when those components are required, in line with PM Contract §6.6 and Rule-052.

### 5.1 Tier 1 — Gematria Module (Deterministic Integrity)

Objectives:

* Verify that Gematria remains a **pure numerics / Bible-logic module**, independent of LM provider details.

* Ensure that new contextual chunking and scoring layers have not corrupted math or policy.

Live validation requirements:

1. **Numeric Verification Enforcement**

   * Wave-3 must invoke the existing math verification flow (e.g., `verification.py` and related scripts) after contextual enrichment steps.

   * This verifies that Gematria calculations remain mathematically correct even when data passes through contextual chunking and RAG paths.

2. **Ketiv/Qere Policy Compliance**

   * Gematria must implement the SSOT policy:

     * **Ketiv is the primary reading** for Gematria.

     * Qere is stored and displayed only as a variant, not used as the main numeric source.

   * Live tests must:

     * use a verse with a known Ketiv/Qere pair, and

     * confirm that Gematria uses Ketiv for `edge_strength` / numeric calculations.

3. **Multi-Language Purity (Phase 13 Contract)**

   * Confirm that Phase 13 guarantees still hold end to end:

     * Hebrew normalization: NFKD → strip combining marks → NFC.

     * Greek Isopsephy: diacritics removed, stable numeric mapping.

     * Strong's IDs: language prefixes (`H` or `G`) are present when querying `bible_db`, preventing ambiguous dictionary lookups.

   * Live validation should include at least:

     * one Hebrew-heavy case,

     * one Greek-heavy case,

     * both exercising verse → Strong's → Gematria paths.

### 5.2 Tier 2 — AgentPM RAG Spine (Live Retrieval & Scoring)

Objectives:

* Validate the **Phase 15 Option B** RAG design using **live DB + live LM**, with the RAG engine treated as a shared spine used by BibleScholar and Gematria flows.

* Confirm that the LM provider (currently LM Studio) is correctly serving:

  * a 1024-D embedding model, and

  * a reranker model.

Live validation requirements:

1. **End-to-End Live RAG Execution**

   * Run a **small live slice** of the RAG pipeline (e.g., via `test_rag_live.py` or an equivalent harness) that performs:

     * query → 1024-D query embedding (via configured embedding model in LM Studio or other active provider),

     * pgvector similarity search in Postgres,

     * reranker scoring via the configured reranker model,

     * combined scoring and context window construction.

   * `db_off` or `lm_off` in this path is a **hard failure**, not a warning.

2. **Reranker Profile Verification (Provider-Agnostic)**

   * The validation must confirm:

     * the configured **1024-D embedding model** is actually used for retrieval, and

     * the configured **reranker model** is invoked and contributes to the final score.

   * Implementation detail (provider-agnostic):

     * Today, these models run through **LM Studio**.

     * In the future, they may also be available via Ollama or another provider.

     * The RAG spine must not depend on provider-specific behavior; it only expects:

       * an embedding endpoint,

       * a reranker endpoint.

3. **Contextual Metadata Proof (Phase 14 Integration)**

   * Live results must show that the RAG engine:

     * enriches verses/chunks with RelationshipAdapter metadata (proper names, relationships),

     * enriches with LexiconAdapter metadata (Greek words, lemmas),

     * surfaces **cross-language lemma signals** (e.g., Greek ↔ Hebrew Strong's mappings).

   * At least one live test case must:

     * query a verse with known cross-language mappings, and

     * confirm that the enriched metadata contains the expected cross-language hints.

### 5.3 Tier 3 — COMPASS + Rule 045 (Envelope-Level Correctness)

Objectives:

* Validate that the final data envelope (where Gematria + RAG + graph/temporal features converge) satisfies COMPASS correctness requirements, including **Rule 045** blend semantics and **>80% COMPASS score** for envelope acceptance.

Live validation requirements:

1. **Rule 045 — Blend Calculation Correctness**

   * Ensure that the RAG engine produces scores compatible with the SSOT blend contract:

     * `edge_strength = α * cosine + (1 - α) * rerank_score`

     * with `EDGE_ALPHA = 0.5` and tolerance `BLEND_TOL = 0.005`.

   * Integrate the existing blend validation script (e.g., `scripts/eval/validate_blend_ssot.py`) into the Wave-3 validation flow.

   * The graph export step (e.g., via `scripts/export_graph.py` or an equivalent make target) must produce artifacts such as `graph_latest.scored.json` containing:

     * cosine similarity,

     * reranker score,

     * final blended edge strength,

     * SSOT field names.

2. **COMPASS Score Threshold (>80%)**

   * Run the full envelope export (e.g., `make ui.extract.all`) and COMPASS scorer against the resulting envelope (e.g., `unified_envelope.json` or equivalent).

   * Wave-3 "done" condition requires:

     * COMPASS mathematical correctness score **>80%** on the envelope that includes Phase 15 RAG contributions.

   * If the COMPASS score is below the threshold:

     * treat it as a **release blocker** for Phase 15,

     * open remediation work on:

       * RAG retrieval quality,

       * reranker weighting,

       * Gematria integration,

       * or graph/temporal feature alignment.

3. **LLM Subordination & Grounding**

   * Confirm that:

     * LLM output remains **metadata-only** (labels, summaries, classifications),

     * all factual/Scriptural authority is grounded in the database and Gematria module (`LLM < bible_db`),

     * no theological interpretations from the LLM are treated as truth in the envelope.

   * COMPASS scoring must be able to rely on:

     * deterministic Gematria/math,

     * RAG scores produced from the embedding+reranker blend,

     * strictly controlled LLM contributions.

## 6. Provider-Agnostic LM Assumptions

* LM Studio is currently the **only active LM backend**; Ollama is disabled by configuration but may be turned back on later.

* The RAG spine and validation plan must remain **provider-agnostic**:

  * they depend on "an embedding model" and "a reranker model" exposed via LM APIs,

  * not on LM Studio or Ollama specifically.

* Orchestrator Assistant proposals (like the Wave-3 validation strategy) are treated as **advisory**; they become SSOT only when adopted and recorded in documents such as this plan.


## 8. Execution Phasing (Wave-3 Steps)

Wave-3 is executed in clearly separated steps:

1. **Step 1 — LM Wiring & Live Sanity (COMPLETE)**

   * Embedding and reranker adapters are wired to real LM endpoints (LM Studio today).

   * Live RAG sanity tests (e.g., `test_rag_live.py` with `@pytest.mark.live`) verify:

     * basic query embedding calls,

     * pgvector searches,

     * reranker calls.

   * LOUD FAIL semantics are enforced if DB or LM are unavailable.

   * Status: treated as implemented on the current branch.

2. **Step 2 — Blend Scoring Integration (Rule 045)**

   * RAGRetriever and related components must:

     * compute cosine and rerank scores for each candidate,

     * compute `edge_strength_blend` according to Rule 045:

       * `edge_strength = α * cosine + (1 - α) * rerank_score`

       * with `EDGE_ALPHA = 0.5`, `BLEND_TOL = 0.005`.

   * `scripts/export_graph.py` (or `make graph.export`) must emit a scored graph file

     (e.g., `exports/graph_latest.scored.json`) containing:

     * cosine similarity,

     * rerank score,

     * blended edge strength,

     * SSOT field names.

   * `scripts/eval/validate_blend_ssot.py` must be integrated into the Wave-3 flow to validate the blend contract.

3. **Step 3 — Full Validation Harness Execution**

   * Run the three-tier harness defined in Sections 5–7:

     * **Tier 1:** Gematria determinism (math verifier, Ketiv primary, Strong's prefixes, cross-language lemma TODO resolved).

     * **Tier 2:** AgentPM RAG live tests (embedding, vector search, end-to-end retrieval).

     * **Tier 3:** Graph export + Rule 045 validator + envelope extraction + COMPASS scorer.

   * Precondition: `make reality.green` or `pmagent reality-check check --mode strict` must pass, confirming DB, control-plane, and LM health.

   * Acceptance: COMPASS score > 80% on the Wave-3 envelope and no critical Gematria/RAG governance violations.

## 9. LLM Governance Harness (Content Synthesis Control)

Wave-3 validation must enforce strict LLM governance:

1. **LLM Subordination Order**

   * Authority order is:

     * **Code Gematria > bible_db > LLM**

   * LLM output is always treated as **metadata-only** (summaries, paraphrases, labels), never as the primary source of truth.

2. **No Content Synthesis**

   * System prompts and harness configuration must:

     * forbid the LLM from generating new biblical content,

     * forbid doctrinal or theological claims that are not directly supported by retrieved context,

     * ensure responses are grounded in verses and data retrieved from `bible_db` and Gematria pipelines.

   * Any detected hallucinated verses or theology during validation is considered a governance bug and must be corrected before Wave-3 is marked complete.

3. **Harness-Level Checks**

   * Where feasible, add checks/tests that:

     * inspect sample outputs to confirm they reference existing verses and data,

     * verify citations align with retrieved context,

     * log and flag any suspected hallucinations or unsupported expansions.

   * These checks can be a mix of automated tests and manual review on a curated test set.


## 10. Current Validation Status & Blockers (as of 2025-12-01)

### 10.1 Step-2 (Rule 045 Blend Wiring)

* Status: **COMPLETE (code-level)**.

* RAG spine now uses:

  * `cosine` for embedding similarity,

  * `rerank_score` for reranker output,

  * `edge_strength = 0.5 * cosine + 0.5 * rerank_score` (Rule 045, EDGE_ALPHA=0.5).

* Tests updated:

  * `pmagent/biblescholar/tests/test_reranker_adapter.py`

  * `pmagent/biblescholar/tests/test_rag_retrieval.py`

  * `pmagent/biblescholar/tests/test_rag_live.py` (field names and expectations).

* `scripts/export_graph.py` and `scripts/eval/validate_blend_ssot.py` are aligned on field names and math.

### 10.2 Step-3 (Full Live Harness Execution)

* Status: **BLOCKED ON DATA ALIGNMENT**, not on missing infrastructure.

**Reality Gate:**

* DB and control-plane: healthy.

* LM: reachable via LM Studio.

* **Embeddings exist**: 116,566 embeddings in `bible_db.bible.verse_embeddings` (verse_ids ~101850+).

* Governance issues:

  * AGENTS.md sync, share exports, ledger verification, and hint registry reported failures.

  * These are tracked as governance/ops items; they do not indicate DB/LM infra failure.

**Tier 1 — Gematria Determinism:**

* Gematria / cross-language code present.

* Math verifier tests and cross-language tests did not run cleanly in this attempt (pytest/env wiring).

* Requires a follow-up pass to:

  * locate or add dedicated tests,

  * ensure they run under the current env.

**Tier 2 — RAG Live Tests:**

* Live tests executed via:

  * `pytest pmagent/biblescholar/tests/test_rag_live.py -m live -v`

* Results:

  * Several tests passed (end-to-end RAG, reranker integration, contextual chunks).

  * Several tests failed due to **verse_id mismatch**: tests check verse_ids 1-10, but actual embeddings use verse_ids ~101850+.

* Conclusion:

  * RAG live pipeline is wired and callable.

  * Failures are due to **test data alignment** (wrong verse_ids), not missing embeddings or scoring logic.

**Tier 3 — Graph Export + Blend Validator + COMPASS:**

* `graph_latest.scored.json` exists but contains **0 edges** (stale export from before Step-2).

* Blend validator:

  * Ran successfully but checked 0 edges:

    * `checked_edges: 0`

    * `blend_mismatch: 0`

    * `missing_fields: 0`

* Unified envelope:

  * `scripts/extract_all.py --size 10000 --outdir ui/out` produced `ui/out/unified_envelope_10000.json`.

  * Edges use legacy `strength` field and lack Rule 045 fields (`cosine`, `rerank_score`, `edge_strength`).

* COMPASS:

  * Ran on the extracted envelope and reported:

    * **COMPASS score: 0.0% (below 80% threshold)**,

    * missing correlation weights, blend fields, and temporal patterns.

* Conclusion:

  * Current graph/envelope are built from **pre-Step-2 data and schema**.

  * COMPASS cannot yet provide a meaningful Wave-3 assessment until graph is rebuilt with Rule 045 fields.

### 10.3 Preconditions for Future Wave-3 Completion

To complete Wave-3 and achieve a meaningful COMPASS score:

1. **Use Existing Embeddings (Data Alignment)**

   * Update RAG live tests to use actual verse_ids (~101850+) that have embeddings.

   * Or verify `get_embedding_for_verse()` correctly maps test verse_ids to actual embeddings.

2. **Rebuild Graph with Rule-045 Fields**

   * Re-run the graph build/export logic so that edges include:

     * `cosine`,

     * `rerank_score`,

     * `edge_strength` computed via Rule 045.

   * Re-run:

     * `scripts/export_graph.py` (or equivalent graph build pipeline),

     * `scripts/eval/validate_blend_ssot.py` (should now check real edges).

3. **Re-run Tier 2 and Tier 3 Harness**

   * Re-run live RAG tests (`test_rag_live.py -m live`) with correct verse_ids.

   * Rebuild the unified envelope (`scripts/extract_all.py`) from the updated graph.

   * Re-run COMPASS scorer; Wave-3 requires:

     * COMPASS score ≥ 80%,

     * no critical Gematria or RAG governance violations.

4. **Governance Cleanup (Recommended but Parallel)**

   * Fix AGENTS sync, share exports, ledger verification, and hint registry/venv issues so that:

     * `make reality.green` and/or `pmagent reality-check --mode strict` are fully green for production.


## 11. PM Correction: Attached File Evidence Integration

### 11.1 Issue

Prior PM analysis incorrectly inferred missing embeddings and incomplete COMPASS infrastructure based on failing tests.

### 11.2 Source of Error

Attached files already contained:

* confirmation of 116,566 embeddings in `bible_db.bible.verse_embeddings`
* prior COMPASS execution
* existing graph/export infrastructure
* verse_id domain (~100k)
* historic system runs in earlier phases

These were not integrated into analysis.

### 11.3 Correction

PM must integrate evidence from:

* SSOT documents
* all attached project files
* Cursor execution evidence

  **before** issuing system-state conclusions.

### 11.4 Unified Correct System State

* Embeddings exist and are healthy
* COMPASS infrastructure is present
* Live RAG failures result from test verse_ids not matching DB domain
* Graph/envelope used for validation was stale
* Wave-3 Step-2 is complete (code-level)
* Wave-3 Step-3 is blocked on data alignment, not infra

