# Qwen3 Integration Guide

This document describes the integration of Qwen3 models for embedding generation and reranking in the Gemantria semantic network pipeline.

## Overview

The semantic aggregation system uses two Qwen3 models loaded in LM Studio:

1. **Qwen3-Embedding-0.6B-GGUF**: Generates 1024-dimensional semantic embeddings
2. **Qwen3-Reranker-0.6B-GGUF**: Reranks concept relationships for relevance

## Configuration

### Environment Variables

```bash
# Enable Qwen embeddings (default: true)
USE_QWEN_EMBEDDINGS=true

# Model names in LM Studio
QWEN_EMBEDDING_MODEL=qwen-embed
QWEN_RERANKER_MODEL=qwen-reranker

# LM Studio connection
LM_STUDIO_HOST=http://localhost:1234
```

### Fallback Behavior

When `USE_QWEN_EMBEDDINGS=false` or `LM_STUDIO_MOCK=true`, the system uses deterministic mock embeddings for testing and development.

## Embedding Generation

### Input Format

Embeddings are generated from structured documents with the following format:

```
Document: {noun_name}
Meaning: {hebrew_text}
Reference: Genesis (placeholder)
Gematria: {numeric_value}
Insight: {theological_insight}
```

### Processing Pipeline

1. **Text Formatting**: Convert noun data to structured document format
2. **Batch Processing**: Group 16-32 documents per LM Studio request
3. **Embedding Generation**: Call `/v1/embeddings` endpoint
4. **Normalization**: Apply L2 normalization to ensure unit vectors
5. **Storage**: Persist normalized vectors in `concept_network` table

### Vector Properties

- **Dimensions**: 1024
- **Normalization**: L2 normalized (unit vectors)
- **Storage**: pgvector `VECTOR(1024)` format
- **Similarity**: Cosine similarity between normalized vectors

## Reranking

### Use Case

Reranking provides a secondary validation layer for concept relationships, scoring how well candidate concepts match a theological query or theme.

### Input/Output

- **Query**: Theological theme or question
- **Candidates**: List of concept descriptions to score
- **Output**: Relevance scores (0.0-1.0) for each candidate

### Prompt Format

```
<Instruct>: Given a theological theme, identify relevant biblical nouns.

<Query>: {query}

<Document>: {candidate}

Respond with only "yes" or "no" indicating if this document is relevant to the query.
```

### Score Mapping

- "yes" → 0.9 (high relevance)
- "no" → 0.1 (low relevance)
- unclear responses → 0.5 (neutral)

## Testing Examples

### Embedding Test

```python
from services.lmstudio_client import get_lmstudio_client

client = get_lmstudio_client()
texts = [
    "Document: adam\nMeaning: אָדָם\nReference: Genesis\nGematria: 45\nInsight: First human created by God",
    "Document: hevel\nMeaning: הֶבֶל\nReference: Genesis\nGematria: 37\nInsight: Meaningless pursuits without God"
]

embeddings = client.get_embeddings(texts)
print(f"Generated {len(embeddings)} embeddings, each {len(embeddings[0])} dimensions")
```

### Reranking Test

```python
from services.lmstudio_client import get_lmstudio_client

client = get_lmstudio_client()
query = "concepts related to human nature and creation"
candidates = [
    "adam - first human, created from dust, given divine breath",
    "hevel - vanity, meaningless pursuits apart from God",
    "sin - rebellion against divine will"
]

scores = client.rerank(query, candidates)
for candidate, score in zip(candidates, scores):
    print(f"{candidate}: {score:.2f}")
```

## Performance Considerations

### Hardware Requirements

- **GPU**: RTX 5070 Ti recommended for optimal performance
- **RAM**: 8GB+ system RAM for model loading
- **Storage**: ~4KB per concept embedding

### Batch Optimization

- **Embedding Batch Size**: 16-32 texts per request (balance latency vs throughput)
- **Request Parallelization**: Multiple concurrent requests supported
- **Rate Limiting**: Respect LM Studio's concurrent request limits

### Index Performance

pgvector indexes optimize similarity searches:
- `ivfflat` index with `vector_cosine_ops`
- `lists = 100` parameter for index tuning

## Troubleshooting

### Common Issues

1. **Empty Embeddings Response**
   - Check LM Studio model loading
   - Verify `/v1/embeddings` endpoint availability
   - Confirm model name matches LM Studio configuration

2. **Vector Normalization Issues**
   - Zero-length vectors cause division by zero
   - Fallback to unnormalized vector if norm = 0

3. **Reranking Parse Errors**
   - Model may return unexpected responses
   - Fallback score of 0.5 for unparseable responses

### Debug Mode

Set `LOG_LEVEL=DEBUG` to see detailed embedding generation and API call logs.

## Future Extensions

### Advanced Reranking

- Multi-turn reranking conversations
- Confidence score calibration
- Cross-reference validation

### Embedding Fine-tuning

- Domain-specific fine-tuning on biblical texts
- Multi-modal embeddings (text + numerical patterns)
- Temporal embedding evolution

### Graph Analytics

- Community detection using embedding clusters
- Path finding with semantic similarity
- Visualization of embedding space
