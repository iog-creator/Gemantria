#!/usr/bin/env python3
"""
Docs Dashboard Refresh Script

Regenerates JSON exports for the Doc Control Panel UI.
Reads from control.kb_document and writes to share/exports/docs-control/.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

try:
    import psycopg
except ImportError:
    psycopg = None

from scripts.config.env import get_rw_dsn

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPORTS_DIR = REPO_ROOT / "share/exports/docs-control"


def ensure_exports_dir() -> None:
    """Ensure the exports directory exists."""
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


def write_json(filename: str, data: Any) -> None:
    """Write data to a JSON file in the exports directory."""
    path = EXPORTS_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"✓ Wrote {path}")


def get_db_connection() -> Any:
    """Get a database connection or exit if unavailable."""
    if psycopg is None:
        print("ERROR: psycopg not available", file=sys.stderr)
        sys.exit(1)

    dsn = get_rw_dsn()
    if not dsn:
        print("ERROR: GEMATRIA_DSN not set", file=sys.stderr)
        sys.exit(1)

    try:
        return psycopg.connect(dsn, autocommit=True)
    except Exception as exc:
        print(f"ERROR: Failed to connect to database: {exc}", file=sys.stderr)
        sys.exit(1)


def generate_summary(conn: Any) -> None:
    """Generate summary.json."""
    with conn.cursor() as cur:
        # Total docs
        cur.execute("SELECT COUNT(*) FROM control.kb_document")
        total_docs = cur.fetchone()[0]

        # Canonical docs (using is_canonical flag)
        cur.execute("SELECT COUNT(*) FROM control.kb_document WHERE is_canonical = TRUE")
        canonical_docs = cur.fetchone()[0]

        # Archive candidates
        cur.execute("SELECT COUNT(*) FROM control.kb_document WHERE status = 'archive_candidate'")
        archive_candidates = cur.fetchone()[0]

        # Unreviewed
        cur.execute("SELECT COUNT(*) FROM control.kb_document WHERE status = 'unreviewed'")
        unreviewed = cur.fetchone()[0]

        # Path buckets
        cur.execute("SELECT COUNT(*) FROM control.kb_document WHERE path LIKE 'docs/SSOT/%'")
        ssot_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM control.kb_document WHERE path LIKE 'archive/%'")
        archive_count = cur.fetchone()[0]

        other_count = total_docs - ssot_count - archive_count

    data = {
        "totals": {
            "canonical": canonical_docs,
            "archive_candidates": archive_candidates,
            "unreviewed": unreviewed,
            "total": total_docs,
        },
        "path_buckets": {
            "ssot": ssot_count,
            "archive": archive_count,
            "other": other_count,
        },
        "generated_at": datetime.now(UTC).isoformat(),
    }
    write_json("summary.json", data)


def generate_canonical(conn: Any) -> None:
    """Generate canonical.json."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT path, title, doc_type, status, is_canonical, mtime, size_bytes
            FROM control.kb_document
            WHERE is_canonical = TRUE
            ORDER BY path
            """
        )
        rows = cur.fetchall()

    items = []
    for row in rows:
        items.append(
            {
                "path": row[0],
                "title": row[1],
                "doc_type": row[2],
                "status": row[3] or "canonical",
                "is_canonical": bool(row[4]),
                "last_modified": row[5].isoformat() if row[5] else None,
                "size_bytes": row[6] or 0,
            }
        )

    data = {
        "items": items,
        "total": len(items),
        "generated_at": datetime.now(UTC).isoformat(),
    }
    write_json("canonical.json", data)


def generate_archive_candidates(conn: Any) -> None:
    """Generate archive-candidates.json."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT path
            FROM control.kb_document
            WHERE doc_type = 'archive_candidate'
            ORDER BY path
            """
        )
        rows = cur.fetchall()

    # Group by directory
    groups = {}
    for (path,) in rows:
        directory = str(Path(path).parent)
        if directory not in groups:
            groups[directory] = {"count": 0, "examples": []}
        groups[directory]["count"] += 1
        if len(groups[directory]["examples"]) < 3:
            groups[directory]["examples"].append(path)

    group_list = [
        {
            "directory": directory,
            "count": info["count"],
            "example_paths": info["examples"][:3],  # Limit to 3 examples
            "confidence": "safe_cluster"
            if info["count"] >= 3 and "archive" in directory.lower()
            else "mixed_cluster",
            "notes": f"Detected {info['count']} archive candidates in directory",
        }
        for directory, info in groups.items()
    ]

    total_items = sum(info["count"] for info in groups.values())

    data = {
        "groups": group_list,
        "total_groups": len(group_list),
        "total_items": total_items,
        "generated_at": datetime.now(UTC).isoformat(),
    }
    write_json("archive-candidates.json", data)


def generate_unreviewed_batch(conn: Any) -> None:
    """Generate unreviewed-batch.json."""
    with conn.cursor() as cur:
        # Get total count for remaining_estimate
        cur.execute("SELECT COUNT(*) FROM control.kb_document WHERE status = 'unreviewed'")
        total_unreviewed = cur.fetchone()[0]

        cur.execute(
            """
            SELECT path, title, doc_type, status, mtime
            FROM control.kb_document
            WHERE status = 'unreviewed'
            ORDER BY mtime DESC
            LIMIT 20
            """
        )
        rows = cur.fetchall()

    items = []
    for row in rows:
        items.append(
            {
                "path": row[0],
                "doc_type": row[2],
                "status": row[3] or "unreviewed",
                "title": row[1],
                "snippet": "",  # Placeholder - would need file content or DB field
                "guess": "unknown",  # Placeholder - would need heuristic analysis
                "last_modified": row[4].isoformat() if row[4] else None,
            }
        )

    data = {
        "batch_id": datetime.now(UTC).strftime("%Y%m%d-%H%M%S"),
        "items": items,
        "batch_size": len(items),
        "remaining_estimate": max(0, total_unreviewed - len(items)),
        "generated_at": datetime.now(UTC).isoformat(),
    }
    write_json("unreviewed-batch.json", data)


def generate_orphans() -> None:
    """Generate orphans.json (placeholder implementation)."""
    # In a real implementation, this would parse docs/analysis/ORPHANS_CANDIDATE_REPORT.md
    # or run a scan. For now, we'll generate a placeholder or empty list if the report doesn't exist.
    data = {
        "categories": [],
        "generated_at": datetime.now(UTC).isoformat(),
    }
    write_json("orphans.json", data)


def generate_archive_dryrun() -> None:
    """Generate archive-dryrun.json (placeholder implementation)."""
    # In a real implementation, this would parse docs/analysis/DOC_ARCHIVE_DRYRUN.md
    data = {
        "total_candidates": 0,
        "items": [],
        "groups": [],
        "generated_at": datetime.now(UTC).isoformat(),
    }
    write_json("archive-dryrun.json", data)


def main() -> None:
    """Main entry point."""
    ensure_exports_dir()

    conn = get_db_connection()
    try:
        print("Generating Doc Control Panel exports...")
        generate_summary(conn)
        generate_canonical(conn)
        generate_archive_candidates(conn)
        generate_unreviewed_batch(conn)
        generate_orphans()
        generate_archive_dryrun()
        print("✓ All exports generated successfully.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
