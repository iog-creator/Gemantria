#!/usr/bin/env python3
"""
Knowledge Base Export for Atlas

Phase-6 6C: Exports a subset of knowledge documents from knowledge.kb_document
to share/atlas/control_plane/kb_docs.head.json for downstream consumers.

Tolerates db_off (no DB required; best-effort empty exports).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    import psycopg
except ImportError:
    psycopg = None

from scripts.config.env import get_rw_dsn

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "share" / "atlas" / "control_plane"
OUT_KB_PATH = OUT_DIR / "kb_docs.head.json"

# Preview length (first N characters of body_md)
PREVIEW_LENGTH = 200


@dataclass
class KBDocItem:
    id: str
    title: str
    section: str
    slug: str
    tags: list[str]
    preview: str
    created_at: str


@dataclass
class KBExport:
    schema: str
    generated_at: str
    ok: bool
    connection_ok: bool
    docs: list[KBDocItem]
    db_off: bool = False
    error: str | None = None


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _get_output_path() -> Path:
    """Get output path for KB export (for testing)."""
    return OUT_KB_PATH


def extract_preview(body_md: str, max_length: int = PREVIEW_LENGTH) -> str:
    """Extract preview text from markdown (first paragraph or first N chars)."""
    # Try to extract first paragraph
    lines = body_md.strip().split("\n")
    first_para = ""
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        first_para = line
        break

    if first_para:
        # Remove markdown formatting for preview
        preview = first_para.replace("**", "").replace("*", "").replace("`", "")
        if len(preview) <= max_length:
            return preview
        return preview[:max_length] + "..."

    # Fallback: first N characters
    text = body_md.strip().replace("\n", " ")
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def db_off_kb_payload(message: str) -> KBExport:
    return KBExport(
        schema="knowledge",
        generated_at=now_iso(),
        ok=False,
        connection_ok=False,
        docs=[],
        db_off=True,
        error=message,
    )


def fetch_kb_docs(limit: int = 50) -> KBExport:
    """Fetch a subset of KB documents from knowledge.kb_document."""
    if psycopg is None:
        return db_off_kb_payload("psycopg not available")

    dsn = get_rw_dsn()
    if not dsn:
        return db_off_kb_payload("GEMATRIA_DSN not set")

    try:
        with psycopg.connect(dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Check if knowledge schema exists
                cur.execute(
                    """
                    SELECT 1
                    FROM information_schema.schemata
                    WHERE schema_name = 'knowledge'
                    """
                )
                if not cur.fetchone():
                    # Schema doesn't exist - return empty list (backward compatible)
                    return KBExport(
                        schema="knowledge",
                        generated_at=now_iso(),
                        ok=True,
                        connection_ok=True,
                        docs=[],
                        db_off=False,
                        error=None,
                    )

                # Check if kb_document table exists
                cur.execute(
                    """
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'knowledge'
                      AND table_name = 'kb_document'
                    """
                )
                if not cur.fetchone():
                    # Table doesn't exist - return empty list
                    return KBExport(
                        schema="knowledge",
                        generated_at=now_iso(),
                        ok=True,
                        connection_ok=True,
                        docs=[],
                        db_off=False,
                        error=None,
                    )

                # Fetch documents (ordered by created_at DESC, limit)
                cur.execute(
                    """
                    SELECT id, title, section, slug, tags, body_md, created_at
                    FROM knowledge.kb_document
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cur.fetchall()

                docs: list[KBDocItem] = []
                for row in rows:
                    doc_id, title, section, slug, tags, body_md, created_at = row
                    preview = extract_preview(body_md)
                    docs.append(
                        KBDocItem(
                            id=str(doc_id),
                            title=title,
                            section=section,
                            slug=slug,
                            tags=list(tags) if tags else [],
                            preview=preview,
                            created_at=created_at.isoformat() if created_at else now_iso(),
                        )
                    )

                return KBExport(
                    schema="knowledge",
                    generated_at=now_iso(),
                    ok=True,
                    connection_ok=True,
                    docs=docs,
                    db_off=False,
                    error=None,
                )

    except Exception as exc:  # noqa: BLE001
        return db_off_kb_payload(f"database error: {exc!s}")


def main() -> None:
    """Export KB documents to JSON file."""
    output_path = _get_output_path()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    kb_export = fetch_kb_docs(limit=50)

    # Convert to dict for JSON serialization
    export_dict: dict[str, Any] = {
        "schema": kb_export.schema,
        "generated_at": kb_export.generated_at,
        "ok": kb_export.ok,
        "connection_ok": kb_export.connection_ok,
        "docs": [asdict(doc) for doc in kb_export.docs],
    }
    if kb_export.db_off:
        export_dict["db_off"] = True
    if kb_export.error:
        export_dict["error"] = kb_export.error

    output_path.write_text(
        json.dumps(export_dict, indent=2, sort_keys=True),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
