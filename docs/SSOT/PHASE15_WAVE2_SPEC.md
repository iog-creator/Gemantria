# Phase 15 Wave-2 Specification — Advanced RAG Engine (Option B)

**Status**: Active Development  
**Profile**: Option B (Standard)  
**Dependencies**: Phase 14 ✅ COMPLETE, Phase 15 Wave-1 ✅ COMPLETE

---

## Architectural Decision: Option B (Standard Profile)

**Rationale** (from Orchestrator):
> The inclusion of a reranker fallback is essential for advanced RAG systems. Research confirms that a robust reranking step significantly improves Context Precision and drastically lowers the LLM's Hallucination rate by filtering noise introduced during the initial retrieval phase.

**Profile Characteristics**:
- **Context Window**: 5-verse range (±2 verses from seed)
- **Embedding Dimension**: 1024-D (BGE-M3 fidelity via pgvector)
- **Ranking Algorithm**: Combined score = (0.7 × embedding_similarity) + (0.3 × reranker_score)
- **Cross-Language Signals**: Uses Phase 14 RelationshipAdapter for Greek-Hebrew lemma hints
- **Reranker**: Non-negotiable (Granite Reranker primary, BGE fallback)

---

## Component Architecture

### 1. RAG Retrieval Engine (`rag_retrieval.py`)

**Main Class**: `RAGRetriever`

**API**:
```python
retrieve_contextual_chunks(query: str, top_k: int = 5) -> list[dict]
```

**Internal Methods**:
- `_compute_relevance_score()` — 1024-D cosine similarity via pgvector
- `_apply_reranker_fallback()` — Mandatory reranking layer
- `_expand_context_window()` — 5-verse window expansion

**DB-First**: All data from `bible.verse_embeddings` (pgvector), no external vector DBs.

---

### 2. Embedding Adapter (`embedding_adapter.py`)

**Main Class**: `EmbeddingAdapter`

**API**:
- `get_embedding_for_verse(verse_id: int) -> np.ndarray` — Retrieve 1024-D embedding
- `compute_query_embedding(query: str) -> np.ndarray` — Generate query embedding (BGE-M3)
- `vector_search(query_embedding: np.ndarray, top_k: int) -> list[tuple[int, float]]` — pgvector search

**Schema Assumptions**:
- Table: `bible.verse_embeddings` (columns: `verse_id`, `embedding_1024d`, `model_version`)
- Index: `ivfflat (embedding_1024d vector_cosine_ops)`

---

### 3. Reranker Adapter (`reranker_adapter.py`)

**Main Class**: `RerankerAdapter`

**API**:
- `rerank_chunks(chunks: list[dict], query: str) -> list[dict]` — Rerank by relevance

**Model Stack**:
- Primary: Granite Reranker (local via LM Studio/Ollama)
- Fallback: BGE Reranker
- Hermetic Mode: Returns original ranking if reranker unavailable (no hard failure)

---

## Integration with Phase 14

**RelationshipAdapter** (batch optimization):
- New method: `get_enriched_context_batch(verse_ids: list[int]) -> list[dict]`
- Purpose: Reduce N+1 queries for 5-verse windows

**LexiconAdapter** (batch optimization):
- New method: `get_greek_words_batch(verse_refs: list[str]) -> dict[str, list[dict]]`
- Purpose: Optimize context window retrieval

---

## Test Vectors

**TV-Phase15-Wave2-01**: Basic retrieval with 1024-D embeddings  
**TV-Phase15-Wave2-02**: Reranker fallback improves ranking  
**TV-Phase15-Wave2-03**: 5-verse context window expansion  
**TV-Phase15-Wave2-04**: Cross-language lemma signals present  
**TV-Phase15-Wave2-05**: Hermetic mode graceful degradation  

---

## Quality Gates

**Hermetic**:
- All test vectors pass with DB-off graceful degradation
- `pytest agentpm/biblescholar/tests/test_rag_retrieval.py -v`

**Live** (Required per PM Contract §6.6):
- pgvector 1024-D embeddings accessible
- Reranker invocation verified
- 5-verse context window expansion functional
- `make reality.green` passes

---

## Future Work (Wave-3)

- API Gateway layer for external integrations
- UI components for RAG visualization
- Performance optimization (caching, batch inference)
