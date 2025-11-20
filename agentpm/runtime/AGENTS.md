# AGENTS.md - agentpm/runtime Directory

## Directory Purpose

The `agentpm/runtime/` directory contains runtime components for LM Studio integration with control-plane logging and AI tracking.

## Key Components

### `lm_studio_chat_with_logging()`

**Purpose:** Wraps LM Studio adapter calls with control-plane logging. Writes to `control.agent_run` when DB is available; graceful no-op when DB is unavailable.

**Location:** `agentpm/runtime/lm_logging.py`

**Function Signature:**
```python
def lm_studio_chat_with_logging(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.0,
    max_tokens: int = 512,
    timeout: float = 30.0,
) -> dict[str, Any]
```

**Parameters:**
- `messages`: List of message dicts with `"role"` and `"content"` keys
- `temperature`: Sampling temperature (default: 0.0)
- `max_tokens`: Maximum tokens to generate (default: 512)
- `timeout`: Request timeout in seconds (default: 30.0)

**Returns:**
Dictionary from `lm_studio_chat()` with same structure:
- `ok`: Boolean indicating if call succeeded
- `mode`: `"lm_on"` or `"lm_off"`
- `reason`: Error reason string or `None`
- `response`: LM Studio response dict or `None`

**Behavior:**
- Calls `lm_studio_chat()` from `agentpm/adapters/lm_studio.py`
- Calculates latency and extracts token counts/response length
- Writes to `control.agent_run` table via `_write_agent_run()` if DB is available
- Records violations in `violations_json` if call fails
- Returns the same result dict as `lm_studio_chat()` (no modification)

**AI Tracking:**
- All calls are logged to `control.agent_run` via `_write_agent_run()` when DB is available
- Logged fields:
  - `tool`: `"lm_studio"` (not `"lm_studio_chat"` - matches the tool identifier)
  - `args_json`: Input parameters (messages, temperature, max_tokens, timeout)
  - `result_json`: Result with latency, usage, response_length, mode (`"lm_on"` or `"lm_off"`)
  - `violations_json`: Error details if call failed (empty list `[]` for successful calls)
- **DB-off behavior**: When DB is unavailable, `_write_agent_run()` returns `None` and the function continues normally (no exceptions raised)
- The LM call result is returned unchanged regardless of logging success/failure

### `guarded_lm_call()`

**Purpose:** Guarded LM Studio call wrapper with call_site tracking and budget enforcement. Respects `LM_STUDIO_ENABLED` flag and budget limits.

**Location:** `agentpm/runtime/lm_logging.py`

**Function Signature:**
```python
def guarded_lm_call(
    call_site: str,
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.0,
    max_tokens: int = 512,
    timeout: float = 30.0,
    fallback_fn: Callable[[list[dict[str, str]], dict[str, Any]], dict[str, Any]] | None = None,
    fallback_kwargs: dict[str, Any] | None = None,
    app_name: str | None = None,
) -> dict[str, Any]
```

**Parameters:**
- `call_site`: Identifier for where this call is made (e.g., `"storymaker.idea_gen"`)
- `messages`: List of message dicts with `"role"` and `"content"` keys
- `temperature`: Sampling temperature (default: 0.0)
- `max_tokens`: Maximum tokens to generate (default: 512)
- `timeout`: Request timeout in seconds (default: 30.0)
- `fallback_fn`: Optional fallback function to call when LM Studio is disabled/unavailable
- `fallback_kwargs`: Optional kwargs to pass to fallback function
- `app_name`: Application identifier for budget tracking (default: derived from `call_site`)

**Returns:**
Dictionary with:
- `ok`: Boolean (True if call succeeded)
- `mode`: `"lm_on"` | `"lm_off"` | `"fallback"` | `"budget_exceeded"`
- `reason`: Error reason string or `None`
- `response`: LM Studio or fallback response dict or `None`
- `call_site`: The call_site identifier

**Behavior:**
- Checks `LM_STUDIO_ENABLED` flag; if disabled, uses fallback or returns `lm_off` mode
- Checks budget limits via `check_lm_budget()`; if exceeded, returns `budget_exceeded` mode
- If enabled and within budget, calls `lm_studio_chat_with_logging()`
- If LM Studio call fails and fallback is available, uses fallback function
- Adds `app_name` and `call_site` to result for observability

**AI Tracking:**
- **Budget exceeded mode**: When budget is exceeded, `_write_agent_run()` is called directly with:
  - `tool`: `"lm_studio"`
  - `args_json`: Contains `call_site`, `app_name`, `messages`, `max_tokens`
  - `result_json`: `{"ok": False, "mode": "budget_exceeded", "reason": "budget_exceeded"}`
  - `violations_json`: `[{"type": "budget_exceeded", "reason": "Budget exceeded for {app_name}"}]`
- **LM Studio enabled mode**: All successful LM Studio calls go through `lm_studio_chat_with_logging()` which logs to `control.agent_run` via `_write_agent_run()`
- **Fallback mode**: When fallback function is used, no additional logging occurs (only the original LM Studio attempt is logged if it was made)
- **DB-off behavior**: All logging attempts gracefully no-op when DB is unavailable (returns `None`, no exceptions)

## API Contracts

### `_write_agent_run()`

**Purpose:** Internal helper to write agent_run row to `control.agent_run` table.

**Function Signature:**
```python
def _write_agent_run(
    tool: str,
    args_json: dict[str, Any],
    result_json: dict[str, Any],
    violations_json: list[dict[str, Any]] | None = None,
) -> str | None
```

**Returns:**
- Run ID (UUID string) if successful
- `None` if DB unavailable or error (non-fatal)

**Behavior:**
- **DB-on mode**: When `get_rw_dsn()` returns a valid DSN and `psycopg` is available:
  - Connects to database and inserts row into `control.agent_run` table
  - Inserts row with `project_id=1` (hardcoded for now)
  - Returns run ID (UUID string) for tracking
  - All exceptions during DB write are caught and return `None` (non-fatal)
- **DB-off mode**: When DSN is unavailable, `psycopg` is missing, or DB write fails:
  - Returns `None` immediately (graceful no-op)
  - Does not raise exceptions (hermetic behavior for CI/offline scenarios)
  - Caller should handle `None` return value gracefully

**AI Tracking Contract (Rule-061/064):**
- This function is the primary writer for `control.agent_run` table from runtime LM calls
- All LM Studio calls via `lm_studio_chat_with_logging()` and `guarded_lm_call()` use this helper
- The table stores:
  - `tool`: Tool identifier (e.g., `"lm_studio"`)
  - `args_json`: Input parameters (messages, temperature, max_tokens, timeout)
  - `result_json`: Result with latency, usage, response_length, mode
  - `violations_json`: Error details if call failed (budget exceeded, connection errors, etc.)
- DB-off behavior ensures CI and hermetic tests can run without database access

## Testing Strategy

**Unit Tests:**
- Test `lm_studio_chat_with_logging()` with mocked `lm_studio_chat()` and `_write_agent_run()`
- Test DB-on and DB-off scenarios
- Test success and failure cases
- Verify control plane logging behavior

**Integration Tests:**
- Test `guarded_lm_call()` with real LM Studio (when available)
- Test budget enforcement and fallback behavior
- Verify call_site tracking

## Development Guidelines

- All functions should gracefully handle DB unavailability (no-op, not failure)
- Use `scripts/config/env.py` helpers for DSN access
- Follow control-plane logging patterns for observability
- Respect `LM_STUDIO_ENABLED` flag and budget limits
- Always include `call_site` for tracking and debugging

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
| `lm_studio_chat_with_logging()` | ADR-066 (LM Studio Control Plane Integration) |
| `guarded_lm_call()` | ADR-066 (LM Studio Control Plane Integration) |
| Control plane logging | ADR-065 (Postgres SSOT) |
