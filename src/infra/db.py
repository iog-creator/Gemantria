# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any

from scripts.config.env import get_bible_db_dsn, get_rw_dsn

try:
    # psycopg 3 preferred
    import psycopg

    HAS_DB = True
except Exception:  # pragma: no cover
    HAS_DB = False  # Import optional for CI paths without DSNs

__all__ = [
    "BibleReadOnly",
    "GematriaRW",
    "ReadOnlyViolation",
    "get_bible_ro",
    "get_gematria_rw",
    "sql_is_write",
]

WRITE_RE = re.compile(
    r"^\s*(INSERT|UPDATE|DELETE|MERGE|CREATE|ALTER|DROP|TRUNCATE|GRANT|REVOKE)\b", re.I
)


class ReadOnlyViolation(RuntimeError):
    """Attempted write against read-only bible_db."""


def sql_is_write(sql: str) -> bool:
    return bool(WRITE_RE.match(sql or ""))


@dataclass
class BibleReadOnly:
    dsn: str | None

    def execute(self, sql: str, params: Sequence[Any] | None = None) -> Iterable[tuple]:
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
                yield from cur


@dataclass
class GematriaRW:
    dsn: str | None

    def execute(self, sql: str, params: Sequence[Any] | None = None) -> Iterable[tuple]:
        if not self.dsn:
            raise RuntimeError("GEMATRIA_DSN not set; cannot execute query")
        if not HAS_DB:
            raise RuntimeError("psycopg not available in this environment")
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params or ())
                if cur.description:
                    yield from cur


def get_bible_ro() -> BibleReadOnly:
    return BibleReadOnly(dsn=get_bible_db_dsn())


def get_gematria_rw() -> GematriaRW:
    return GematriaRW(dsn=get_rw_dsn())
