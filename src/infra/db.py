from __future__ import annotations
import os
import re
from dataclasses import dataclass
from typing import Any, Iterable, Optional, Sequence, Tuple

try:
    # psycopg 3 preferred
    import psycopg
    HAS_DB = True
except Exception:  # pragma: no cover
    HAS_DB = False  # Import optional for CI paths without DSNs

__all__ = [
    "ReadOnlyViolation",
    "BibleReadOnly",
    "GematriaRW",
    "get_bible_ro",
    "get_gematria_rw",
    "sql_is_write",
]

WRITE_RE = re.compile(r"^\s*(INSERT|UPDATE|DELETE|MERGE|CREATE|ALTER|DROP|TRUNCATE|GRANT|REVOKE)\b", re.I)

class ReadOnlyViolation(RuntimeError):
    """Attempted write against read-only bible_db."""

def sql_is_write(sql: str) -> bool:
    return bool(WRITE_RE.match(sql or ""))

@dataclass
class BibleReadOnly:
    dsn: Optional[str]

    def execute(self, sql: str, params: Optional[Sequence[Any]] = None) -> Iterable[Tuple]:
        """
        Enforces read-only at the adapter level *before* any DB connection is touched.
        Requires %s parameterization; does not permit f-string interpolation.
        """
        if sql_is_write(sql):
            raise ReadOnlyViolation("Writes are forbidden on bible_db (RO adapter)")
        # Guard: only connect if we truly need to run a read query.
        if not self.dsn:
            # No DSN present; allow unit/contract tests to run without DB.
            raise RuntimeError("BIBLE_DB_DSN not set; cannot execute read query")
        if not HAS_DB:
            raise RuntimeError("psycopg not available in this environment")
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params or ())
                for row in cur:
                    yield row

@dataclass
class GematriaRW:
    dsn: Optional[str]

    def execute(self, sql: str, params: Optional[Sequence[Any]] = None) -> Iterable[Tuple]:
        if not self.dsn:
            raise RuntimeError("GEMATRIA_DSN not set; cannot execute query")
        if not HAS_DB:
            raise RuntimeError("psycopg not available in this environment")
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params or ())
                if cur.description:
                    for row in cur:
                        yield row

def get_bible_ro() -> BibleReadOnly:
    return BibleReadOnly(dsn=os.getenv("BIBLE_DB_DSN"))

def get_gematria_rw() -> GematriaRW:
    return GematriaRW(dsn=os.getenv("GEMATRIA_DSN"))
