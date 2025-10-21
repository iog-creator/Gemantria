# ADR-010: Qwen3 Integration for Real Semantic Intelligence

## Status
Accepted

## Context
The semantic aggregation system (ADR-009) was implemented with mock embeddings for development and testing. To activate real semantic intelligence, we need to integrate Qwen3 models through LM Studio for production-quality vector embeddings and relationship validation.

## Decision
Integrate Qwen3-Embedding-0.6B-GGUF and Qwen3-Reranker-0.6B-GGUF models with the following implementation:

1. **Embedding Generation**: Real 1024-dimensional vectors using Qwen3-Embedding-0.6B-GGUF
2. **Batch Processing**: 16-32 text batching for GPU efficiency
3. **Vector Normalization**: L2 normalization for cosine similarity
4. **Reranking**: Qwen3-Reranker-0.6B-GGUF for relationship validation
5. **Configuration**: `USE_QWEN_EMBEDDINGS=true` flag for real vs mock mode
6. **Fallback**: Deterministic mock embeddings when disabled

## Implementation Details

### Architecture Components

#### LM Studio Client Extensions
- **Location**: `src/services/lmstudio_client.py`
- **New Methods**: `get_embeddings()`, `rerank()`
- **Environment Variables**: `USE_QWEN_EMBEDDINGS`, `QWEN_EMBEDDING_MODEL`, `QWEN_RERANKER_MODEL`

#### Network Aggregator Updates
- **Location**: `src/nodes/network_aggregator.py`
- **Enhancement**: Real embedding generation with structured input formatting
- **Batch Processing**: 16-text batches with error handling
- **Storage**: pgvector `VECTOR(1024)` with upsert operations

### Input Formatting

Embeddings generated from structured documents:
```
Document: {noun_name}
Meaning: {hebrew_text}
Reference: Genesis (placeholder)
Gematria: {numeric_value}
Insight: {theological_insight}
```

### Reranking Implementation

- **Query**: Theological theme or relationship question
- **Candidates**: Concept descriptions to validate
- **Prompt Format**: Yes/no classification for relevance
- **Score Mapping**: "yes" → 0.9, "no" → 0.1, unclear → 0.5

### Database Schema

```sql
-- Added in migration 008_add_concept_network_constraints.sql
ALTER TABLE concept_network ADD CONSTRAINT concept_network_concept_id_unique UNIQUE (concept_id);
ALTER TABLE concept_relations ADD CONSTRAINT concept_relations_unique_pair UNIQUE (source_id, target_id);
```

### Configuration

```bash
USE_QWEN_EMBEDDINGS=true          # Enable real embeddings
QWEN_EMBEDDING_MODEL=qwen-embed   # Embedding model name
QWEN_RERANKER_MODEL=qwen-reranker # Reranker model name
LM_STUDIO_HOST=http://127.0.0.1:1234
```

## Consequences

### Positive
- **Real Semantic Intelligence**: Production-quality embeddings instead of mocks
- **GPU Acceleration**: RTX 5070 Ti utilization for batch processing
- **Scalable Architecture**: LM Studio server can handle multiple models
- **Relationship Quality**: Improved concept similarity through real AI understanding
- **Future-Ready**: Reranking foundation for advanced relationship validation

### Negative
- **Dependency on LM Studio**: Requires running LM Studio server
- **GPU Memory Usage**: Models loaded in VRAM (~1.2GB per model)
- **Network Latency**: API calls add processing time vs local mocks
- **Model Loading Time**: Initial model load delays first inference

### Risks
- **Model Availability**: LM Studio server must be running with correct models
- **API Compatibility**: Changes in LM Studio API could break integration
- **Resource Usage**: High GPU utilization during batch processing
- **Fallback Complexity**: Mock vs real mode switching for testing

## Alternatives Considered

### Option 1: Local Model Loading
- **Pro**: No external server dependency, faster inference
- **Con**: Python dependency management, memory constraints, no GPU offloading

### Option 2: Cloud API Integration
- **Pro**: Always available, managed infrastructure
- **Con**: Cost, privacy concerns, network dependency

### Option 3: Hybrid Approach
- **Pro**: Best of both worlds (local for embeddings, cloud for complex tasks)
- **Con**: Architecture complexity, multiple API dependencies

### Option 4: Delayed Integration
- **Pro**: Keep current mock system, defer real AI to later phase
- **Con**: Miss opportunity to validate semantic network with real intelligence

## Testing Strategy

### Unit Tests
- Embedding vector normalization and dimensionality
- Reranking score mapping and error handling
- Mock vs real mode switching
- Batch processing edge cases

### Integration Tests
- Full pipeline with real embeddings enabled
- Database persistence and pgvector operations
- LM Studio API error handling and retries
- Performance benchmarking vs mock mode

### End-to-End Tests
- Genesis batch processing with real Qwen inference
- Report generation with network metrics
- Configuration validation across environments

## Performance Characteristics

### Throughput
- **Mock Mode**: ~1000 embeddings/second (CPU)
- **Real Mode**: ~50-100 embeddings/second (GPU batched)
- **Batch Size**: 16-32 optimal for GPU utilization

### Memory Usage
- **System RAM**: Minimal additional usage
- **GPU VRAM**: ~2.4GB total for both models
- **Database**: ~4KB per embedding vector

### Latency
- **Mock**: <1ms per embedding
- **Real**: 50-200ms per batch (depending on batch size)
- **Network**: Additional 10-50ms for LM Studio API calls

## Future Considerations

### Advanced Reranking
- Multi-turn conversations for complex relationship validation
- Confidence score calibration based on historical accuracy
- Cross-reference validation with multiple models

### Model Optimization
- Quantization for reduced memory footprint
- Model fine-tuning on biblical corpora
- Ensemble approaches combining multiple embedding models

### Scalability
- Distributed LM Studio servers for horizontal scaling
- Embedding caching for repeated concepts
- Incremental embedding updates for evolving concepts

### Monitoring
- Embedding quality metrics and drift detection
- Model performance monitoring and alerting
- GPU utilization and temperature monitoring
