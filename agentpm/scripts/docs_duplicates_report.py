#!/usr/bin/env python3
"""
Document Duplicates Report Script (DM-001)

Generates a report of exact and near-duplicate documents from control.kb_document.

Tolerates db_off (no DB required; fails gracefully with clear message).
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    import psycopg
except ImportError:
    psycopg = None

from scripts.config.env import get_rw_dsn

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = REPO_ROOT / "docs" / "analysis" / "DOC_DUPLICATES_REPORT.md"


def generate_duplicates_report(output_path: Path | None = None) -> dict[str, Any]:
    """
    Generate duplicates report and return summary.

    Args:
        output_path: Output file path (defaults to OUTPUT_PATH)

    Returns:
        Dictionary with report summary:
        {
            "ok": bool,
            "db_off": bool,
            "error": str | None,
            "exact_duplicates": int,
            "duplicate_groups": list[dict],
        }
    """
    if output_path is None:
        output_path = OUTPUT_PATH

    result: dict[str, Any] = {
        "ok": False,
        "db_off": False,
        "error": None,
        "exact_duplicates": 0,
        "duplicate_groups": [],
    }

    # Check for DB connection
    if psycopg is None:
        result["db_off"] = True
        result["error"] = "psycopg not available"
        return result

    dsn = get_rw_dsn()
    if not dsn:
        result["db_off"] = True
        result["error"] = "GEMATRIA_DSN not set"
        return result

    try:
        with psycopg.connect(dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Check if control.kb_document table exists
                cur.execute(
                    """
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'control'
                      AND table_name = 'kb_document'
                    """
                )
                if not cur.fetchone():
                    result["error"] = "control.kb_document table does not exist. Run migration 048 first."
                    return result

                # Find exact duplicates (same content_hash, multiple paths)
                cur.execute(
                    """
                    SELECT content_hash, array_agg(path ORDER BY path) AS paths, count(*) AS n
                    FROM control.kb_document
                    WHERE project = 'Gemantria.v2'
                    GROUP BY content_hash
                    HAVING count(*) > 1
                    ORDER BY n DESC, content_hash
                    """
                )
                duplicate_rows = cur.fetchall()

                duplicate_groups: list[dict[str, Any]] = []
                total_duplicate_files = 0

                for content_hash, paths, count in duplicate_rows:
                    # Get additional metadata for each path
                    cur.execute(
                        """
                        SELECT path, title, doc_type, size_bytes, mtime, status
                        FROM control.kb_document
                        WHERE content_hash = %s
                        ORDER BY path
                        """,
                        (content_hash,),
                    )
                    file_details = cur.fetchall()

                    group = {
                        "content_hash": content_hash,
                        "count": count,
                        "paths": list(paths),
                        "files": [
                            {
                                "path": row[0],
                                "title": row[1],
                                "doc_type": row[2],
                                "size_bytes": row[3],
                                "mtime": row[4].isoformat() if row[4] else None,
                                "status": row[5],
                            }
                            for row in file_details
                        ],
                    }
                    duplicate_groups.append(group)
                    total_duplicate_files += count

                result["ok"] = True
                result["exact_duplicates"] = total_duplicate_files
                result["duplicate_groups"] = duplicate_groups

                # Generate markdown report
                output_path.parent.mkdir(parents=True, exist_ok=True)
                report_lines = [
                    "# Document Duplicates Report (DM-001)",
                    "",
                    f"**Generated:** {datetime.now(UTC).isoformat()}",
                    "",
                    "This report lists exact duplicate documents found in the repository.",
                    "Documents are considered duplicates if they have the same content hash (SHA-256).",
                    "",
                    "## Summary",
                    "",
                    f"- **Total duplicate groups:** {len(duplicate_groups)}",
                    f"- **Total duplicate files:** {total_duplicate_files}",
                    "",
                    "## Exact Duplicates",
                    "",
                ]

                if not duplicate_groups:
                    report_lines.append("No exact duplicates found. ✓")
                else:
                    for i, group in enumerate(duplicate_groups, 1):
                        report_lines.append(f"### Duplicate Group {i}")
                        report_lines.append("")
                        report_lines.append(f"**Content Hash:** `{group['content_hash']}`")
                        report_lines.append(f"**Count:** {group['count']} file(s)")
                        report_lines.append("")
                        report_lines.append("**Files:**")
                        report_lines.append("")
                        for file_info in group["files"]:
                            report_lines.append(f"- `{file_info['path']}`")
                            report_lines.append(f"  - Title: {file_info['title']}")
                            report_lines.append(f"  - Type: {file_info['doc_type']}")
                            report_lines.append(f"  - Size: {file_info['size_bytes']} bytes")
                            report_lines.append(f"  - Status: {file_info['status']}")
                            if file_info["mtime"]:
                                report_lines.append(f"  - Modified: {file_info['mtime']}")
                            report_lines.append("")

                report_lines.append("---")
                report_lines.append("")
                report_lines.append("*This report was generated by DM-001 document inventory system.*")

                output_path.write_text("\n".join(report_lines), encoding="utf-8")

    except Exception as exc:  # noqa: BLE001
        result["error"] = f"database error: {exc!s}"
        result["db_off"] = True

    return result


def main() -> None:
    """CLI entry point for duplicates report."""
    import sys

    result = generate_duplicates_report()

    if result.get("db_off"):
        print(f"WARNING: {result.get('error', 'Database unavailable')}")
        print("db_off: true")
        sys.exit(0)

    if not result.get("ok"):
        print(f"ERROR: {result.get('error', 'Unknown error')}")
        sys.exit(1)

    print(f"Found {len(result['duplicate_groups'])} duplicate group(s)")
    print(f"Total duplicate files: {result['exact_duplicates']}")
    print(f"Report written to: {OUTPUT_PATH}")
    print("✓ Duplicates report generated successfully")


if __name__ == "__main__":
    main()
