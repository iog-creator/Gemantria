# AGENTS.md - agentpm/adapters Directory

## Directory Purpose

The `agentpm/adapters/` directory contains adapter components that bridge external services and data sources with the Gematria analysis pipeline. Adapters handle protocol translation, error handling, and hermetic fallbacks.

## Key Components

### MCP Database Adapter (`mcp_db.py`)

Provides read-only access to MCP (Model Context Protocol) catalog data stored in PostgreSQL.

**Purpose**: Enables guarded tool calls to query MCP catalog entries when available, with graceful degradation when database/view is unavailable.

**Key Functions**:
- `catalog_read_ro()` - Reads MCP catalog entries from `mcp.v_catalog` view

**Error Handling**: Returns structured error information when DSN/view unavailable, never throws exceptions.

### Ollama Adapter (`ollama.py`)

Provides adapter for Ollama API (chat, embeddings, reranking) with error-tolerant fallback behavior.

**Purpose**: Bridges Ollama API calls with the Gematria pipeline, providing hermetic fallbacks and error tolerance.

**Key Functions**:
- `chat()` - Chat completions via Ollama API
- `embed()` - Text embeddings via Ollama API
- `rerank()` - Document reranking with Granite LLM or embedding-only fallback
- `_rerank_granite_llm()` - Granite LLM-based reranking with structured JSON prompts

**Granite Reranker Configuration**:
- **Document Truncation**: `MAX_DOC_CHARS=1024` - Each candidate document truncated to stay within ~8K token envelope
- **Generation Limit**: `GRANITE_RERANK_NUM_PREDICT=4096` (default) - Sets `num_predict` for sufficient generation tokens
- **JSON-Only Contract**: Model must return `[{"index": 1, "score": 0.95}, ...]` format only
- **Error-Tolerant Fallback**: On JSON parse errors or HTTP errors, logs HINT and falls back to `embedding_only` scoring (non-fatal)

**Error Handling**: All rerank errors are non-fatal; pipeline continues with embedding-only scores when Granite rerank fails.

### Theology Adapter (`theology.py`)

Provides adapter for Christian-Bible-Expert-v2.0-12B model via LM Studio or Ollama.

**Purpose**: Dedicated adapter for theology model, separate from LM Studio critical path. Supports local-only providers (no internet).

**Key Functions**:
- `chat(prompt: str, *, system: str | None = None, model: str | None = None) -> str` - Chat with theology model

**Configuration**:
- **Port Default**: Uses config's `base_url` default (typically port 9994), not hardcoded values
- **Provider Selection**: `THEOLOGY_PROVIDER=lmstudio|ollama` (default: `lmstudio`)
- **Base URL**: `THEOLOGY_LMSTUDIO_BASE_URL` (defaults to `base_url` from config, typically `http://127.0.0.1:9994/v1`)
- **Model**: `THEOLOGY_MODEL=Christian-Bible-Expert-v2.0-12B`

**Error Handling**: Raises `RuntimeError` if model not configured or provider unavailable (fail-closed, no fallbacks).

**Security**: Enforces localhost-only connections (127.0.0.1 or localhost).

## API Contracts

### `catalog_read_ro() -> dict[str, Any]`

```python
def catalog_read_ro() -> dict[str, Any]:
    """Read MCP catalog entries from database.

    Returns:
        {
            "ok": bool,           # True if catalog accessible
            "tools": List[dict],  # Tool definitions from catalog
            "error": str | None   # Error message if ok=False
        }
    """
```

**Hermetic Behavior**: Always returns a valid dict, never throws exceptions. Safe to call without database connectivity.

## Testing Strategy

- Unit tests with mocked database connections
- Integration tests that skip when DSN unavailable
- Coverage ≥98% including error paths

## Development Guidelines

- All adapters must be hermetic (work without external dependencies)
- Return structured error information, never throw exceptions
- Use centralized DSN loaders (`scripts.config.env`)
- Include comprehensive type hints

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
| `catalog_read_ro()` | ADR-066 (LM Studio Control Plane Integration) |
| MCP adapters | PLAN-091 (Guarded Tool Calls P0 Execution) |
