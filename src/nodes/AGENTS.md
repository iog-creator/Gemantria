# AGENTS.md - Pipeline Nodes Directory

## Directory Purpose

The `src/nodes/` directory contains the individual LangGraph node implementations that form the core processing pipeline. Each node represents a discrete step in the gematria analysis workflow, with clear input/output contracts and error handling.

## Key Components

### `enrichment.py` - AI Enrichment Node

**Purpose**: Generate theological insights and confidence scores using Qwen models
**Key Functions**:

- `enrich_noun()` - Process single noun with AI theological analysis
- `process_batch()` - Handle batch processing with rate limiting
- `validate_insights()` - Ensure insight quality and length requirements
  **Requirements**:
- **150-250 word insights** with theological depth
- **Confidence scoring** (0-1) for quality assessment
- **Qwen Live Gate** compliance (never fallback to mocks)
- Comprehensive error handling with partial batch recovery

### `confidence_validator.py` - Confidence Validation Node

**Purpose**: Apply confidence gates and quality thresholds to enriched nouns
**Key Functions**:

- `evaluate_confidence()` - Apply AI confidence soft/hard gates
- `validate_batch_completeness()` - Ensure batch meets quality standards
- `filter_low_confidence()` - Remove nouns below thresholds
  **Requirements**:
- **AI_CONFIDENCE_SOFT** (0.90) - Warning threshold
- **AI_CONFIDENCE_HARD** (0.95) - Failure threshold
- **Batch integrity** maintained through validation
- Detailed logging of confidence distributions

### `network_aggregator.py` - Network Aggregation Node

**Purpose**: Build semantic concept networks with embeddings and relationships
**Key Functions**:

- `build_embeddings()` - Generate 1024-dim Qwen embeddings
- `compute_relations()` - Calculate cosine similarity relationships
- `build_relations()` - KNN + rerank with unified edge strength calculation
- `persist_network()` - Save embeddings and relations to database
  **Requirements**:
- **1024-dim embeddings** with L2 normalization
- **Cosine similarity** for relationship calculation
- **Unified edge strength**: `EDGE_ALPHA*cosine + (1-EDGE_ALPHA)*rerank_score`
- **Strong edges** ≥`EDGE_STRONG`, **weak edges** ≥`EDGE_WEAK`, **candidates** <`EDGE_WEAK`
- **KNN + rerank** relationship discovery with configurable alpha blending
- **All pairs reranked** (not just top-K) with batch processing

### `analysis_runner.py` - Analysis and Export Node

**Purpose**: Run graph analysis operations and export visualization-ready data
**Key Functions**:

- `_export_graph_data()` - Export nodes, edges, and metadata to JSON
- `_export_stats()` - Export graph statistics and metrics
- `_run_temporal_analysis()` - Compute temporal patterns and forecasts
  **Requirements**:
- **Graph export**: Includes nodes, edges, and metadata with hints envelope when available
- **Hints persistence**: Hints from pipeline state included in `graph_latest.json` metadata
- **Schema validation**: Exports validated against JSON schemas when available
- **Temporal analysis**: Time-series patterns and Prophet forecasts exported separately

## Node Architecture

### State Management

Each node receives and returns a `PipelineState` dict containing:

```python
{
    "run_id": str,           # UUID for traceability
    "nouns": List[dict],     # Input noun batch
    "enriched_nouns": List[dict],  # Post-enrichment results
    "network_summary": dict, # Aggregation statistics
    "qwen_health": dict,     # Model health verification
    "hints": List[str],      # Runtime hints collected during execution
    "enveloped_hints": dict  # Hints wrapped in envelope structure for persistence
}
```

### Error Handling Strategy

- **Node-level failures**: Log detailed errors, continue with partial results
- **Critical failures**: Raise exceptions that abort pipeline execution
- **Qwen failures**: Immediate pipeline abort (fail-closed principle)
- **Batch integrity**: Maintain consistency across node transitions

### Performance Considerations

- **Batch processing**: Optimize for external API call efficiency
- **Memory management**: Efficient handling of large embedding arrays
- **Rate limiting**: Respect LM Studio API constraints
- **Parallel processing**: Future-ready for concurrent node execution

## Quality Gates

### Enrichment Quality

- **Insight length**: 150-250 words minimum
- **Theological depth**: Verified by AI confidence scoring
- **Hebrew accuracy**: Cross-referenced with source text
- **Uniqueness**: No duplicate insights within batch

### Network Quality

- **Embedding dimensions**: Exactly 1024 (L2 normalized)
- **Relationship thresholds**: Configurable strong/weak edge cutoffs
- **Cluster coherence**: Validated through centrality measures
- **Semantic accuracy**: Verified against known relationships

## Development Guidelines

### Adding New Nodes

1. **Implement node function** with clear input/output contracts
2. **Add comprehensive error handling** with appropriate logging
3. **Include metrics emission** for observability integration
4. **Update state schema** documentation
5. **Add unit tests** with mocked external dependencies

### Node Testing Strategy

- **Unit tests**: Individual node logic with state mocking
- **Integration tests**: Node interactions and state transitions
- **Performance tests**: Batch processing efficiency
- **Failure tests**: Error handling and recovery scenarios

## Dependencies

- **Core modules**: Hebrew processing utilities
- **Services**: LM Studio client for AI operations
- **Infrastructure**: Database connectivity and metrics
- **External**: NumPy for embedding operations

## Related Documentation

- **Parent**: [AGENTS.md](../AGENTS.md) - Repository overview
- **Graph orchestration**: [../graph/AGENTS.md](../graph/AGENTS.md) - Pipeline coordination
- **Rules**: [.cursor/rules/003-graph-and-batch.mdc](../../.cursor/rules/003-graph-and-batch.mdc)
- **SSOT**: [docs/SSOT/](../../docs/SSOT/) - Node state schemas
