# LM Router Contract (Phase-7C)

**Status**: ✅ COMPLETE (Phase-7C Granite Router)  
**Design Reference**: `Prompting Guide for Our Core LLM models.md`  
**Runtime SSOT**: This document (contract) + `agentpm/lm/router.py` (implementation)

## Purpose

The LM Router provides centralized task classification and model slot selection for language model operations. It maps task characteristics (domain, language, tool requirements) to appropriate model slots and providers based on the Granite 4.0 + BGE-M3 + Granite Reranker stack described in the Prompting Guide.

## Core Responsibilities

1. **Task Classification**: Analyze task metadata to determine the appropriate model slot (theology, math, local_agent, embedding, reranker).
2. **Model Slot Selection**: Choose the correct slot based on task domain and requirements.
3. **Provider Selection**: Respect per-slot provider configuration (Ollama vs LM Studio) without duplicating adapter logic.
4. **Deterministic Behavior**: Same inputs produce the same routing decisions (no randomness in routing logic).

## Router API

### RouterTask

Input structure describing a task that needs an LM operation:

```python
@dataclass
class RouterTask:
    kind: str  # Task type: "chat", "embed", "rerank", "math_verification", "theology_enrichment", etc.
    domain: str | None  # Domain: "theology", "math", "general", "bible", "greek", "hebrew", etc.
    language: str | None  # Language hint: "hebrew", "greek", "english", etc.
    needs_tools: bool  # Whether task requires tool-calling capabilities
    max_tokens: int | None  # Maximum tokens for response (optional)
    temperature: float | None  # Temperature preference (optional, router may override)
```

### RouterDecision

Output structure describing the chosen model and configuration:

```python
@dataclass
class RouterDecision:
    slot: str  # Model slot: "theology", "math", "local_agent", "embedding", "reranker"
    provider: str  # Provider: "ollama" or "lmstudio"
    model_name: str  # Concrete model ID (e.g., "granite4:tiny-h", "christian-bible-expert-v2.0-12b")
    temperature: float  # Recommended temperature (defaults from Prompting Guide)
    extra_params: dict[str, Any]  # Additional parameters (e.g., tool_choice, response_format)
```

### Router Function

```python
def route_task(task: RouterTask) -> RouterDecision:
    """
    Route a task to the appropriate model slot and provider.
    
    Args:
        task: RouterTask describing the operation
        
    Returns:
        RouterDecision with slot, provider, model, and parameters
        
    Raises:
        RuntimeError: If no suitable model is configured or provider is unavailable
    """
```

## Routing Rules (Rule-Based Mapping)

The router uses rule-based mapping (fast path) driven by `RouterTask.kind` and `RouterTask.domain`:

### Slot Selection Rules

- **`kind == "embed"`** → `slot = "embedding"`
- **`kind == "rerank"`** → `slot = "reranker"`
- **`kind == "math_verification"` or `domain == "math"`** → `slot = "math"` (if configured) or fallback to `"local_agent"`
- **`kind == "theology_enrichment"` or `domain == "theology"` or `domain == "bible"`** → `slot = "theology"`
- **`needs_tools == True`** → `slot = "local_agent"` (Granite 4.0 tool-calling)
- **Default** → `slot = "local_agent"` (general fallback)

### Provider Selection

Provider is determined by per-slot environment variables (via `get_lm_model_config()`):
- `THEOLOGY_PROVIDER` → theology slot
- `LOCAL_AGENT_PROVIDER` → local_agent slot
- `EMBEDDING_PROVIDER` → embedding slot
- `RERANKER_PROVIDER` → reranker slot
- Falls back to `INFERENCE_PROVIDER` if slot-specific provider not set

### Model Selection

Model is determined by per-slot environment variables:
- `THEOLOGY_MODEL` → theology slot
- `LOCAL_AGENT_MODEL` → local_agent slot
- `MATH_MODEL` → math slot (optional, falls back to `LOCAL_AGENT_MODEL`)
- `EMBEDDING_MODEL` → embedding slot
- `RERANKER_MODEL` → reranker slot

### Temperature Defaults (from Prompting Guide)

- **Theology tasks**: `0.35` (enrichment) or `0.6` (reasoning)
- **Math tasks**: `0.0` (deterministic verification)
- **General/Agent tasks**: `0.6` (reasoning, default from Prompting Guide)
- **Embedding/Rerank**: N/A (not applicable)

## Guardrails

1. **Determinism**: Same `RouterTask` inputs always produce the same `RouterDecision` (no randomness in routing logic).
2. **Fallback Behavior**: If a specific slot's model is not configured, fall back to `local_agent` slot (if available) or raise `RuntimeError` with a clear message.
3. **Provider Availability**: Router checks provider enable flags (`OLLAMA_ENABLED`, `LM_STUDIO_ENABLED`) and raises `RuntimeError` if the required provider is disabled.
4. **Hermetic Mode**: Router supports a "dry-run" mode that returns static decisions without checking provider availability (for CI/tests).

## Rerank Error-Tolerance Rules

For `kind == "rerank"` tasks, downstream adapters **MUST** implement error-tolerant behavior:

1. **HTTP Errors (4xx/5xx)**: If the provider (Ollama/LM Studio) returns HTTP errors (404, 500, etc.):
   - Adapter raises `OllamaAPIError` with `error_type="http_error"` and `status_code` set
   - Rerank functions catch `OllamaAPIError` and log a HINT-level warning (non-fatal)
   - Fall back to `embedding_only` scoring (deterministic cosine similarity)
   - If `embedding_only` also fails, return equal scores (0.5) for all documents
   - Continue pipeline execution (do not raise exceptions)

2. **Connection Errors & Timeouts**: If the provider is unreachable or times out:
   - Adapter raises `OllamaAPIError` with `error_type="connection_error"` or `"timeout"`
   - Rerank functions catch `OllamaAPIError` and log a HINT-level warning (non-fatal)
   - Fall back to `embedding_only` scoring, then equal scores if that also fails
   - Continue pipeline execution (do not raise exceptions)

3. **JSON Parse Errors**: If the reranker model returns malformed or truncated JSON:
   - Log a HINT-level warning (non-fatal)
   - Fall back to `embedding_only` scoring (deterministic cosine similarity)
   - Continue pipeline execution (do not raise exceptions)

4. **Edge Strength Computation**: Even when fallback occurs:
   - Compute `edge_strength = α*cosine + (1-α)*rerank_score` using available scores
   - If rerank scores are unavailable (fallback to equal scores), use default rerank_score (0.5)
   - Pipeline must not fail due to missing rerank scores
   - `make eval.reclassify` remains valid even when rerank fails (uses available edge_strength values)

5. **Router Decision Stability**: Router decisions remain deterministic regardless of adapter fallback behavior. Fallback is an **adapter concern**, not a routing change. The router continues to route `kind == "rerank"` to the `reranker` slot; adapters handle errors internally.

**Implementation Reference**: 
- `agentpm/adapters/ollama.OllamaAPIError` - Custom exception for HTTP/connection/timeout errors
- `agentpm/adapters/ollama._post_json()` / `_get_json()` - HTTP error handling with `OllamaAPIError` raising
- `agentpm/adapters/ollama._rerank_granite_llm()` - Catches `OllamaAPIError` and falls back to `embedding_only`
- `agentpm/adapters/ollama._rerank_embedding_only()` - Catches `OllamaAPIError` and returns equal scores (0.5)
- `tests/unit/test_ollama_rerank_failures.py` - Comprehensive test coverage for all failure modes

## Integration with Existing Adapters

The router does **not** duplicate HTTP/adapter logic. It produces `RouterDecision` objects that downstream code uses to call existing adapters:

- `agentpm.adapters.lm_studio.chat()` / `embed()` / `rerank()`
- `agentpm.adapters.ollama.chat()` / `embed()` / `rerank()`
- `agentpm.adapters.theology.chat()`

The router is **agnostic** to whether the underlying provider is `lmstudio` or `ollama`; that decision belongs to the adapters and environment configuration.

## Configuration

Router behavior is controlled by environment variables loaded via `scripts.config.env.get_lm_model_config()`:

- **Per-slot providers**: `THEOLOGY_PROVIDER`, `LOCAL_AGENT_PROVIDER`, `EMBEDDING_PROVIDER`, `RERANKER_PROVIDER`
- **Per-slot models**: `THEOLOGY_MODEL`, `LOCAL_AGENT_MODEL`, `MATH_MODEL`, `EMBEDDING_MODEL`, `RERANKER_MODEL`
- **Provider enable flags**: `OLLAMA_ENABLED`, `LM_STUDIO_ENABLED`
- **Router enable flag**: `ROUTER_ENABLED` (default: `1` / enabled; set to `0` to bypass router and use legacy behavior)

## Future Extensions

- **Option B (later)**: Use Granite Tiny-H as a classifier to route tasks dynamically (calls the local_agent model to classify tasks before routing).
- **MoE-of-MoEs**: Support hot-swapping models via Ollama client for expert activation (as described in Prompting Guide).

## Related Documents

- `Prompting Guide for Our Core LLM models.md` - Design-level spec for model stack and prompting
- `AGENTS.md` - Runtime SSOT for model bindings and adapter usage
- `scripts/config/env.py` - Environment configuration loader (`get_lm_model_config()`)
- `agentpm/adapters/lm_studio.py` - LM Studio adapter
- `agentpm/adapters/ollama.py` - Ollama adapter
- `agentpm/adapters/theology.py` - Theology adapter

