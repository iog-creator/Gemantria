#!/usr/bin/env python

"""
Ingest document content into control.doc_fragment.

Purpose
-------
Read documents from control.doc_registry and chunk them into fragments
stored in control.doc_fragment. This is the first step in making docs
RAG-ready (embeddings come later).

The script:
- Queries control.doc_registry + control.doc_version for enabled SSOT docs
- Focuses on AGENTS docs (Tier-0) by default
- Chunks markdown into fragments (headings, paragraphs, code blocks)
- Upserts fragments into control.doc_fragment

This script does NOT:
- Generate embeddings (that's a separate pipeline)
- Modify source files
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List

# Add project root to path for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

import pdfplumber

from agentpm.db.loader import get_control_engine


REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class Fragment:
    """Represents a single document fragment."""

    fragment_index: int
    fragment_type: str  # "heading", "paragraph", "code"
    content: str


def normalize_content(content: str) -> str:
    """
    Normalize document content.

    - Strip BOM
    - Normalize newlines to \n
    """
    # Strip BOM
    if content.startswith("\ufeff"):
        content = content[1:]
    # Normalize newlines
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    return content


def chunk_pdf(file_path: Path) -> List[Fragment]:
    """
    Chunk PDF content into fragments (one fragment per page).

    Args:
        file_path: Path to PDF file

    Returns:
        List of Fragment objects with fragment_type='page' and fragment_index=0..N-1
    """
    fragments: List[Fragment] = []
    fragment_index = 0

    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                # Extract text from page
                text_content = page.extract_text()
                if text_content:
                    # Normalize content
                    text_content = normalize_content(text_content)
                    fragments.append(
                        Fragment(
                            fragment_index=fragment_index,
                            fragment_type="page",
                            content=text_content,
                        )
                    )
                    fragment_index += 1
    except Exception as exc:
        print(f"[WARN] Failed to extract PDF {file_path}: {exc}", file=sys.stderr)
        # Return empty list on error (don't crash the pipeline)
        return []

    return fragments


def chunk_markdown(content: str) -> List[Fragment]:
    """
    Chunk markdown content into fragments.

    Fragments are:
    - Headings: lines starting with # (any level)
    - Code blocks: content between ``` fences
    - Paragraphs: everything else (grouped by blank lines)

    Returns fragments in document order with fragment_index 0..N-1.
    """
    content = normalize_content(content)
    lines = content.split("\n")
    fragments: List[Fragment] = []
    fragment_index = 0
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check for heading
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            level = len(heading_match.group(1))
            text_content = heading_match.group(2).strip()
            fragments.append(
                Fragment(
                    fragment_index=fragment_index,
                    fragment_type="heading",
                    content=line,
                )
            )
            fragment_index += 1
            i += 1
            continue

        # Check for code fence
        if line.strip().startswith("```"):
            code_lines = [line]
            i += 1
            # Collect until closing fence
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if i < len(lines):
                code_lines.append(lines[i])  # Include closing fence
                i += 1
            fragments.append(
                Fragment(
                    fragment_index=fragment_index,
                    fragment_type="code",
                    content="\n".join(code_lines),
                )
            )
            fragment_index += 1
            continue

        # Collect paragraph (non-empty lines until blank line or heading/code)
        if line.strip():
            para_lines = [line]
            i += 1
            while i < len(lines):
                next_line = lines[i]
                # Stop at blank line, heading, or code fence
                if not next_line.strip():
                    break
                if re.match(r"^#{1,6}\s+", next_line):
                    break
                if next_line.strip().startswith("```"):
                    break
                para_lines.append(next_line)
                i += 1
            para_content = "\n".join(para_lines).strip()
            if para_content:
                fragments.append(
                    Fragment(
                        fragment_index=fragment_index,
                        fragment_type="paragraph",
                        content=para_content,
                    )
                )
                fragment_index += 1
            continue

        # Skip blank lines
        i += 1

    return fragments


def ingest_doc_content(
    dry_run: bool = False,
    only_agents: bool = True,
    limit: int | None = None,
) -> dict:
    """
    Ingest document content into control.doc_fragment.

    Args:
        dry_run: If True, compute chunks but don't write to DB
        only_agents: If True, only process AGENTS docs (default: True)
        limit: Limit number of docs processed (for debugging)

    Returns:
        Dictionary with stats: {docs_processed, fragments_written, dry_run}
    """
    try:
        engine = get_control_engine()
    except Exception as exc:
        if dry_run:
            print(f"[DRY-RUN] Would connect to DB (error: {exc})", file=sys.stderr)
            return {"docs_processed": 0, "fragments_written": 0, "dry_run": True, "error": str(exc)}
        raise RuntimeError(f"Failed to connect to control-plane DB: {exc}") from exc

    docs_processed = 0
    fragments_written = 0

    with engine.connect() as conn:
        # Query for enabled SSOT docs
        # Focus on AGENTS docs if only_agents=True
        if only_agents:
            where_clause = """
                WHERE d.is_ssot = TRUE
                AND d.enabled = TRUE
                AND (d.logical_name = 'AGENTS_ROOT' OR d.logical_name LIKE 'AGENTS::%')
            """
        else:
            where_clause = """
                WHERE d.is_ssot = TRUE
                AND d.enabled = TRUE
            """

        # Get latest version per doc_id
        query = text(
            f"""
            SELECT DISTINCT ON (d.doc_id)
                d.doc_id,
                d.logical_name,
                d.repo_path,
                v.id as version_id,
                v.content_hash
            FROM control.doc_registry d
            INNER JOIN control.doc_version v ON v.doc_id = d.doc_id
            {where_clause}
            ORDER BY d.doc_id, v.id DESC
            """
        )

        if limit:
            query = text(str(query) + f" LIMIT {limit}")

        rows = conn.execute(query).fetchall()

        for doc_id, logical_name, repo_path, version_id, content_hash in rows:
            # Resolve file path
            file_path = REPO_ROOT / repo_path
            if not file_path.is_file():
                print(
                    f"[WARN] File not found: {repo_path} (logical_name={logical_name})",
                    file=sys.stderr,
                )
                continue

            # Read and chunk based on file type
            try:
                if file_path.suffix.lower() == ".pdf":
                    # PDF: chunk by page
                    fragments = chunk_pdf(file_path)
                else:
                    # Markdown or other text: read as text and chunk
                    content = file_path.read_text(encoding="utf-8")
                    fragments = chunk_markdown(content)
            except Exception as exc:
                print(f"[WARN] Failed to read {repo_path}: {exc}", file=sys.stderr)
                continue

            if dry_run:
                print(f"[DRY-RUN] {logical_name}: {len(fragments)} fragments", file=sys.stderr)
                docs_processed += 1
                fragments_written += len(fragments)
                continue

            # Delete existing fragments for this (doc_id, version_id)
            conn.execute(
                text(
                    """
                    DELETE FROM control.doc_fragment
                    WHERE doc_id = :doc_id AND version_id = :version_id
                    """
                ),
                {"doc_id": doc_id, "version_id": version_id},
            )

            # Insert new fragments
            for frag in fragments:
                # Generate UUID for fragment id (compatible with existing table structure)
                conn.execute(
                    text(
                        """
                        INSERT INTO control.doc_fragment
                            (doc_id, version_id, fragment_index, fragment_type, content)
                        VALUES
                            (:doc_id, :version_id, :fragment_index, :fragment_type, :content)
                        """
                    ),
                    {
                        "doc_id": doc_id,
                        "version_id": version_id,
                        "fragment_index": frag.fragment_index,
                        "fragment_type": frag.fragment_type,
                        "content": frag.content,
                    },
                )

            conn.commit()
            docs_processed += 1
            fragments_written += len(fragments)
            print(f"[OK] {logical_name}: {len(fragments)} fragments", file=sys.stderr)

    return {
        "docs_processed": docs_processed,
        "fragments_written": fragments_written,
        "dry_run": dry_run,
    }


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Ingest document content into control.doc_fragment")
    parser.add_argument("--dry-run", action="store_true", help="Compute chunks but don't write to DB")
    parser.add_argument("--limit", type=int, help="Limit number of docs processed")
    parser.add_argument(
        "--only-agents",
        action="store_true",
        default=True,
        help="Only process AGENTS docs (default: True)",
    )
    parser.add_argument(
        "--all-docs",
        action="store_true",
        help="Process all enabled SSOT docs (overrides --only-agents)",
    )

    args = parser.parse_args()

    only_agents = args.only_agents and not args.all_docs

    try:
        result = ingest_doc_content(
            dry_run=args.dry_run,
            only_agents=only_agents,
            limit=args.limit,
        )

        # Emit JSON summary
        import json

        print(json.dumps(result, indent=2))

        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
