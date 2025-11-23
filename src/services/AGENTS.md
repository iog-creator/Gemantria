# AGENTS.md — Service Layer Agents

## Directory Purpose

The `src/services/` directory contains service-level integrations (database + LM Studio) that provide external dependencies for the Gematria pipeline. This document ensures consistent interface contracts and safety policies across all service interactions.

## Purpose

Describes service-level integrations (database + LM Studio) that provide external dependencies for the Gematria pipeline. This document ensures consistent interface contracts and safety policies across all service interactions.

## Agent Output Format

**Output shape:** 4 blocks (Goal, Commands, Evidence to return, Next gate)
**SSOT:** Rule 051 — Cursor Insight & Handoff (AlwaysApply)

| Service                  | Function                        | Related ADRs     |
| ------------------------ | ------------------------------- | ---------------- |
| db.py                    | Connection management + pooling | ADR-001          |
| lmstudio_client.py       | Qwen3 embedding/rerank client   | ADR-010, ADR-015 |
| rerank_via_embeddings.py | Bi-encoder rerank proxy         | ADR-026          |
| api_server.py            | Analytics REST API server       | ADR-023, ADR-025 |
| config.py                | Env loader & runtime settings   | ADR-002          |

## Service Contracts

### Database Service (db.py)

- **Read-Only Policy**: bible_db connections enforce SELECT-only operations
- **Connection Pooling**: Configurable pool size and overflow limits
- **Parameterized Queries**: No f-string SQL; banned %s parameterization required

### LM Studio Service (lmstudio_client.py)

- **Qwen Live Gate**: Must call assert_qwen_live() before network aggregation
- **Model Validation**: Embedding models tested with /v1/embeddings; reranker with /v1/chat/completions
- **Health Logging**: All checks logged to qwen_health_log table
- **Fail-Closed**: QwenUnavailableError on any health check failure

### Rerank via Embeddings Service (rerank_via_embeddings.py)

- **Bi-Encoder Proxy**: Computes cosine similarity between BGE-M3 embeddings for concept pairs
- **LM Studio Compatible**: Uses only /v1/embeddings endpoint (no unsupported /v1/rerank)
- **Interface Compatibility**: Drop-in replacement for previous rerank_pairs function
- **Batch Processing**: Efficient embedding of multiple text pairs in minimal API calls
- **Score Range**: Returns similarity scores in [0.0, 1.0] range
- **Error Handling**: Graceful fallback on API failures with logged warnings

#### Production Safety

- **No Mocks**: `USE_MOCKS=1` hard-fails at import for production runs.
- **Environment Separation**: `EMBED_URL` used for embeddings proxy; `LM_STUDIO_HOST` used by `lmstudio_client` health checks (Rule 011). Ensure chat model is accessible at `LM_STUDIO_HOST` for Qwen Live Gate.

### API Server Service (api_server.py)

- **FastAPI Framework**: REST API built on FastAPI with automatic OpenAPI documentation
- **CORS Support**: Cross-origin requests enabled for web UI integration
- **Health Monitoring**: Comprehensive health checks including all export file statuses
- **Endpoint Categories**:
  - **Statistics**: `GET /api/v1/stats` - Graph network statistics
  - **Correlations**: `GET /api/v1/correlations` - Concept relationship data
  - **Patterns**: `GET /api/v1/patterns` - Cross-text pattern correlations
  - **Temporal**: `GET /api/v1/temporal` - Time series pattern analysis (Phase 8)
  - **Forecasting**: `GET /api/v1/forecast` - Predictive pattern modeling (Phase 8)
  - **Network**: `GET /api/v1/network/{concept_id}` - Concept subgraph exploration
  - **Docs Search**: `GET /api/docs/search` - Semantic search over governance/docs (Phase-8D)
  - **Rerank Metrics**: `GET /api/rerank/summary` - Rerank/edge strength metrics summary (nodes, edges, strong/weak edge counts, avg_edge_strength)
- **Filtering & Pagination**: Efficient parameter-based filtering with result limits
- **Error Handling**: Structured error responses with appropriate HTTP status codes

### Configuration Service (config.py)

- **Environment Loading**: Validates required variables at startup
- **Type Safety**: Strong typing for all configuration values
- **Production Safety**: ALLOW_MOCKS_FOR_TESTS=0 enforced in production

## Related Documentation

- **Parent**: [AGENTS.md](../AGENTS.md) - Repository overview
- **Rules**: [.cursor/rules/011-production-safety.mdc](../../.cursor/rules/011-production-safety.mdc)
- **SSOT**: [docs/SSOT/](../../docs/SSOT/) - Service contracts
* See .cursor/rules/050-ops-contract.mdc (AlwaysApply).
