# RFC-080: LM Studio + Control Plane Integration (Phase-3C)

- **Author:** PM (GPT-5 Thinking)
- **Date:** 2025-11-14
- **Status:** In Progress (P0 complete, P1 complete, P2 pending)
- **Ratified by:** [ADR-066](../ADRs/ADR-066-lm-studio-control-plane-integration.md) (2025-11-14)
- **Related:** Rule-050/051/052 (Always-Apply triad), Rule-046 (Hermetic CI Fallbacks), Rule-062 (Environment Validation), Phase-3B (pmagent control-plane health suite), AGENTS.md (LM Studio setup), ADR-007 (LLM Integration), ADR-065 (Postgres SSOT)

## Summary

Integrate LM Studio as a local model backend for the Gemantria pipeline, with health-aware routing through `pmagent` and control-plane observability. LM Studio provides low-latency, cost-effective, offline-capable LLM inference. The control-plane serves as the source of truth for LM usage tracking, enabling `pmagent control summary` and `pmagent control pipeline-status` to reflect real LM Studio traffic. This integration maintains hermetic DB-off behavior and does not change STRICT/HINT posture.

## Motivation

### Why LM Studio?

- **Latency**: Local inference eliminates network round-trips, reducing LLM call latency from seconds to milliseconds for local models.
- **Cost**: No per-token API costs; runs on local hardware (GPU/CPU).
- **Offline capability**: Works without internet connectivity, enabling development and testing in isolated environments.
- **Privacy**: Data never leaves the local machine, important for sensitive theological content.

### Why Control-Plane Integration?

- **Observability**: Track LM Studio usage patterns, success/failure rates, and model performance through existing `pmagent control` commands.
- **Health-aware routing**: Use `pmagent health lm` and `pmagent control summary` to determine when LM Studio is eligible vs. when to fall back to remote LLMs.
- **Consistency**: All LLM calls (local or remote) should be logged to the control-plane for unified monitoring and debugging.

## Proposal

### 1. LM Studio Configuration

#### Environment-Driven Configuration

- **Base URL**: `LM_STUDIO_BASE_URL` (default: `http://localhost:1234/v1`)
- **Model**: `LM_STUDIO_MODEL` (default: unset, must be explicitly configured)
- **Timeout**: `LM_STUDIO_TIMEOUT_SECONDS` (default: `30`)
- **Health Check Endpoint**: `LM_STUDIO_HEALTH_ENDPOINT` (default: `/health`)

#### Centralized Loader

- Create `scripts/config/lm_studio.py` (similar to `scripts/config/env.py` for DSNs):
  - `get_lm_studio_base_url() -> str | None`
  - `get_lm_studio_model() -> str | None`
  - `get_lm_studio_timeout() -> int`
  - All functions use centralized env loading; **no direct `os.environ` calls** in adapter code.

#### Configuration Validation

- `pmagent health lm` validates:
  - Base URL is reachable (HTTP GET to `/health` or `/v1/models`)
  - Model is available (if `LM_STUDIO_MODEL` is set, verify it's in the model list)
  - Response time is acceptable (< 5s for health check)

### 2. Health + Routing

#### Pre-Flight Health Checks

- **Before LM Studio calls**: Run `pmagent health lm` (or equivalent programmatic check) to verify:
  - LM Studio server is running
  - Model is loaded (if `LM_STUDIO_MODEL` is set)
  - Response time is acceptable

#### Routing Rules

- **Eligible for LM Studio**:
  - `pmagent health lm` returns `ok=true` and `mode=lm_ready`
  - `LM_STUDIO_MODEL` is set and matches an available model
  - Health check latency < 5s

- **Fallback to remote LLMs**:
  - LM Studio health check fails
  - `LM_STUDIO_MODEL` is not set
  - Health check latency > 5s
  - Explicit `USE_LM_STUDIO=0` override

#### Integration Points

- Existing `pmagent health lm` command (Phase-3B Feature #4) already checks LM Studio health.
- `pmagent control summary` aggregates health status, enabling routing decisions at the orchestration level.

### 3. Control-Plane Logging

#### Database Integration

- **When DB is ON**: LM Studio-backed calls write rows to:
  - `control.agent_run` (tool: `lm_studio`, args_json: `{model, prompt_length, ...}`, result_json: `{response_length, latency_ms, ...}`)
  - Related tables as needed (e.g., `control.tool_catalog` for model metadata)

- **When DB is OFF**: Behavior remains hermetic:
  - No crashes or unhandled exceptions
  - LM Studio calls still work (local inference doesn't require DB)
  - Logging is skipped gracefully (no-op)

#### Logging Model

- **Tool name**: `lm_studio` (consistent identifier for all LM Studio calls)
- **Args JSON**: `{model: str, prompt_length: int, temperature: float, max_tokens: int, ...}`
- **Result JSON**: `{response_length: int, latency_ms: int, tokens_per_second: float, ...}`
- **Violations JSON**: `[]` (empty) for successful calls; error details for failures

#### Observability

- `pmagent control pipeline-status` shows LM Studio usage:
  - Pipeline name: `lm_studio`
  - Success/failure counts
  - Last run timestamp and status

- `pmagent control summary` aggregates LM Studio health and usage across all components.

### 4. CLI and Adapter Boundaries

#### LM Studio Adapter Module

- **Location**: `agentpm/adapters/lm_studio.py`
- **Responsibilities** (ONLY):
  - Building HTTP requests to LM Studio API (OpenAI-compatible format)
  - Parsing responses (JSON extraction, error handling)
  - Mapping errors (LM Studio errors → standardized error types)
  - Health check implementation (ping endpoint, model list)

- **NOT responsible for**:
  - Routing decisions (handled by orchestration layer)
  - Control-plane logging (handled by logging layer)
  - Configuration loading (handled by centralized loader)

#### Adapter Interface

```python
def lm_studio_complete(
    prompt: str,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> dict[str, Any]:
    """
    Complete a prompt using LM Studio.
    
    Returns:
        {
            "ok": bool,
            "response": str | None,
            "error": str | None,
            "metadata": {
                "model": str,
                "latency_ms": int,
                "tokens_per_second": float,
                ...
            }
        }
    """
    ...

def lm_studio_health() -> dict[str, Any]:
    """
    Check LM Studio health.
    
    Returns:
        {
            "ok": bool,
            "mode": "lm_ready" | "lm_off" | "error",
            "details": {...}
        }
    """
    ...
```

#### Integration with pmagent

- `pmagent health lm` calls `lm_studio_health()` from the adapter.
- Orchestration code (e.g., `scripts/agents/enrich_nouns.py`) calls `lm_studio_complete()` when routing to LM Studio.
- Control-plane logging wraps adapter calls to record usage.

### 5. Safety & Governance

#### Database Contracts

- **No change to bible_db read-only contract**: LM Studio integration does not touch `BIBLE_DB_DSN` or bible_db schema.
- **No new DSNs**: LM Studio configuration is separate from database DSNs (uses `LM_STUDIO_*` env vars, not DSNs).

#### Environment Variable Management

- **All new env usage must go through centralized loaders**: No direct `os.environ` calls in adapter or orchestration code.
- **Validation**: Centralized loaders validate env vars and provide sensible defaults where appropriate.

#### Hermetic Behavior

- **DB-off tolerance**: All control-plane logging must gracefully handle DB unavailability:
  - No crashes or unhandled exceptions
  - LM Studio calls still work (local inference is independent of DB)
  - Logging is skipped (no-op) when DB is unavailable

#### Governance Rules

- **Rule-046 (Hermetic CI Fallbacks)**: LM Studio adapter must work in CI environments where DB is unavailable.
- **Rule-050/051/052 (Always-Apply triad)**: All new code must follow OPS contract, CI gating, and tool-priority rules.
- **Rule-062 (Environment Validation)**: Centralized env loading ensures consistent validation across all components.

## Scope

### In-Scope

- **Adapter design**: LM Studio adapter module with health check and completion interfaces.
- **Config & env knobs**: Centralized loader for LM Studio configuration (base URL, model, timeout).
- **Health/routing rules**: Pre-flight health checks and routing logic (LM Studio vs. remote LLMs).
- **Control-plane logging model**: Integration with `control.agent_run` and related tables for observability.
- **CLI integration**: `pmagent health lm` enhancement (if needed) and `pmagent control` visibility of LM Studio usage.

### Out-of-Scope (Future RFCs)

- **Advanced prompt routing**: Multi-model selection, A/B testing, model-specific routing rules.
- **Atlas UI tiles**: Specific Atlas dashboard tiles for LM Studio metrics (covered by existing `pmagent control summary` integration).
- **Model management**: Automatic model downloading, versioning, or switching.
- **Guarded Tool Calls wiring**: Integration with guarded tool calls system (separate RFC/plan).

## Acceptance Criteria

- [x] RFC reviewed and accepted by PM.
- [x] MASTER_PLAN updated to reference Phase-3C (LM Studio + Control Plane Integration).
- [x] Clear list of concrete PRs (≤5) to implement the integration:
  1. **P0**: ✅ **COMPLETE** - LM Studio adapter module (`agentpm/adapters/lm_studio.py`) + centralized config loader (`scripts/config/env.py`) - [PR #532](https://github.com/iog-creator/Gemantria/pull/532)
  2. **P0**: ✅ **COMPLETE** - Health check integration with `pmagent health lm` (uses LM Studio adapter) - [PR #532](https://github.com/iog-creator/Gemantria/pull/532)
  3. **P1**: ✅ **COMPLETE** - Control-plane logging integration (`agentpm/runtime/lm_logging.py` wraps adapter calls to write to `control.agent_run`) - [PR #532](https://github.com/iog-creator/Gemantria/pull/532)
  4. **P1**: Routing logic (pre-flight health checks, fallback to remote LLMs)
  5. **P2**: Documentation (runbook for LM Studio setup, troubleshooting guide)

## QA Checklist

- [x] **Hermetic DB-off story preserved**: All control-plane logging gracefully handles DB unavailability; LM Studio calls work without DB. ✅ Verified in `test_lm_logging_db_off` and `test_lm_logging_no_dsn`
- [x] **No direct `os.environ` in new code**: All env var access goes through centralized loaders (`scripts/config/env.py`). ✅ Verified in PR #532
- [ ] **Control-plane tables unchanged**: No schema changes to `control.agent_run` or related tables (uses existing structure).
- [ ] **Health checks work**: `pmagent health lm` correctly detects LM Studio availability and model readiness.
- [ ] **Routing works**: Orchestration code correctly routes to LM Studio when eligible, falls back to remote LLMs when not.
- [ ] **Observability works**: `pmagent control pipeline-status` and `pmagent control summary` show LM Studio usage when DB is available.

## Implementation Notes

### Phase-3C PR Sequence

1. **PR #532 (P0)**: ✅ **COMPLETE** - Adapter + Config
   - ✅ Created `agentpm/adapters/lm_studio.py` with `lm_studio_chat()` and hermetic `lm_off` fallback
   - ✅ Added `get_lm_studio_settings()` to `scripts/config/env.py` (centralized env loader)
   - ✅ Created `agentpm/runtime/lm_routing.py` with `select_lm_backend()` helper
   - ✅ Added tests for adapter (12/12 passing, all hermetic with mocked HTTP)
   - ✅ Added tests for routing helper (4/4 passing)
   - **Merged**: 2025-11-14 (commit `99e6116e`)

2. **PR #2 (P0)**: ✅ **COMPLETE** - Health Check Integration
   - ✅ Enhanced `pmagent health lm` to use LM Studio adapter (`scripts/guards/guard_lm_health.py`)
   - ✅ Health check uses `lm_studio_chat()` from adapter
   - ✅ Updated tests to use adapter mocks
   - **Merged**: 2025-11-14 (commit `99e6116e` - same PR as P0)

3. **PR #3 (P1)**: ✅ **COMPLETE** - Control-Plane Logging
   - ✅ Created `agentpm/runtime/lm_logging.py` with `lm_studio_chat_with_logging()` wrapper
   - ✅ Writes to `control.agent_run` when DB is available (tool: `lm_studio`)
   - ✅ Graceful no-op when DB is unavailable (hermetic DB-off behavior)
   - ✅ Added tests for logging (DB-on and DB-off scenarios) - `agentpm/tests/runtime/test_lm_logging.py`
   - **Merged**: 2025-11-14 (commit `99e6116e` - same PR as P0)

4. **PR #4 (P1)**: Routing Logic
   - Add routing helper (check health, decide LM Studio vs. remote)
   - Integrate routing into orchestration code (e.g., `enrich_nouns.py`)
   - Add tests for routing (eligible, fallback scenarios)

5. **PR #5 (P2)**: Documentation
   - Create runbook: `docs/runbooks/LM_STUDIO_SETUP.md`
   - Update `AGENTS.md` with LM Studio integration details
   - Add troubleshooting guide for common issues

### Testing Strategy

- **Unit tests**: Adapter, config loader, routing logic (all mocked)
- **Integration tests**: Health check, control-plane logging (DB-on and DB-off)
- **Hermetic tests**: Verify DB-off behavior (no crashes, graceful degradation)
- **Smoke tests**: `make lm_studio.smoke` (requires LM Studio running locally)

### Migration Path

- **Backward compatible**: Existing remote LLM calls continue to work unchanged.
- **Opt-in**: LM Studio is only used when `LM_STUDIO_MODEL` is set and health check passes.
- **Gradual rollout**: Can be enabled per-component (e.g., enrichment only) before full pipeline integration.

