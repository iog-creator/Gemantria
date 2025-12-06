# AGENTS.md - pmagent/lm Directory

## Directory Purpose

The `pmagent/lm/` directory contains lm components for the Gematria analysis pipeline.

## Key Components

- `router.py`: LM Router (Phase-7C) - Centralized task classification and model slot selection for language model operations. Maps task characteristics (domain, language, tool requirements) to appropriate model slots and providers based on the Granite 4.0 + BGE-M3 + Granite Reranker stack.
- `lm_status.py`: LM Status Module (Phase-7G) - Introspect LM configuration and local service health.

## API Contracts

### `pmagent.lm.router`

```python
@dataclass
class RouterTask:
    kind: str  # Task type: "chat", "embed", "rerank", "math_verification", "theology_enrichment", etc.
    domain: str | None  # Domain: "theology", "math", "general", "bible", "greek", "hebrew", etc.
    language: str | None  # Language hint: "hebrew", "greek", "english", etc.
    needs_tools: bool  # Whether task requires tool-calling capabilities
    max_tokens: int | None  # Maximum tokens for response (optional)
    temperature: float | None  # Temperature preference (optional, router may override)

@dataclass
class RouterDecision:
    slot: str  # Model slot: "theology", "math", "local_agent", "embedding", "reranker"
    provider: str  # Provider: "ollama" or "lmstudio"
    model_name: str  # Concrete model ID
    temperature: float  # Recommended temperature
    extra_params: dict[str, Any]  # Additional parameters

def route_task(task: RouterTask, config: dict[str, Any] | None = None, dry_run: bool = False) -> RouterDecision:
    """Route a task to the appropriate model slot and provider."""
```

**Router Behavior:**
- Uses rule-based mapping (fast path) driven by `RouterTask.kind` and `RouterTask.domain`
- Slot selection: `kind == "embed"` → `"embedding"`, `kind == "rerank"` → `"reranker"`, `domain == "math"` → `"math"`, `domain == "theology"` → `"theology"`, `needs_tools == True` → `"local_agent"`, default → `"local_agent"`
- Provider selection: Uses per-slot environment variables (`THEOLOGY_PROVIDER`, `LOCAL_AGENT_PROVIDER`, etc.) or falls back to `INFERENCE_PROVIDER`
- Temperature defaults: Theology enrichment (0.35), math (0.0), general/agent (0.6)
- Deterministic: Same inputs produce same outputs
- Hermetic: Supports `dry_run=True` for tests (no provider availability checks)

**Configuration:**
- `ROUTER_ENABLED` (default: `1`) - Enable/disable router (set to `0` to use legacy behavior)
- Per-slot providers: `THEOLOGY_PROVIDER`, `LOCAL_AGENT_PROVIDER`, `EMBEDDING_PROVIDER`, `RERANKER_PROVIDER`
- Per-slot models: `THEOLOGY_MODEL`, `LOCAL_AGENT_MODEL`, `MATH_MODEL`, `EMBEDDING_MODEL`, `RERANKER_MODEL`

**Integration Points:**
- `src/nodes/math_verifier.py` - Math verification uses router when `ROUTER_ENABLED=1`
- `pmagent lm router-status` - CLI command to show router configuration

**See also:** `docs/SSOT/LM_ROUTER_CONTRACT.md` for full contract specification.

## Testing Strategy

<!-- Add testing approach and coverage requirements here -->

## Development Guidelines

<!-- Add coding standards and patterns specific to this directory here -->

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
<!-- Add ADR references here -->
