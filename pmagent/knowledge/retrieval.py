#!/usr/bin/env python3
"""
Document Retrieval Module

E2E Pipeline (Reality Check #1): Simple retrieval of doc sections based on text match.
"""

from __future__ import annotations

from typing import Any

try:
    import psycopg
except ImportError:
    psycopg = None

from scripts.config.env import get_rw_dsn


def retrieve_doc_sections(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """
    Retrieve doc sections matching the query using simple text match.

    Args:
        query: Search query string
        limit: Maximum number of sections to return (default: 5)

    Returns:
        List of dicts with keys: id, source_id, section_title, body, order_index
        Returns empty list if DB unavailable (db_off mode)
    """
    if psycopg is None:
        return []

    dsn = get_rw_dsn()
    if not dsn:
        return []

    try:
        with psycopg.connect(dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        ds.id,
                        ds.source_id,
                        ds.section_title,
                        ds.body,
                        ds.order_index,
                        dsrc.path,
                        dsrc.title as source_title
                    FROM control.doc_sections ds
                    JOIN control.doc_sources dsrc ON ds.source_id = dsrc.id
                    WHERE ds.body ILIKE %s
                    ORDER BY LENGTH(ds.body) ASC
                    LIMIT %s
                    """,
                    (f"%{query}%", limit),
                )
                rows = cur.fetchall()
                return [
                    {
                        "id": str(row[0]),
                        "source_id": str(row[1]),
                        "section_title": row[2],
                        "body": row[3],
                        "order_index": row[4],
                        "source_path": row[5],
                        "source_title": row[6],
                    }
                    for row in rows
                ]
    except Exception:
        # DB unavailable - return empty list (db_off mode)
        return []


def retrieve_all_sections() -> list[dict[str, Any]]:
    """
    Retrieve all doc sections (for testing/debugging).

    Returns:
        List of all doc sections
        Returns empty list if DB unavailable (db_off mode)
    """
    if psycopg is None:
        return []

    dsn = get_rw_dsn()
    if not dsn:
        return []

    try:
        with psycopg.connect(dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        ds.id,
                        ds.source_id,
                        ds.section_title,
                        ds.body,
                        ds.order_index,
                        dsrc.path,
                        dsrc.title as source_title
                    FROM control.doc_sections ds
                    JOIN control.doc_sources dsrc ON ds.source_id = dsrc.id
                    ORDER BY dsrc.path, ds.order_index
                    """
                )
                rows = cur.fetchall()
                return [
                    {
                        "id": str(row[0]),
                        "source_id": str(row[1]),
                        "section_title": row[2],
                        "body": row[3],
                        "order_index": row[4],
                        "source_path": row[5],
                        "source_title": row[6],
                    }
                    for row in rows
                ]
    except Exception:
        # DB unavailable - return empty list (db_off mode)
        return []
