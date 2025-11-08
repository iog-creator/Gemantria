# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
populate_document_sections.py — Parse and track document sections in AI database

Analyzes markdown documents and populates the document_sections table
for AI-assisted document management and maintenance.
"""

import hashlib
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Load environment variables
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from infra.env_loader import ensure_env_loaded

ensure_env_loaded()

import psycopg


def parse_markdown_sections(content: str) -> List[Tuple[str, int, str]]:
    """
    Parse markdown content and extract section hierarchy.

    Returns list of (section_name, level, parent_section) tuples.
    """
    sections = []
    current_parent = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None}

    lines = content.split("\n")
    for line in lines:
        # Match headers (# ## ### ####)
        header_match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
        if header_match:
            level = len(header_match.group(1))
            title = header_match.group(2).strip()

            # Clean title (remove emojis and extra formatting)
            title = re.sub(r"[^\w\s\-&]", "", title).strip()

            # Determine parent section
            parent = current_parent.get(level - 1)

            sections.append((title, level, parent))

            # Update current parent for this level
            current_parent[level] = title

    return sections


def calculate_content_hash(text: str) -> str:
    """Calculate SHA-256 hash of text content."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def extract_section_content(content: str, section_name: str) -> str:
    """
    Extract content for a specific section from markdown.
    This is a simplified implementation - in practice you'd want more sophisticated parsing.
    """
    # Simple approach: find the section header and get content until next header
    lines = content.split("\n")
    section_content = []
    in_section = False

    for line in lines:
        if re.match(rf"^#{1, 6}\s+{re.escape(section_name)}", line.strip()):
            in_section = True
            continue
        elif in_section and re.match(r"^#{1,6}\s+", line.strip()):
            # Next header found, stop
            break
        elif in_section:
            section_content.append(line)

    return "\n".join(section_content).strip()


def populate_document_sections_with_conn(doc_path: str, doc_name: str, conn) -> None:
    """Populate document_sections table for a given document using provided connection."""

    if not Path(doc_path).exists():
        print(f"❌ Document not found: {doc_path}")
        return

    content = Path(doc_path).read_text(encoding="utf-8")
    sections = parse_markdown_sections(content)

    print(f"📄 Processing {doc_name} with {len(sections)} sections...")

    with conn.cursor() as cur:
        for section_name, level, parent in sections:
            # Extract section content for hash and word count
            section_content = extract_section_content(content, section_name)
            content_hash = calculate_content_hash(section_content)
            word_count = count_words(section_content)

            # Insert/update section tracking
            cur.execute(
                """
                SELECT update_document_section(%s, %s, %s, %s, %s, %s, %s)
            """,
                (doc_name, section_name, doc_path, level, parent, content_hash, word_count),
            )

            print(f"  ✅ {section_name} (level {level}, {word_count} words)")

    print(f"✅ Successfully populated {len(sections)} sections for {doc_name}")


def populate_document_sections(doc_path: str, doc_name: str) -> None:
    """Populate document_sections table for a given document."""

    if not Path(doc_path).exists():
        print(f"❌ Document not found: {doc_path}")
        return

    content = Path(doc_path).read_text(encoding="utf-8")
    sections = parse_markdown_sections(content)

    print(f"📄 Processing {doc_name} with {len(sections)} sections...")

    with psycopg.connect(os.environ["GEMATRIA_DSN"]) as conn:
        with conn.cursor() as cur:
            for section_name, level, parent in sections:
                # Extract section content for hash and word count
                section_content = extract_section_content(content, section_name)
                content_hash = calculate_content_hash(section_content)
                word_count = count_words(section_content)

                # Insert/update section tracking
                cur.execute(
                    """
                    SELECT update_document_section(%s, %s, %s, %s, %s, %s, %s)
                """,
                    (doc_name, section_name, doc_path, level, parent, content_hash, word_count),
                )

                print(f"  ✅ {section_name} (level {level}, {word_count} words)")

        conn.commit()
    print(f"✅ Successfully populated {len(sections)} sections for {doc_name}")


def main():
    """Main function to populate document sections."""

    import argparse

    parser = argparse.ArgumentParser(description="Populate document sections in database")
    parser.add_argument("--doc-path", help="Path to document file")
    parser.add_argument("--doc-name", help="Name of document in database")
    parser.add_argument("--all", action="store_true", help="Process all default documents")

    args = parser.parse_args()

    if args.doc_path and args.doc_name:
        # Process single document
        documents = [(args.doc_path, args.doc_name)]
    elif args.all:
        # Process all default documents
        documents = [
            ("docs/SSOT/GEMATRIA_MASTER_REFERENCE.md", "GEMATRIA_MASTER_REFERENCE.md"),
            ("AGENTS.md", "AGENTS.md"),
            ("docs/README.md", "README.md"),
        ]
    else:
        # Default behavior - process all
        documents = [
            ("docs/SSOT/GEMATRIA_MASTER_REFERENCE.md", "GEMATRIA_MASTER_REFERENCE.md"),
            ("AGENTS.md", "AGENTS.md"),
            ("docs/README.md", "README.md"),
        ]

    # Use a single connection for all operations
    with psycopg.connect(os.environ["GEMATRIA_DSN"]) as conn:
        for doc_path, doc_name in documents:
            try:
                populate_document_sections_with_conn(doc_path, doc_name, conn)
            except Exception as e:
                print(f"❌ Error processing {doc_name}: {e}")
                conn.rollback()  # Rollback on error to maintain connection
        conn.commit()  # Commit all changes at the end


if __name__ == "__main__":
    main()
