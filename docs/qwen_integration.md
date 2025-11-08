# Qwen3 Integration Guide

This document describes the integration of Qwen3 models for embedding generation and rerank-driven relationship refinement in the Gemantria semantic network pipeline.

## Overview

The semantic aggregation system uses two Qwen3 models loaded in LM Studio:

1. **Qwen3-Embedding-0.6B-GGUF**: Generates 1024-dimensional semantic embeddings for concepts
2. **Qwen3-Reranker-0.6B-GGUF**: Provides precision reranking for concept relationship validation

## Rerank-Driven Relationship Refinement

### Architecture

The network aggregator implements a two-stage relationship discovery process:

1. **Recall Stage**: pgvector KNN finds top-k semantically similar concepts using cosine similarity
2. **Precision Stage**: Qwen reranker validates theological relevance and computes final edge strength

### Edge Strength Calculation

```python
edge_strength = 0.5 * cosine_similarity + 0.5 * rerank_score
```

### Relationship Classification

- **Strong Edges**: `edge_strength ≥ 0.90`
- **Weak Edges**: `edge_strength ≥ 0.75`
- **Filtered**: `edge_strength < 0.75` (not stored)

### Rerank Evidence Storage

All relationships include rerank evidence in the database:

```sql
ALTER TABLE concept_relations
ADD COLUMN cosine NUMERIC(6,5),
ADD COLUMN rerank_score NUMERIC(6,5),
ADD COLUMN edge_strength NUMERIC(6,5),
ADD COLUMN rerank_model TEXT,
ADD COLUMN rerank_at TIMESTAMPTZ DEFAULT now();
```

## Configuration

### Environment Variables

```bash
# Enable Qwen embeddings (default: true)
USE_QWEN_EMBEDDINGS=true

# Model names in LM Studio (use exact model IDs from `lms ls`)
EMBEDDING_MODEL=text-embedding-bge-m3
RERANKER_MODEL=qwen.qwen3-reranker-0.6b

# LM Studio connection
LM_STUDIO_HOST=http://localhost:9994

# Rerank-driven relationship configuration
NN_TOPK=20              # KNN neighbors to retrieve for reranking
RERANK_MIN=0.50         # Minimum rerank score to keep candidates
EDGE_STRONG=0.90        # Threshold for strong relationship classification
EDGE_WEAK=0.75          # Threshold for weak relationship classification
```

### Fallback Behavior

The system has multiple fallback mechanisms:

1. **Mock Mode**: When `LM_STUDIO_MOCK=true`, uses deterministic mock embeddings/reranking
2. **Disabled Mode**: When `USE_QWEN_EMBEDDINGS=false`, uses mock embeddings
3. **Connection Failure**: When LM Studio is not available or models not loaded, automatically falls back to mock embeddings with a warning message

This ensures the pipeline can run in development/testing environments without requiring LM Studio setup.

## Embedding Generation

### Input Format

Embeddings are generated from structured documents with the following format:

```
Document: {noun_name}
Meaning: {hebrew_text}
Primary Verse: {primary_verse_reference}
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

Reranking validates concept relationships by assessing theological relevance. For each source concept, KNN neighbors are reranked against the source concept's document to determine if they represent meaningful theological connections.

### Input/Output

- **Query**: Source concept document (used as theological theme)
- **Candidates**: Neighbor concept documents to validate
- **Output**: Relevance scores (0.0-1.0) used in edge strength calculation

### Prompt Format

System prompt:

```
Judge whether the Document meets the requirements based on the Query and the Instruct provided. The answer can only be yes or no.
```

User prompt:

```
<Instruct>: Given a theological theme, identify relevant biblical nouns.
<Query>: {source_concept_document}

<Document>: {candidate_concept_document}
```

### Score Mapping

The reranker supports multiple scoring methods:

1. **Logprob-based scoring** (preferred):

   - Extracts yes/no token log probabilities
   - `score = sigmoid(yes_logprob - no_logprob)`
   - More precise than text parsing

2. **Text parsing fallback**:

   - "yes" → 1.0 (perfect relevance)
   - "no" → 0.0 (no relevance)
   - unclear → 0.5 (neutral)

3. **Batch processing**: Candidates processed in groups of 4-8 to optimize latency

## Testing Examples

### Embedding Test

```python
from services.lmstudio_client import get_lmstudio_client

client = get_lmstudio_client()
texts = [
    """Document: adam
Meaning: אָדָם
Primary Verse: Genesis 1:1
Gematria: 45
Insight: First human created by God""",
    """Document: eve
Meaning: חַוָּה
Primary Verse: Genesis 2:18
Gematria: 19
Insight: Mother of all living, represents life and relationships"""
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

## LM Studio Setup

### Model Loading Commands

**Important**: LM Studio must be running in GUI mode (not headless service) to provide the utility process needed for model loading.

```bash
# 1. Start LM Studio GUI (required for utility process)
DISPLAY=:0 lm-studio &

# 2. Start server on port 9994
lms server start --port 9994

# 3. Models load automatically on first use (dynamic loading)
# Verify available models:
lms ls

# Check loaded models:
lms ps
```

### Hardware Optimization

- **GPU Memory**: 4-bit quantization reduces VRAM requirements  
- **GPU Offload**: Enabled by default when available
- **Concurrent Requests**: Models support parallel inference
- **Batch Processing**: Optimize batch sizes (4-8 for reranking, 16-32 for embeddings)
- **Dynamic Loading**: Models load on-demand when first requested via API

## AI Noun Discovery JSON Prompting Issues

### Problem: AI Returns Natural Language Instead of JSON

**Symptoms:**
- AI noun discovery returns natural language explanations instead of structured JSON
- Pipeline fails with "ai_response_parse_error"
- Nouns discovered = 0

**Root Cause:**
- The theology model (`christian-bible-expert-v2.0-12b`) interprets complex Hebrew text analysis as a natural language task
- Despite strict "Return ONLY JSON" instructions, the model responds with explanatory text

**Solutions:**

1. **Mock Mode Fallback (Recommended for now):**
   ```bash
   export LM_STUDIO_MOCK=true
   # This provides deterministic mock nouns for development/testing
   ```

2. **Alternative Models:**
   - Try `qwen/qwen3-14b` for better structured output (may not support theology tasks)
   - Test different models for JSON extraction vs theological reasoning

3. **Prompt Engineering:**
   - Use simpler, more direct prompts
   - Separate task description from output format
   - Test with minimal Hebrew text samples

### Current Status

- ✅ Mock fallback implemented in `src/nodes/ai_noun_discovery.py`
- ✅ Pipeline works with `LM_STUDIO_MOCK=true`
- 🔄 JSON prompting refinement ongoing

## Troubleshooting

### Common Issues

1. **"Utility process is not defined" Error**

   **Cause**: LM Studio running in headless mode (`--run-as-service`) doesn't spawn the utility process needed for model loading.
   
   **Solution**: Run LM Studio in GUI mode:
   ```bash
   # Kill headless service
   pkill -f "lm-studio.*--run-as-service"
   
   # Start GUI (spawns utility process)
   DISPLAY=:0 /path/to/LM-Studio.AppImage &
   
   # Restart server
   lms server start --port 9994
   ```

2. **Model Not Found Errors**

   - Verify model names match `lms ls` output exactly
   - Update `.env` with correct model IDs: `EMBEDDING_MODEL=text-embedding-bge-m3`, `RERANKER_MODEL=qwen.qwen3-reranker-0.6b`
   - Check GPU memory availability for `--gpu=1.0` flag
   - Confirm LM Studio server is running on correct port

2. **Empty Embeddings Response**

   - Check LM Studio model loading status
   - Verify `/v1/embeddings` endpoint availability
   - Confirm model name matches environment variables

3. **Vector Normalization Issues**

   - Zero-length vectors cause division by zero
   - Fallback to unnormalized vector if norm = 0

4. **Reranking Connection Errors**

   - Verify reranker model is loaded and accessible
   - Check `/v1/chat/completions` endpoint for reranking
   - Confirm `logprobs=True` parameter is supported

5. **Low Rerank Scores**

   - Check prompt formatting matches expected structure
   - Verify system/user message separation
   - Test with simpler queries to isolate issues

6. **Database Migration Errors**
   - Ensure migration `009_rerank_evidence.sql` is applied
   - Check column existence: `cosine`, `rerank_score`, `edge_strength`
   - Verify `pgvector` extension is installed

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
