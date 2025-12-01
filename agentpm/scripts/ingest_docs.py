#!/usr/bin/env python3
"""
SSOT Documentation Ingestion Script

E2E Pipeline (Reality Check #1): Ingests curated SSOT docs into control.doc_sources and control.doc_sections.
Tolerates db_off (no DB required; fails gracefully with clear message).

Usage:
    python -m agentpm.scripts.ingest_docs
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

try:
    import psycopg
except ImportError:
    psycopg = None

from scripts.config.env import get_rw_dsn

# REPO_ROOT: from agentpm/scripts/ingest_docs.py, go up 2 levels to repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

# Curated subset of SSOT files to ingest
SSOT_FILES = [
    REPO_ROOT / "docs" / "SSOT" / "MASTER_PLAN.md",
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "docs" / "SSOT" / "graph.schema.json",
]


def split_markdown_sections(content: str) -> list[tuple[str | None, str]]:
    """
    Split markdown content into sections based on headings (## or ###).
    Returns list of (section_title, section_body) tuples.
    """
    sections: list[tuple[str | None, str]] = []
    lines = content.split("\n")
    current_title: str | None = None
    current_body: list[str] = []

    for line in lines:
        # Check for heading (## or ###)
        heading_match = re.match(r"^#{2,3}\s+(.+)$", line)
        if heading_match:
            # Save previous section if any
            if current_body:
                sections.append((current_title, "\n".join(current_body).strip()))
            # Start new section
            current_title = heading_match.group(1).strip()
            current_body = []
        else:
            current_body.append(line)

    # Add final section
    if current_body:
        sections.append((current_title, "\n".join(current_body).strip()))

    # If no sections found, treat entire content as one section
    if not sections:
        sections.append((None, content.strip()))

    return sections


def extract_tags_from_path(filepath: Path) -> list[str]:
    """Extract tags based on file path and name."""
    tags = ["ssot"]
    rel_path = filepath.relative_to(REPO_ROOT)

    if "SSOT" in rel_path.parts:
        tags.append("ssot")
    if filepath.name == "MASTER_PLAN.md":
        tags.append("plan")
    elif filepath.name == "AGENTS.md":
        tags.append("agents")
    elif filepath.suffix == ".json":
        tags.append("schema")

    return tags


def ingest_file(filepath: Path, conn: Any) -> tuple[str, bool]:
    """Ingest a single file into the database."""
    if not filepath.exists():
        return f"File not found: {filepath}", False

    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as exc:
        return f"Failed to read {filepath}: {exc!s}", False

    # Extract title from first line or filename
    title = filepath.stem.replace("_", " ").replace("-", " ").title()
    if filepath.suffix == ".md":
        # Try to extract title from first H1
        h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if h1_match:
            title = h1_match.group(1).strip()
    elif filepath.suffix == ".json":
        # For JSON, use filename as title
        title = filepath.stem

    path_str = str(filepath.relative_to(REPO_ROOT))
    tags = extract_tags_from_path(filepath)

    with conn.cursor() as cur:
        # Insert or update doc_source
        cur.execute(
            """
            INSERT INTO control.doc_sources (path, title, tags)
            VALUES (%s, %s, %s)
            ON CONFLICT (path) DO UPDATE SET
                title = EXCLUDED.title,
                tags = EXCLUDED.tags
            RETURNING id
            """,
            (path_str, title, tags),
        )
        source_id = cur.fetchone()[0]

        # Delete existing sections for this source (idempotent re-ingestion)
        cur.execute("DELETE FROM control.doc_sections WHERE source_id = %s", (source_id,))

        # Split content into sections
        if filepath.suffix == ".md":
            sections = split_markdown_sections(content)
        else:
            # For non-markdown (e.g., JSON), treat entire content as one section
            sections = [(None, content)]

        # Insert sections
        for order_idx, (section_title, section_body) in enumerate(sections, start=1):
            if not section_body.strip():
                continue
            cur.execute(
                """
                INSERT INTO control.doc_sections (source_id, section_title, body, order_index)
                VALUES (%s, %s, %s, %s)
                """,
                (source_id, section_title, section_body, order_idx),
            )

        return f"✓ {filepath.name} → {len(sections)} section(s)", True


def main() -> None:
    """Ingest SSOT docs into control.doc_sources and control.doc_sections."""
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
            # Check if control schema exists
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1
                    FROM information_schema.schemata
                    WHERE schema_name = 'control'
                    """
                )
                if not cur.fetchone():
                    print("ERROR: control schema does not exist. Run migration 040 first.")
                    sys.exit(1)

            # Check if tables exist
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'control'
                    AND table_name IN ('doc_sources', 'doc_sections')
                    """
                )
                found_tables = {row[0] for row in cur.fetchall()}
                if found_tables != {"doc_sources", "doc_sections"}:
                    print("ERROR: doc_sources or doc_sections tables do not exist. Run migration 044 first.")
                    sys.exit(1)

            # Find files to ingest
            files_to_ingest = []
            for filepath in SSOT_FILES:
                if filepath.exists():
                    files_to_ingest.append(filepath)
                else:
                    print(f"WARNING: SSOT file not found: {filepath}")

            if not files_to_ingest:
                print("WARNING: No SSOT files found to ingest")
                sys.exit(0)

            print(f"Ingesting {len(files_to_ingest)} SSOT file(s)...")

            success_count = 0
            for filepath in files_to_ingest:
                msg, success = ingest_file(filepath, conn)
                print(msg)
                if success:
                    success_count += 1

            print(f"\n✓ Ingested {success_count}/{len(files_to_ingest)} file(s) successfully")

    except Exception as exc:
        print(f"ERROR: Database error: {exc!s}")
        print("db_off: true")
        sys.exit(0)  # Fail-soft: exit 0 on DB errors


if __name__ == "__main__":
    main()
