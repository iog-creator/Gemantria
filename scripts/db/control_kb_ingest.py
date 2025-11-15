#!/usr/bin/env python3
"""
Knowledge Base Ingestion Script

Phase-6 6C: Ingests markdown files from a directory into knowledge.kb_document table.
Tolerates db_off (no DB required; fails gracefully with clear message).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    import psycopg
except ImportError:
    psycopg = None

from scripts.config.env import get_rw_dsn

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_DIR = REPO_ROOT / "docs" / "knowledge_seed"


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    # Convert to lowercase
    slug = text.lower()
    # Replace forward slashes with hyphens first
    slug = slug.replace("/", "-")
    # Remove special chars (keep word chars, spaces, hyphens)
    slug = re.sub(r"[^\w\s-]", "", slug)
    # Replace underscores and spaces with hyphens
    slug = re.sub(r"[_\s]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)  # Collapse multiple hyphens
    return slug.strip("-")


def extract_title_from_markdown(content: str, filename: str) -> str:
    """Extract title from markdown (first H1) or use filename."""
    # Look for first H1
    h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip()
    # Fallback to filename without extension
    return Path(filename).stem.replace("_", " ").replace("-", " ").title()


def extract_section_from_path(filepath: Path, base_dir: Path) -> str:
    """Extract section from parent directory name or 'general'."""
    rel_path = filepath.relative_to(base_dir)
    if len(rel_path.parts) > 1:
        # Parent directory is the section
        return rel_path.parts[0]
    return "general"


def ingest_markdown_file(
    filepath: Path,
    base_dir: Path,
    conn: Any,
) -> tuple[str, bool]:
    """Ingest a single markdown file into the database."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as exc:
        return f"Failed to read {filepath}: {exc!s}", False

    title = extract_title_from_markdown(content, filepath.name)
    section = extract_section_from_path(filepath, base_dir)
    slug = slugify(f"{section}-{filepath.stem}")

    # For now, tags are empty (future: parse frontmatter)
    tags: list[str] = []

    with conn.cursor() as cur:
        # UPSERT: update if slug exists, insert otherwise
        cur.execute(
            """
            INSERT INTO knowledge.kb_document (title, section, slug, body_md, tags)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (slug) DO UPDATE SET
                title = EXCLUDED.title,
                section = EXCLUDED.section,
                body_md = EXCLUDED.body_md,
                tags = EXCLUDED.tags,
                updated_at = now()
            RETURNING id, slug
            """,
            (title, section, slug, content, tags),
        )
        row = cur.fetchone()
        if row:
            doc_id, doc_slug = row
            return f"✓ {filepath.name} → {doc_slug} (id: {doc_id})", True
        return f"Failed to insert {filepath.name}", False

    return f"Unexpected error processing {filepath.name}", False


def main() -> None:
    """Ingest markdown files from input directory into knowledge.kb_document."""
    import sys

    # Parse input directory argument or use default
    input_dir_str = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_INPUT_DIR)
    input_dir = Path(input_dir_str).resolve()

    if not input_dir.exists():
        print(f"ERROR: Input directory does not exist: {input_dir}")
        sys.exit(1)

    if not input_dir.is_dir():
        print(f"ERROR: Input path is not a directory: {input_dir}")
        sys.exit(1)

    # Check for DB connection
    if psycopg is None:
        print("WARNING: psycopg not available; skipping DB ingestion")
        print("db_off: true")
        sys.exit(0)

    dsn = get_rw_dsn()
    if not dsn:
        print("WARNING: GEMATRIA_DSN not set; skipping DB ingestion")
        print("db_off: true")
        sys.exit(0)

    try:
        with psycopg.connect(dsn, autocommit=True) as conn:
            # Check if knowledge schema exists
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1
                    FROM information_schema.schemata
                    WHERE schema_name = 'knowledge'
                    """
                )
                if not cur.fetchone():
                    print("ERROR: knowledge schema does not exist. Run migration 043 first.")
                    sys.exit(1)

            # Find all markdown files
            md_files = list(input_dir.rglob("*.md"))
            if not md_files:
                print(f"WARNING: No markdown files found in {input_dir}")
                sys.exit(0)

            print(f"Ingesting {len(md_files)} markdown file(s) from {input_dir}...")

            success_count = 0
            for md_file in md_files:
                msg, success = ingest_markdown_file(md_file, input_dir, conn)
                print(msg)
                if success:
                    success_count += 1

            print(f"\n✓ Ingested {success_count}/{len(md_files)} file(s) successfully")

    except Exception as exc:
        print(f"ERROR: Database error: {exc!s}")
        print("db_off: true")
        sys.exit(0)  # Fail-soft: exit 0 on DB errors


if __name__ == "__main__":
    main()
