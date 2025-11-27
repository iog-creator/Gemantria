#!/usr/bin/env python3
"""
Document Inventory Script (DM-001)

Scans the repository for markdown-like files and upserts metadata into control.kb_document
for document management and duplicate detection.

This command REQUIRES the database to be available.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

try:
    import psycopg
except ImportError:
    psycopg = None

from scripts.config.env import get_rw_dsn

REPO_ROOT = Path(__file__).resolve().parents[2]

# File extensions to include
DOC_EXTENSIONS = {".md", ".mdx", ".txt", ".mdc"}

# Directories to exclude
EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".ruff_cache",
    ".mypy_cache",
    "archive/evidence",
    ".pytest_cache",
    "test-results",
    "gemantria.egg-info",
    "share",  # Exclude share directory (derived artifacts)
}


def extract_title_from_markdown(content: str, filename: str) -> str:
    """Extract title from markdown (first H1) or use filename."""
    # Look for first H1
    h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip()
    # Fallback to filename without extension
    return Path(filename).stem.replace("_", " ").replace("-", " ").title()


def infer_doc_type(filepath: Path, repo_root: Path) -> str:
    """Infer document type from path."""
    rel_path = str(filepath.relative_to(repo_root))
    rel_path_lower = rel_path.lower()

    if "ssot" in rel_path_lower or rel_path.startswith("docs/SSOT/"):
        return "ssot"
    if "runbook" in rel_path_lower or rel_path.startswith("docs/runbooks/"):
        return "runbook"
    if "legacy" in rel_path_lower or "old" in rel_path_lower or "archive" in rel_path_lower:
        return "legacy"
    return "reference"


def compute_content_hash(content: bytes) -> str:
    """Compute SHA-256 hash of content."""
    return hashlib.sha256(content).hexdigest()


def inventory_file(filepath: Path, repo_root: Path, conn: Any) -> tuple[str, bool]:
    """Inventory a single file into control.kb_document."""
    try:
        content_bytes = filepath.read_bytes()
        content_str = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        return f"Failed to read {filepath}: {exc!s}", False

    # Compute metadata
    rel_path = str(filepath.relative_to(repo_root))
    title = extract_title_from_markdown(content_str, filepath.name)
    doc_type = infer_doc_type(filepath, repo_root)
    content_hash = compute_content_hash(content_bytes)
    size_bytes = len(content_bytes)
    mtime = datetime.fromtimestamp(filepath.stat().st_mtime, tz=UTC)

    with conn.cursor() as cur:
        # UPSERT: update if path exists, insert otherwise
        cur.execute(
            """
            INSERT INTO control.kb_document (
                path, title, doc_type, project, content_hash, size_bytes, mtime, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (path) DO UPDATE SET
                title = EXCLUDED.title,
                doc_type = EXCLUDED.doc_type,
                content_hash = EXCLUDED.content_hash,
                size_bytes = EXCLUDED.size_bytes,
                mtime = EXCLUDED.mtime,
                updated_at = now()
            RETURNING id, path
            """,
            (
                rel_path,
                title,
                doc_type,
                "Gemantria.v2",
                content_hash,
                size_bytes,
                mtime,
                "unreviewed",
            ),
        )
        row = cur.fetchone()
        if row:
            doc_id, _doc_path = row
            return f"✓ {rel_path} → {doc_type} (id: {doc_id})", True
        return f"Failed to insert {rel_path}", False

    return f"Unexpected error processing {rel_path}", False


def should_include_path(filepath: Path, repo_root: Path) -> bool:
    """Check if a file path should be included in inventory."""
    # Check extension
    if filepath.suffix.lower() not in DOC_EXTENSIONS:
        return False

    # Check if in excluded directory
    try:
        rel_path = filepath.relative_to(repo_root)
        parts = rel_path.parts
        for part in parts:
            if part in EXCLUDE_DIRS:
                return False
            # Check for archive/evidence pattern
            if part == "archive" and "evidence" in parts:
                return False
    except ValueError:
        # Path not relative to repo root
        return False

    return True


def run_inventory(repo_root: Path | None = None) -> dict[str, Any]:
    """
    Run document inventory and return summary.

    Args:
        repo_root: Repository root path (defaults to REPO_ROOT)

    Returns:
        Dictionary with inventory summary:
        {
            "ok": bool,
            "db_off": bool,
            "error": str | None,
            "scanned": int,
            "inserted": int,
            "updated": int,
        }
    """
    if repo_root is None:
        repo_root = REPO_ROOT

    result: dict[str, Any] = {
        "ok": False,
        "db_off": False,
        "error": None,
        "scanned": 0,
        "inserted": 0,
        "updated": 0,
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
            # Check if control schema and kb_document table exist
            with conn.cursor() as cur:
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

            # Find all doc-like files
            doc_files: list[Path] = []
            for ext in DOC_EXTENSIONS:
                doc_files.extend(repo_root.rglob(f"*{ext}"))

            # Filter files
            included_files = [f for f in doc_files if should_include_path(f, repo_root)]
            result["scanned"] = len(included_files)

            if not included_files:
                result["ok"] = True
                result["error"] = "No markdown-like files found"
                return result

            # Track existing vs new
            inserted = 0
            updated = 0

            for doc_file in included_files:
                # Check if file exists in DB before upsert
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT path FROM control.kb_document WHERE path = %s",
                        (str(doc_file.relative_to(repo_root)),),
                    )
                    existed = cur.fetchone() is not None

                _msg, success = inventory_file(doc_file, repo_root, conn)
                if success:
                    if existed:
                        updated += 1
                    else:
                        inserted += 1

            result["ok"] = True
            result["inserted"] = inserted
            result["updated"] = updated

    except Exception as exc:  # noqa: BLE001
        result["error"] = f"database error: {exc!s}"

    return result


def main() -> None:
    """CLI entry point for document inventory."""
    import sys

    result = run_inventory()

    # This command REQUIRES the database - must fail if unavailable
    if result.get("error") and "database" in result.get("error", "").lower():
        print(f"ERROR: {result.get('error', 'Database unavailable')}", file=sys.stderr)
        print("ERROR: This command requires the database to be available.", file=sys.stderr)
        sys.exit(1)

    if not result.get("ok"):
        print(f"ERROR: {result.get('error', 'Unknown error')}")
        sys.exit(1)

    print(f"Scanned {result['scanned']} file(s)")
    print(f"Inserted {result['inserted']} new document(s)")
    print(f"Updated {result['updated']} existing document(s)")
    print("✓ Inventory completed successfully")


if __name__ == "__main__":
    main()
