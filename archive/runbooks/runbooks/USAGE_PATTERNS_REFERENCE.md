# LM Studio & Database Usage Patterns Reference

**Purpose**: Quick reference guide for correct usage of LM Studio and databases in the Gemantria codebase.

**Last Updated**: 2025-11-15

## Table of Contents

1. [Database Connection Patterns](#database-connection-patterns)
2. [LM Studio Configuration](#lm-studio-configuration)
3. [LM Studio Usage in Code](#lm-studio-usage-in-code)
4. [Common Patterns](#common-patterns)
5. [Anti-Patterns (What NOT to Do)](#anti-patterns-what-not-to-do)

---

## Database Connection Patterns

### ✅ CORRECT: Use Centralized DSN Loaders

**Always use centralized loaders from `scripts/config/env.py`:**

```python
from scripts.config.env import get_rw_dsn, get_ro_dsn, get_bible_db_dsn

# For read-write operations (GEMATRIA_DSN)
dsn = get_rw_dsn()
if not dsn:
    raise RuntimeError("GEMATRIA_DSN not configured")

# For read-only operations (GEMATRIA_RO_DSN or ATLAS_DSN_RO)
dsn = get_ro_dsn()
if not dsn:
    raise RuntimeError("RO DSN not configured")

# For Bible database (read-only)
dsn = get_bible_db_dsn()
if not dsn:
    raise RuntimeError("BIBLE_DB_DSN not configured")
```

### DSN Precedence

**Read-Write DSN** (`get_rw_dsn()`):
1. `GEMATRIA_DSN` (primary)
2. `RW_DSN`
3. `AI_AUTOMATION_DSN`
4. `ATLAS_DSN_RW`
5. `ATLAS_DSN` (fallback)

**Read-Only DSN** (`get_ro_dsn()`):
1. `GEMATRIA_RO_DSN` (peer primary)
2. `ATLAS_DSN_RO` (peer primary)
3. `ATLAS_DSN` (fallback)
4. `get_rw_dsn()` (last resort)

**Bible DB DSN** (`get_bible_db_dsn()`):
1. `BIBLE_DB_DSN` (primary)
2. `BIBLE_RO_DSN`
3. `RO_DSN`
4. `ATLAS_DSN_RO`
5. `ATLAS_DSN` (fallback)

### ❌ WRONG: Direct Environment Variable Access

**Never do this:**
```python
import os

# ❌ WRONG - Bypasses centralized loader
dsn = os.getenv("GEMATRIA_DSN")
```

**Why**: Centralized loaders handle precedence, fallbacks, and validation. Direct `os.getenv()` bypasses this logic.

### Database Connection Examples

**Using psycopg (direct connection):**
```python
from scripts.config.env import get_rw_dsn
import psycopg

dsn = get_rw_dsn()
if not dsn:
    raise RuntimeError("DSN not configured")

with psycopg.connect(dsn) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM gematria.nodes")
        count = cur.fetchone()[0]
```

**Using SQLAlchemy (engine):**
```python
from pmagent.db.loader import get_control_engine
from sqlalchemy import text

engine = get_control_engine()
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM gematria.nodes"))
    count = result.scalar()
```

**Using connection pool:**
```python
from scripts.db.pool import get_pool

pool = get_pool()
with pool.connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM gematria.nodes")
        count = cur.fetchone()[0]
```

---

## LM Studio Configuration

### ✅ CORRECT: Environment Variables

**Required variables in `.env` or `.env.local`:**

```bash
# Master switch (must be explicitly enabled)
LM_STUDIO_ENABLED=1

# Base URL (must include /v1)
LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1

# Model name (must match loaded model in LM Studio)
LM_STUDIO_MODEL=christian-bible-expert-v2.0-12b

# Optional API key (any non-empty string works for local servers)
LM_STUDIO_API_KEY=sk-local-placeholder
```

**Model-specific configuration:**
```bash
# Model names (used by various components)
THEOLOGY_MODEL=christian-bible-expert-v2.0-12b
MATH_MODEL=self-certainty-qwen3-1.7b-base-math
EMBEDDING_MODEL=text-embedding-bge-m3
RERANKER_MODEL=qwen.qwen3-reranker-0.6b
```

**Legacy support (backward compatibility):**
```bash
# These still work but prefer LM_STUDIO_BASE_URL
LM_STUDIO_HOST=http://127.0.0.1:1234
LM_EMBED_HOST=127.0.0.1
LM_EMBED_PORT=1234
```

### ✅ CORRECT: Use Centralized Config Loader

**Always use `get_lm_studio_settings()` from `scripts/config/env.py`:**

```python
from scripts.config.env import get_lm_studio_settings

settings = get_lm_studio_settings()
# Returns:
# {
#     "enabled": bool,      # True if LM_STUDIO_ENABLED=1 and base_url/model are set
#     "base_url": str | None,  # Base URL with /v1 suffix
#     "model": str | None,     # Model name
#     "api_key": str | None,   # Optional API key
# }

if not settings["enabled"]:
    # LM Studio is disabled or not configured
    return {"ok": False, "mode": "lm_off", "reason": "lm_studio_disabled"}
```

**Check if LM Studio is enabled:**
```python
from scripts.config.env import get_lm_studio_enabled

if get_lm_studio_enabled():
    # LM Studio is enabled
    pass
```

### ❌ WRONG: Direct Environment Variable Access

**Never do this:**
```python
import os

# ❌ WRONG - Bypasses centralized loader
enabled = os.getenv("LM_STUDIO_ENABLED") == "1"
base_url = os.getenv("LM_STUDIO_BASE_URL")
```

**Why**: Centralized loader handles validation, defaults, and precedence. Direct access bypasses this logic.

---

## LM Studio Usage in Code

### ✅ CORRECT: Use Adapter Pattern

**For simple LM Studio calls, use the adapter:**

```python
from pmagent.adapters.lm_studio import lm_studio_chat

messages = [
    {"role": "user", "content": "What is gematria?"}
]

result = lm_studio_chat(
    messages=messages,
    temperature=0.0,
    max_tokens=512,
    timeout=30.0,
)

# Result structure:
# {
#     "ok": bool,              # True if call succeeded
#     "mode": "lm_on" | "lm_off",  # Current mode
#     "reason": str | None,    # Error reason if mode is lm_off
#     "response": dict | None, # LM Studio API response if ok
# }

if result["ok"]:
    content = result["response"]["choices"][0]["message"]["content"]
else:
    # Handle lm_off mode (hermetic behavior)
    print(f"LM Studio unavailable: {result['reason']}")
```

### ✅ CORRECT: Use Logging Wrapper (Recommended)

**For control-plane observability, use the logging wrapper:**

```python
from pmagent.runtime.lm_logging import lm_studio_chat_with_logging

messages = [
    {"role": "user", "content": "What is gematria?"}
]

result = lm_studio_chat_with_logging(
    messages=messages,
    temperature=0.0,
    max_tokens=512,
    timeout=30.0,
)

# Same result structure as lm_studio_chat()
# Plus: Automatically logs to control.agent_run table (if DB available)
# Graceful no-op when DB unavailable (hermetic DB-off behavior)
```

### ✅ CORRECT: Use Guarded Wrapper (Phase-6)

**For budget enforcement and fallback support, use the guarded wrapper:**

```python
from pmagent.runtime.lm_logging import guarded_lm_call

def my_fallback(messages, kwargs):
    """Fallback function when LM Studio is unavailable."""
    return {
        "ok": True,
        "response": {"choices": [{"message": {"content": "Fallback response"}}]}
    }

result = guarded_lm_call(
    call_site="my_module.my_function",
    messages=[{"role": "user", "content": "What is gematria?"}],
    temperature=0.0,
    max_tokens=512,
    timeout=30.0,
    fallback_fn=my_fallback,
    fallback_kwargs={},
    app_name="my_app",  # Optional, derived from call_site if not provided
)

# Result structure:
# {
#     "ok": bool,
#     "mode": "lm_on" | "lm_off" | "fallback" | "budget_exceeded",
#     "reason": str | None,
#     "response": dict | None,
#     "call_site": str,
# }
```

**Features of `guarded_lm_call()`:**
- Respects `LM_STUDIO_ENABLED` flag
- Enforces budget limits (Phase-6)
- Automatic fallback when LM Studio unavailable
- Control-plane logging (if DB available)
- Call-site tracking for observability

### ✅ CORRECT: Use Routing Helper

**For backend selection logic:**

```python
from pmagent.runtime.lm_routing import select_lm_backend

backend = select_lm_backend(prefer_local=True)
# Returns: "lm_studio" or "remote"

if backend == "lm_studio":
    # Use LM Studio adapter
    result = lm_studio_chat_with_logging(messages, ...)
else:
    # Use remote LLM (e.g., OpenAI, Anthropic)
    result = call_remote_llm(messages, ...)
```

### ❌ WRONG: Direct HTTP Calls

**Never do this:**
```python
import requests

# ❌ WRONG - Bypasses adapter, logging, and error handling
response = requests.post(
    "http://127.0.0.1:1234/v1/chat/completions",
    json={"model": "test", "messages": [...]}
)
```

**Why**: Adapter pattern provides:
- Centralized configuration
- Error handling (connection errors, timeouts)
- Hermetic behavior (lm_off mode)
- Control-plane logging
- Budget enforcement

---

## Common Patterns

### Pattern 1: Check LM Studio Before Use

```python
from scripts.config.env import get_lm_studio_enabled
from pmagent.adapters.lm_studio import lm_studio_chat

if get_lm_studio_enabled():
    result = lm_studio_chat(messages, ...)
    if result["ok"]:
        # Use result
        pass
    else:
        # Handle lm_off mode
        print(f"LM Studio unavailable: {result['reason']}")
else:
    # LM Studio disabled - use alternative
    pass
```

### Pattern 2: Graceful Degradation

```python
from pmagent.runtime.lm_logging import guarded_lm_call

def fallback_response(messages, kwargs):
    """Return a simple fallback when LM Studio is unavailable."""
    return {
        "ok": True,
        "response": {
            "choices": [{
                "message": {
                    "content": "I'm sorry, I cannot process this request right now."
                }
            }]
        }
    }

result = guarded_lm_call(
    call_site="my_module.process",
    messages=messages,
    fallback_fn=fallback_response,
)

# Always get a response, even if LM Studio is unavailable
if result["ok"]:
    content = result["response"]["choices"][0]["message"]["content"]
```

### Pattern 3: Database with Error Handling

```python
from scripts.config.env import get_rw_dsn
import psycopg

def query_database():
    dsn = get_rw_dsn()
    if not dsn:
        # DB not configured - return empty result (hermetic behavior)
        return {"ok": False, "mode": "db_off", "data": []}
    
    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM gematria.nodes LIMIT 10")
                rows = cur.fetchall()
                return {"ok": True, "mode": "db_on", "data": rows}
    except psycopg.OperationalError as e:
        # DB unavailable - return empty result (hermetic behavior)
        return {"ok": False, "mode": "db_off", "reason": str(e), "data": []}
```

### Pattern 4: Control-Plane Logging

```python
from pmagent.runtime.lm_logging import _write_agent_run

# Log any tool/agent operation to control.agent_run
_write_agent_run(
    tool="my_tool",
    args_json={"input": "test"},
    result_json={"output": "result"},
    violations_json=None,  # Or list of violations if any
)

# Returns run_id (UUID string) if successful, None if DB unavailable
# Graceful no-op when DB unavailable (hermetic DB-off behavior)
```

---

## Anti-Patterns (What NOT to Do)

### ❌ Anti-Pattern 1: Direct os.getenv() for DSNs

```python
# ❌ WRONG
import os
dsn = os.getenv("GEMATRIA_DSN")

# ✅ CORRECT
from scripts.config.env import get_rw_dsn
dsn = get_rw_dsn()
```

### ❌ Anti-Pattern 2: Direct os.getenv() for LM Studio Config

```python
# ❌ WRONG
import os
enabled = os.getenv("LM_STUDIO_ENABLED") == "1"
base_url = os.getenv("LM_STUDIO_BASE_URL")

# ✅ CORRECT
from scripts.config.env import get_lm_studio_settings
settings = get_lm_studio_settings()
enabled = settings["enabled"]
base_url = settings["base_url"]
```

### ❌ Anti-Pattern 3: Direct HTTP Calls to LM Studio

```python
# ❌ WRONG
import requests
response = requests.post("http://127.0.0.1:1234/v1/chat/completions", ...)

# ✅ CORRECT
from pmagent.adapters.lm_studio import lm_studio_chat
result = lm_studio_chat(messages, ...)
```

### ❌ Anti-Pattern 4: Hardcoded DSNs

```python
# ❌ WRONG
dsn = "postgresql://user:pass@localhost:5432/gematria"

# ✅ CORRECT
from scripts.config.env import get_rw_dsn
dsn = get_rw_dsn()
```

### ❌ Anti-Pattern 5: Not Handling DB-Off Mode

```python
# ❌ WRONG - Crashes when DB unavailable
from scripts.config.env import get_rw_dsn
import psycopg

dsn = get_rw_dsn()
conn = psycopg.connect(dsn)  # Raises exception if DB unavailable

# ✅ CORRECT - Graceful degradation
from scripts.config.env import get_rw_dsn
import psycopg

dsn = get_rw_dsn()
if not dsn:
    return {"ok": False, "mode": "db_off"}

try:
    with psycopg.connect(dsn) as conn:
        # Use connection
        pass
except psycopg.OperationalError:
    return {"ok": False, "mode": "db_off"}
```

### ❌ Anti-Pattern 6: Not Handling LM-Off Mode

```python
# ❌ WRONG - Assumes LM Studio is always available
from pmagent.adapters.lm_studio import lm_studio_chat

result = lm_studio_chat(messages, ...)
content = result["response"]["choices"][0]["message"]["content"]  # Crashes if lm_off

# ✅ CORRECT - Check result first
from pmagent.adapters.lm_studio import lm_studio_chat

result = lm_studio_chat(messages, ...)
if result["ok"]:
    content = result["response"]["choices"][0]["message"]["content"]
else:
    # Handle lm_off mode
    content = "LM Studio unavailable"
```

---

## Quick Reference Checklist

When writing code that uses LM Studio or databases:

- [ ] Use `get_rw_dsn()`, `get_ro_dsn()`, or `get_bible_db_dsn()` for database connections
- [ ] Use `get_lm_studio_settings()` or `get_lm_studio_enabled()` for LM Studio configuration
- [ ] Use `lm_studio_chat()` or `lm_studio_chat_with_logging()` for LM Studio calls
- [ ] Use `guarded_lm_call()` for budget enforcement and fallback support
- [ ] Handle `db_off` mode gracefully (hermetic behavior)
- [ ] Handle `lm_off` mode gracefully (hermetic behavior)
- [ ] Never use `os.getenv()` directly for DSNs or LM Studio config
- [ ] Never make direct HTTP calls to LM Studio
- [ ] Never hardcode DSNs or connection strings

---

## Related Documentation

- **LM Studio Setup**: `docs/runbooks/LM_STUDIO_SETUP.md`
- **Database Configuration**: `env_example.txt`
- **Centralized Config**: `scripts/config/env.py`
- **LM Studio Adapter**: `pmagent/adapters/lm_studio.py`
- **LM Logging**: `pmagent/runtime/lm_logging.py`
- **LM Routing**: `pmagent/runtime/lm_routing.py`
- **ADR-066**: `docs/ADRs/ADR-066-lm-studio-control-plane-integration.md`
- **RFC-080**: `docs/rfcs/RFC-080-lm-studio-control-plane-integration.md`

---

## Enforcement

These patterns are enforced by:

- **Rule 012**: Connectivity troubleshooting (DSN centralization)
- **Rule 043**: CI DB bootstrap (empty-DB handling)
- **Rule 057**: Embedding consistency (DSN centralization)
- **Rule 061**: AI learning tracking (DSN centralization)
- **Guard**: `scripts/ci/guard_dsn_centralized.py` (checks for direct `os.getenv()` usage)

