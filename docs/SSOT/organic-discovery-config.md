# Organic AI Discovery Configuration

## Overview

The Gemantria system uses organic AI-driven noun discovery that removes artificial limits and allows the AI to determine when comprehensive analysis is complete. This configuration document outlines the parameters and algorithms used.

## Discovery Algorithm

### 1. Word Extraction Phase
- **Source**: Bible database via `get_bible_ro()`
- **Query**: Extract top 500 most frequent Hebrew words with frequencies
- **Cleaning**: Remove morphological markers (dagesh, vowels, prefixes)
- **Filtering**: Only Hebrew words (א-ת) with length ≥ 2

### 2. Chunk Processing Phase
- **Chunk Size**: 15,000 characters
- **Overlap**: 1,000 characters (ensures continuity)
- **Total Chunks**: ~15 for Genesis (200k characters)
- **Processing**: Sequential chunk analysis

### 3. AI Analysis Phase
- **Model**: christian-bible-expert-v2.0-12b
- **Temperature**: 0.5 (creative yet focused)
- **Prompt Strategy**: Comprehensive noun extraction with examples
- **Response Format**: Strict JSON validation

### 4. Organic Stopping
- **Mechanism**: Track consecutive chunks yielding no new nouns
- **Threshold**: 5 consecutive empty chunks = completion
- **Fallback**: Continue processing all chunks if AI finds nouns

## Configuration Parameters

### Environment Variables

```bash
# Discovery Limits (Organic - AI determines completion)
MAX_AI_CALLS_PER_RUN=2000      # High ceiling for comprehensive discovery
MAX_LATENCY_P95_MS=60000       # 60s for thoughtful analysis

# Database Connections
BIBLE_DB_DSN=postgresql://mccoy@/bible_db?host=/var/run/postgresql
GEMATRIA_DSN=postgresql://mccoy@/gematria?host=/var/run/postgresql

# AI Model Configuration
THEOLOGY_MODEL=christian-bible-expert-v2.0-12b
EMBEDDING_MODEL=text-embedding-bge-m3
RERANKER_MODEL=qwen.qwen3-reranker-0.6b
```

### Algorithm Constants

```python
# Word extraction
MAX_WORDS = 500              # Top frequent words to analyze
MIN_WORD_LENGTH = 2          # Filter very short words

# Chunking
CHUNK_SIZE = 15000           # Characters per chunk
CHUNK_OVERLAP = 1000         # Overlap between chunks

# Organic stopping
MAX_CONSECUTIVE_EMPTY = 5    # Chunks without new nouns = done
MAX_AI_CALLS = 2000          # Hard ceiling (rarely hit)
MAX_LATENCY_MS = 60000       # Per-call timeout
```

## Quality Gates

### Input Validation
- Database connectivity verified before extraction
- Hebrew text encoding validated
- Word frequency calculations accurate

### Output Validation
- JSON schema compliance (SSOT_ai-nouns.v1.schema.json)
- Canonical noun shape via noun_adapter.py
- Theological analysis completeness
- Gematria calculation accuracy

### Performance Gates
- P95 latency monitoring (<60s per call)
- Call count tracking (organic completion preferred)
- Memory usage bounds (chunk processing)

## Expected Outputs

### Genesis Discovery Results
- **Nouns Discovered**: 10 significant theological nouns
- **Coverage**: Patriarchs, covenants, divine names, theological concepts
- **Quality**: Each noun includes gematria, classification, theological analysis
- **Uniqueness**: No duplicates across chunks

### Example Output Structure

```json
{
  "schema": "gemantria/ai-nouns.v1",
  "book": "Genesis",
  "generated_at": "2025-11-05T10:17:15Z",
  "nodes": [
    {
      "noun_id": "ai-genesis-123456789",
      "surface": "אברהם",
      "hebrew_text": "אברהם",
      "letters": ["א", "ב", "ר", "ה", "ם"],
      "gematria_value": 248,
      "class": "person",
      "analysis": {
        "meaning": "Father of many nations",
        "freq": 45
      }
    }
  ]
}
```

## Monitoring & Observability

### Logs Tracked
- `word_frequencies_extracted`: Database extraction success
- `chunk_processed`: Per-chunk progress (nouns found, consecutive empty count)
- `organic_stopping`: AI-determined completion
- `discovery_complete`: Final statistics

### Metrics Collected
- Words extracted from database
- Chunks processed vs total
- Nouns discovered per chunk
- AI call latency percentiles
- Consecutive empty chunk tracking

## Failure Modes & Recovery

### Database Connection Issues
- **Detection**: Connection timeout or query failure
- **Recovery**: Fail fast with clear error message
- **Prevention**: DSN validation on startup

### AI Response Issues
- **Detection**: Invalid JSON, empty responses, timeouts
- **Recovery**: Retry logic with exponential backoff
- **Prevention**: Strict prompt engineering and validation

### Memory/Resource Issues
- **Detection**: Chunk processing failures, OOM errors
- **Recovery**: Reduce chunk size, increase overlap
- **Prevention**: Resource monitoring and limits

## Future Enhancements

### Multi-Book Processing
- Parallel processing across books
- Cross-book noun deduplication
- Incremental discovery (resume from checkpoints)

### Advanced AI Techniques
- Few-shot learning with examples
- Chain-of-thought reasoning
- Multi-turn conversations for complex nouns

### Performance Optimizations
- Batch processing of chunks
- Caching of word frequencies
- Distributed AI inference
