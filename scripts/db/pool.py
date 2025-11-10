#!/usr/bin/env python3
# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
from __future__ import annotations

import os

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

_POOL: ConnectionPool | None = None


def _dsn() -> str:
    return os.environ.get("ATLAS_DSN_RW") or os.environ.get("GEMATRIA_DSN") or os.environ.get("ATLAS_DSN") or ""


def get_pool() -> ConnectionPool:
    """Lazily create a shared pool the first time it's needed."""
    global _POOL
    if _POOL is None:
        dsn = _dsn()
        if not dsn:
            raise RuntimeError(
                "DSN missing: set ATLAS_DSN_RW or GEMATRIA_DSN or ATLAS_DSN before importing writers/search"
            )
        _POOL = ConnectionPool(
            conninfo=dsn,
            min_size=1,
            max_size=10,
            max_idle=30,  # seconds before idle conns are dropped
            num_workers=2,  # background open/close workers
            kwargs={"autocommit": False},  # explicit tx control
        )
    return _POOL


# Backward compatibility: POOL still works but is lazy
def __getattr__(name: str):
    if name == "POOL":
        return get_pool()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def connection_dict():
    """Context manager: pooled connection with dict_row default."""
    cm = get_pool().connection()
    conn = cm.__enter__()
    conn.row_factory = dict_row
    try:
        yield conn
    finally:
        cm.__exit__(None, None, None)
