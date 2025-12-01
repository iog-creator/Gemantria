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

- `agentpm/biblescholar/contextual_chunks.py` (structure only)

- `agentpm/biblescholar/contextual_fetch.py` (structure only)

No code is copied verbatim; structure and schema only.

## 4. Quality Gates

- Must pass `scripts/verify_pmagent_dms_master.py`.

- New tests under `agentpm/biblescholar/tests/`:

  - tv-phase15-01: single verse contextual chunk build

  - tv-phase15-02: cross-language hints present when mapping exists

  - tv-phase15-03: hermetic mode behavior (DB off) is graceful.

