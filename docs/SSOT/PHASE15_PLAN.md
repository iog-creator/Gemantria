# Phase 15 Plan — Advanced RAG Context Integration

## 1. Goal

Design and implement a contextual chunk framework for RAG using:

- RelationshipAdapter (Phase 14)
- Lexicon & cross-language lemma flows (Phase 14)
- 1024-D embeddings (Phase 13)

## 2. Scope (Phase 15, wave 1)

- Implement contextual chunk builder:

  - input: verse_ref (e.g. "Mark 1:1")

  - output: list of enriched chunks with:

    - verse_id / verse_ref

    - greek_words / lemmas (where applicable)

    - proper_names

    - cross-language lemma hints (when available)

- Implement contextual fetch API for BibleScholar:

  - aggregation over RelationshipAdapter + lexicon adapter

- Exclude UI and external API gateway for this wave (internal Python API only).

## 3. Salvage Inputs from PR #593

- `docs/SSOT/contextual_chunk.schema.json` (schema reference only)

- `pmagent/biblescholar/contextual_chunks.py` (structure only)

- `pmagent/biblescholar/contextual_fetch.py` (structure only)

No code is copied verbatim; structure and schema only.

## 4. Quality Gates

- Must pass `scripts/verify_pmagent_dms_master.py`.

- New tests under `pmagent/biblescholar/tests/`:

  - tv-phase15-01: single verse contextual chunk build

  - tv-phase15-02: cross-language hints present when mapping exists

  - tv-phase15-03: hermetic mode behavior (DB off) is graceful.


## Wave-2 Status (2025-12-01)

Wave-2 (Advanced RAG Engine — Option B, Standard Profile) is **hermetic complete**:

* Embedding adapter implemented with 1024-D BGE-M3 + pgvector

* Reranker adapter implemented with combined scoring (0.7 × embedding + 0.3 × reranker)

* RAG retrieval orchestrator implemented with Phase 14 enrichment

* 5-verse context window behavior implemented in contextual chunk builder

* All Wave-2 test vectors implemented (TV-Phase15-Wave2-01..05)

* 174/174 BibleScholar regression tests passing

* All ruff format and lint checks passing

Phase 15 remains **open** pending Wave-3 live DB+LM validation and environment governance hardening.

