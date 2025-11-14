#!/usr/bin/env python3
"""
Phase-3A DB Loader — Centralized database connection helpers.

Provides SQLAlchemy engines and query helpers for GEMATRIA_DSN and BIBLE_DB_DSN.
Uses existing centralized DSN loaders (scripts.config.env).
"""

from __future__ import annotations

from typing import Any

from scripts.config.env import get_bible_db_dsn, get_rw_dsn

try:
    from sqlalchemy import Engine, create_engine, text
    from sqlalchemy.exc import OperationalError, ProgrammingError

    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    Engine = Any  # type: ignore[assignment,misc]


class DbUnavailableError(RuntimeError):
    """Database is unavailable (connection error, DSN not set, etc.)."""


class TableMissingError(RuntimeError):
    """Required table/view does not exist in the database."""


# Engine cache (lazy initialization)
_control_engine: Engine | None = None
_bible_engine: Engine | None = None


def get_control_engine() -> Engine:
    """
    Get SQLAlchemy engine for GEMATRIA_DSN (control/gematria schema).

    Returns:
        SQLAlchemy Engine instance.

    Raises:
        DbUnavailableError: If DSN is not set or SQLAlchemy is not available.
    """
    global _control_engine

    if not HAS_SQLALCHEMY:
        raise DbUnavailableError("SQLAlchemy not available in this environment")

    if _control_engine is None:
        dsn = get_rw_dsn()
        if not dsn:
            raise DbUnavailableError("GEMATRIA_DSN not set; cannot create control engine")
        _control_engine = create_engine(dsn, pool_pre_ping=True, echo=False)

    return _control_engine


def get_bible_engine() -> Engine:
    """
    Get SQLAlchemy engine for BIBLE_DB_DSN (read-only Bible database).

    Returns:
        SQLAlchemy Engine instance.

    Raises:
        DbUnavailableError: If DSN is not set or SQLAlchemy is not available.
    """
    global _bible_engine

    if not HAS_SQLALCHEMY:
        raise DbUnavailableError("SQLAlchemy not available in this environment")

    if _bible_engine is None:
        dsn = get_bible_db_dsn()
        if not dsn:
            raise DbUnavailableError("BIBLE_DB_DSN not set; cannot create bible engine")
        _bible_engine = create_engine(dsn, pool_pre_ping=True, echo=False)

    return _bible_engine


def fetch_graph_head(limit: int = 20) -> list[dict[str, Any]]:
    """
    Fetch head rows from graph nodes table (gematria.nodes or gematria.concepts).

    Args:
        limit: Maximum number of rows to return.

    Returns:
        List of dictionaries, each representing a node/concept row.

    Raises:
        DbUnavailableError: If database connection fails.
        TableMissingError: If required tables do not exist.
    """
    try:
        engine = get_control_engine()
    except DbUnavailableError:
        raise

    # Try gematria.nodes first (newer schema), fallback to gematria.concepts
    queries = [
        "SELECT * FROM gematria.nodes ORDER BY created_at DESC LIMIT :limit",
        "SELECT * FROM gematria.concepts ORDER BY created_at DESC LIMIT :limit",
    ]

    for query in queries:
        try:
            with engine.connect() as conn:
                result = conn.execute(text(query), {"limit": limit})
                rows = result.fetchall()
                # Convert to list of dicts
                return [dict(row._mapping) for row in rows]  # type: ignore[attr-defined]
        except ProgrammingError as e:
            # Table doesn't exist, try next query
            if "does not exist" in str(e) or "relation" in str(e).lower():
                continue
            raise TableMissingError(f"Table query failed: {e}") from e
        except OperationalError as e:
            raise DbUnavailableError(f"Database connection failed: {e}") from e

    # Neither table exists
    raise TableMissingError("Neither gematria.nodes nor gematria.concepts table exists")


def fetch_graph_stats_head(limit: int = 20) -> list[dict[str, Any]]:
    """
    Fetch head rows from graph stats/centrality table (gematria.concept_centrality).

    Args:
        limit: Maximum number of rows to return.

    Returns:
        List of dictionaries, each representing a centrality/stats row.

    Raises:
        DbUnavailableError: If database connection fails.
        TableMissingError: If required tables do not exist.
    """
    try:
        engine = get_control_engine()
    except DbUnavailableError:
        raise

    query = "SELECT * FROM gematria.concept_centrality ORDER BY metrics_at DESC LIMIT :limit"

    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), {"limit": limit})
            rows = result.fetchall()
            # Convert to list of dicts
            return [dict(row._mapping) for row in rows]  # type: ignore[attr-defined]
    except ProgrammingError as e:
        if "does not exist" in str(e) or "relation" in str(e).lower():
            raise TableMissingError("gematria.concept_centrality table does not exist") from e
        raise TableMissingError(f"Table query failed: {e}") from e
    except OperationalError as e:
        raise DbUnavailableError(f"Database connection failed: {e}") from e
