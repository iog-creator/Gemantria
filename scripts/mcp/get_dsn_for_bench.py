#!/usr/bin/env python3
"""Get DSN for MCP bench (centralized loader with fallbacks)."""
try:
    from scripts.config import env as _env
    ro = getattr(_env, "dsn_ro", lambda: None)()
    rw = getattr(_env, "dsn_rw", lambda: None)()
    print(ro or rw or "")
except Exception:
    print("")

