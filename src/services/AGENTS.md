# AGENTS.md — Service Layer Agents

## Purpose
Describes service-level integrations (database + LM Studio) that provide external dependencies for the Gematria pipeline. This document ensures consistent interface contracts and safety policies across all service interactions.

| Service | Function | Related ADRs |
|----------|-----------|--------------|
| db.py | Connection management + pooling | ADR-001 |
| lmstudio_client.py | Qwen3 embedding/rerank client | ADR-010, ADR-015 |
| config.py | Env loader & runtime settings | ADR-002 |

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

### Configuration Service (config.py)
- **Environment Loading**: Validates required variables at startup
- **Type Safety**: Strong typing for all configuration values
- **Production Safety**: ALLOW_MOCKS_FOR_TESTS=0 enforced in production

## Related Documentation

- **Parent**: [AGENTS.md](../AGENTS.md) - Repository overview
- **Rules**: [.cursor/rules/011-production-safety.mdc](../../.cursor/rules/011-production-safety.mdc)
- **SSOT**: [docs/SSOT/](../../docs/SSOT/) - Service contracts
