# ADR-026: Reranker Bi-Encoder Proxy Implementation

## Status

Accepted

## Context

The Gematria pipeline uses reranking to improve the quality of semantic relationships between concepts. The original implementation attempted to use LM Studio's reranker models via the `/v1/chat/completions` endpoint, which proved problematic because:

1. LM Studio does not expose a dedicated `/v1/rerank` API endpoint
2. Reranker GGUFs loaded in LM Studio behave unpredictably when called via `/v1/chat/completions`
3. This resulted in empty, odd, or neutral (0.5) responses that degraded relationship quality
4. Multiple large models loaded simultaneously caused VRAM pressure and system instability

The pipeline requires stable, meaningful similarity scores in the [0.0, 1.0] range to compute edge strengths for the semantic network.

## Decision

Replace the problematic reranker implementation with a **bi-encoder proxy** that computes cosine similarity between BGE-M3 embeddings of concept name pairs, accessed via LM Studio's `/v1/embeddings` endpoint.

### Implementation Details

- **New Service**: `src/services/rerank_via_embeddings.py`
- **Algorithm**: Cosine similarity between BGE-M3 embeddings of paired concept names
- **API Compatibility**: Uses only LM Studio's `/v1/embeddings` endpoint
- **Interface**: Drop-in replacement maintaining `rerank_pairs(pairs, name_map)` signature
- **Model Management**: Explicit `lms unload --all` between phases to prevent VRAM conflicts

## Rationale

### Benefits

- **LM Studio Compatibility**: Uses only supported API endpoints (`/v1/embeddings`)
- **Stable Scores**: Provides meaningful semantic similarity scores instead of neutral fallbacks
- **VRAM Efficiency**: Single model loading with explicit unloading prevents conflicts
- **Interface Preservation**: Zero changes required to calling code (network_aggregator.py)
- **Future-Proof**: Easy to revert to native rerank API when LM Studio adds support

### Trade-offs Considered

- **Cross-encoder vs Bi-encoder**: Bi-encoder provides semantic similarity but not query-document relevance scoring
- **Computational Cost**: Two embedding API calls per batch vs single rerank call
- **Score Quality**: Cosine similarity may be less precise than trained cross-encoder models

### Alignment with Project Goals

- **Correctness**: Code gematria > bible_db > LLM - reranker is metadata enhancement only
- **Determinism**: Fixed embeddings model (BGE-M3) ensures reproducible results
- **Safety**: Fail-closed behavior maintained with proper error handling
- **Production Ready**: No external dependencies, LM Studio-only solution

## Alternatives Considered

### Alternative 1: External Reranker Service

- **Pros**: Access to high-quality cross-encoder models, dedicated rerank APIs
- **Cons**: External dependency, network latency, API costs, data privacy concerns
- **Reason Rejected**: Violates LM Studio-only requirement and introduces external dependencies

### Alternative 2: Skip Reranking Entirely

- **Pros**: Simplifies pipeline, reduces API calls, eliminates reranker complexity
- **Cons**: Loses semantic refinement of relationships, degrades network quality
- **Reason Rejected**: Reranking provides meaningful improvement to edge strength calculations

### Alternative 3: Fallback to Neutral Scores

- **Pros**: Simple implementation, no API changes required
- **Cons**: All relationships get 0.5 scores, no semantic differentiation
- **Reason Rejected**: Degrades network quality and wastes computational effort

## Consequences

### Positive

- Improved semantic relationship quality through meaningful similarity scores
- Stable LM Studio integration without unsupported API usage
- Reduced VRAM pressure through single-model loading strategy
- Maintainable codebase with clear separation of reranking logic
- Future migration path when LM Studio adds native rerank support

### Negative

- Additional API calls (2 embeddings per pair vs 1 rerank call)
- Slightly different scoring semantics (similarity vs relevance)
- New service module increases codebase complexity

### Implementation Requirements

1. **Create rerank_via_embeddings.py** with bi-encoder proxy implementation
2. **Update network_aggregator.py** import to use new service
3. **Update environment configuration** for BGE-M3 embeddings
4. **Update documentation** (AGENTS.md files, this ADR)
5. **Test integration** with small batch to verify scores and performance
6. **Update model loading scripts** to use explicit unload commands

## Related ADRs

- **ADR-010**: Qwen Integration - Original reranker implementation
- **ADR-014**: Relations and Pattern Discovery - Relationship building logic
- **ADR-015**: JSON-LD and Visualization - Network export format
- **[Future ADR]**: Native LM Studio Rerank API Migration

## Notes

- **Model Selection**: BGE-M3 chosen for balance of quality and LM Studio availability
- **Score Range**: Maintains [0.0, 1.0] range compatible with existing edge strength calculations
- **Caching**: DB caching logic unchanged, only model parameter updated to 'bge-m3-emb-proxy'
- **Performance**: Batch processing minimizes API call overhead
- **Migration Path**: Easy reversion by changing import back to lmstudio_client.rerank_pairs
