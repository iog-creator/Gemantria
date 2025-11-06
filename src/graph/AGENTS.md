# AGENTS.md - Graph Orchestration Directory

## Directory Purpose

The `src/graph/` directory contains the main LangGraph pipeline orchestration, execution engine, and batch processing logic. This is the heart of the Gemantria data processing workflow.

## Agent Output Format

**Output shape:** 4 blocks (Goal, Commands, Evidence to return, Next gate)
**SSOT:** Rule 051 — Cursor Insight & Handoff (AlwaysApply)

## Key Components

### `graph.py` - Main Pipeline Engine

**Purpose**: LangGraph pipeline construction, execution, and Qwen health gate enforcement
**Key Functions**:

- `create_graph()` - Build the LangGraph with all nodes and edges
- `run_pipeline()` - Execute pipeline with error handling and observability
- `log_qwen_health()` - Persist Qwen model health checks to database
- `wrap_hints_node()` - Wrap runtime hints into envelope structure for persistence
  **Requirements**:
- **Fail-closed** if Qwen models unavailable (hard stop)
- Comprehensive error handling and logging
- State persistence via checkpointer (Postgres/Memory)
- **Hints envelope**: Runtime hints collected and wrapped in structured envelope for export and validation

### Environment Variables

- `CHECKPOINTER` = `memory` (default) or `postgres` - Choose persistence backend
- `GEMATRIA_DSN` (required when `CHECKPOINTER=postgres`) - PostgreSQL connection string
- `CHECKPOINT_PAYLOAD` = `summary` (default) or `full` - Payload size for checkpoints

### `batch_processor.py` - Batch Processing Logic

**Purpose**: Handle batch semantics, validation, and size management
**Key Functions**:

- `validate_batch_size()` - Ensure batches meet minimum requirements
- `process_batch()` - Execute batch operations with rollback support
- `handle_batch_errors()` - Batch-level error recovery
  **Requirements**:
- Default batch size: 50 nouns
- **ALLOW_PARTIAL=1** override with explicit manifest recording
- Abort on batches < minimum size (unless ALLOW_PARTIAL)

### `patterns.py` - Graph Pattern Discovery (NEW)

**Purpose**: Compute graph patterns, communities, and centrality from concept relations
**Key Functions**:

- `build_graph()` - Construct NetworkX graph from database relations
- `compute_patterns()` - Apply Louvain clustering and centrality algorithms
- `persist_patterns()` - Save clusters and centrality to database tables
  **Requirements**:
- Uses NetworkX for graph algorithms (Louvain communities, degree/betweenness/eigenvector centrality)
- Persists results to `concept_clusters` and `concept_centrality` tables
- Integrates with `analyze_graph.py` script for pattern discovery workflow

## Pipeline Architecture

### Node Sequence

```
collect_nouns → validate_batch → enrichment → confidence_validator → network_aggregator → schema_validator → analysis_runner → wrap_hints
```

Note: When `CHECKPOINTER=postgres`, each node must snapshot via saver; centrality may be persisted after `analysis_runner` (advisory check).

### Relations & Pattern Discovery (NEW)

- **network_aggregator** now builds KNN relations with optional rerank filtering
- **analyze_patterns** (optional node) computes communities and centrality using NetworkX
- Relations persisted to `concept_relations` table with cosine scores and rerank evidence
- Patterns persisted to `concept_clusters` and `concept_centrality` tables

### State Management

- **PipelineState** dict with run_id, nouns, enriched_nouns, network_summary
- **Checkpointer** persists state between runs (Postgres for production)
- **Metadata** includes Qwen health verification and run configuration
- **Hints**: Runtime hints collected in `state.hints` and wrapped in `state.enveloped_hints` for persistence

### Error Handling

- **Node-level**: Individual node failures with detailed logging
- **Pipeline-level**: Qwen health gate failures abort entire pipeline
- **Recovery**: Checkpointer enables resumable execution

## Qwen Health Gate (Production Safety - Always Apply)

### Pre-execution Verification (Fail-Closed)

```python
# Pipeline start - verify ALL required models
required_models = [QWEN_EMBEDDING_MODEL, QWEN_RERANKER_MODEL, THEOLOGY_MODEL]
qwen_health = assert_qwen_live(required_models)
if not qwen_health.ok:
    raise QwenUnavailableError(f"Qwen models unavailable: {qwen_health.reason}")
```

### Health Check Requirements (Critical)

- **Model Availability**: Verify all required Qwen models loaded in LM Studio
- **Embedding Validation**: Test 1024-dim embeddings via `/v1/embeddings` endpoint
- **Reranker Validation**: Test reranker via `/v1/chat/completions` endpoint
- **Latency Measurement**: Capture and log embed/rerank operation times
- **Production Mode**: USE_QWEN_EMBEDDINGS=true required; ALLOW_MOCKS_FOR_TESTS=0

### Fail-Closed Behavior (No Exceptions)

- **QwenUnavailableError**: Hard pipeline abort if any health check fails
- **No Silent Fallback**: Never fallback to mocks in production code
- **Environment Validation**: QWEN_EMBEDDING_MODEL and QWEN_RERANKER_MODEL must match LM Studio loaded models
- **Evidence Requirements**: Undeniable proof of live inference (DB logs + report verification)

### Health Persistence & Auditing

- Results logged to `qwen_health_log` table for production verification
- Latency metrics captured (lat_ms_embed, lat_ms_rerank) for performance monitoring
- Verification status and failure reasons recorded for compliance
- Run_id correlation for traceability across pipeline execution

## Batch Processing Rules

### Size Requirements

- **Minimum**: 50 nouns per batch (configurable)
- **Maximum**: Limited by LM Studio API constraints
- **Partial**: ALLOW_PARTIAL=1 with PARTIAL_REASON in manifest

### Validation Gates

- Hebrew text normalization verification
- Gematria calculation accuracy checks
- Content hash consistency validation

## Development Guidelines

### Adding Pipeline Nodes

1. Implement node function (returns modified state dict)
2. Add to `create_graph()` with proper error handling
3. Update state schema documentation
4. Add metrics emission for observability

### Testing Pipeline Changes

- Unit test individual nodes with mocked state
- Integration test node interactions
- E2E test complete pipeline execution
- Verify checkpointer persistence works

## Performance Considerations

- Batch optimization for external API calls
- Connection pooling for database operations
- Metrics collection with <1% performance overhead
- Memory-efficient state management

## Dependencies

- **LangGraph**: Pipeline orchestration framework
- **psycopg**: Database operations and checkpointer
- **lmstudio_client**: Qwen model health verification
- **Core modules**: Hebrew processing and ID generation
* See .cursor/rules/050-ops-contract.mdc (AlwaysApply).
