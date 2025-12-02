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

