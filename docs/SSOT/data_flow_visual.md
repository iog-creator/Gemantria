# Visual Data Flow Summary

## High-Level Pipeline Flow

```
Bible Text → Noun Collection → Batch Validation → AI Enrichment → Confidence Check → Network Building → Exports + Reports
     ↓             ↓                ↓                ↓                ↓                ↓                ↓
  Read-Only      Hebrew           Quality          LM Studio        Multi-gate       Embeddings      Multiple
  Database       Extraction       Gates            API Calls        Validation       + Relations     Formats
```

## Data Flow Stages

### 📖 Input Sources

- **Bible Database** (PostgreSQL, read-only): KJV text by verse
- **LM Studio API**: Live Qwen models for AI inference

### 🔄 Processing Pipeline

1. **Collect**: Extract Hebrew nouns, deduplicate, normalize
2. **Validate**: Check batch size (≥50), quality gates
3. **Enrich**: Generate theological insights via AI
4. **Confidence**: Validate AI + gematria confidence scores
5. **Network**: Create embeddings, discover relations, find communities

### 💾 Storage Layer

- **concepts**: Noun metadata and identities
- **concept_network**: 1024-dim embeddings
- **concept_relations**: Similarity edges with scores
- **concept_clusters**: Community detection results
- **concept_centrality**: Node importance measures
- **metrics_log**: Performance and observability data

### 📤 Output Formats

- **Reports**: Markdown/JSON analytics (pipeline health, AI quality)
- **Graph JSON**: WebUI visualization data (nodes, edges, clusters)
- **JSON-LD**: Semantic web standard format
- **RDF/Turtle**: Linked data ontology format
- **Statistics**: Dashboard metrics and health indicators

## Key Quality Gates

| Gate          | Threshold                | Action                       |
| ------------- | ------------------------ | ---------------------------- |
| Qwen Live     | All models responding    | Pipeline abort               |
| Batch Size    | ≥50 nouns                | Abort unless ALLOW_PARTIAL=1 |
| AI Confidence | ≥85% (soft), ≥95% (hard) | Filter out low-confidence    |
| Gematria      | ≥90%                     | Validation failure           |
| Embedding     | 1024-dim, L2 normalized  | Quality check                |
| Relations     | Cosine ≥0.75             | Edge filtering               |

## Data Volume Scaling

For **1000 nouns** → **~50MB total storage**:

- Concepts: ~10KB each
- Embeddings: ~4KB each
- Relations: ~100 bytes each edge
- Full network: ~10k edges

## Performance Timeline

```
Collection:    10 seconds  (~1000/sec)
Validation:     5 seconds  (~200/sec)
Enrichment:    15 minutes  (~1/minute - API limited)
Confidence:     2 seconds  (~500/sec)
Network:       10 seconds  (~100/sec)
Reports:        5 seconds  (post-processing)
TOTAL:         ~16 minutes (API-bound)
```

## Failure Recovery

- **Transactional**: All database writes atomic
- **Checkpointer**: Pipeline state persists across restarts
- **ALLOW_PARTIAL**: Override for incomplete batches
- **Node Isolation**: Individual failures don't stop pipeline
- **Resume Capability**: Continue from last successful checkpoint

This architecture ensures **deterministic processing** with **comprehensive observability** and **graceful error handling**.
