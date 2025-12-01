#!/usr/bin/env python

"""
Classify document fragments with AI metadata.

Purpose
-------
Walk through control.doc_fragment and classify fragments with AI-derived metadata,
storing results in the meta JSONB column.

This script:
- Selects fragments for documents matching criteria (e.g., PDFs)
- Calls classify_fragment() for each unclassified fragment
- Updates the meta column with classification results

This script does NOT:
- Modify source files
- Generate embeddings (that's a separate pipeline)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add project root to path for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

from agentpm.db.loader import get_control_engine
from agentpm.kb.classify import classify_fragment

REPO_ROOT = Path(__file__).resolve().parents[2]


def classify_fragments(
    dry_run: bool = False,
    pdf_only: bool = True,
    limit: int | None = None,
) -> dict:
    """
    Classify document fragments with AI metadata.

    Args:
        dry_run: If True, compute classifications but don't write to DB
        pdf_only: If True, only process PDF documents (default: True for Phase 3)
        limit: Limit number of fragments processed (for debugging)

    Returns:
        Dictionary with stats: {fragments_processed, fragments_classified, dry_run}
    """
    try:
        engine = get_control_engine()
    except Exception as exc:
        if dry_run:
            print(f"[DRY-RUN] Would connect to DB (error: {exc})", file=sys.stderr)
            return {
                "fragments_processed": 0,
                "fragments_classified": 0,
                "dry_run": True,
                "error": str(exc),
            }
        raise RuntimeError(f"Failed to connect to control-plane DB: {exc}") from exc

    fragments_processed = 0
    fragments_classified = 0

    with engine.connect() as conn:
        # Query for fragments that need classification
        # Select fragments where meta is NULL or empty JSONB
        where_clause = """
            WHERE (f.meta IS NULL OR f.meta::text = '{}'::text)
        """

        if pdf_only:
            where_clause += """
                AND d.repo_path LIKE 'docs/%.pdf'
            """

        query = text(
            f"""
            SELECT
                f.id as fragment_id,
                f.doc_id,
                f.fragment_index,
                f.content,
                d.logical_name,
                d.repo_path
            FROM control.doc_fragment f
            JOIN control.doc_registry d ON f.doc_id = d.doc_id
            {where_clause}
            ORDER BY d.repo_path, f.fragment_index
            """
        )

        if limit:
            query = text(str(query) + f" LIMIT {limit}")

        rows = conn.execute(query).fetchall()

        for fragment_id, doc_id, fragment_index, content, logical_name, repo_path in rows:
            fragments_processed += 1

            # Classify fragment
            try:
                meta = classify_fragment(content or "", repo_path or "")
            except Exception as exc:
                print(
                    f"[WARN] Classification failed for {logical_name} fragment {fragment_index}: {exc}",
                    file=sys.stderr,
                )
                continue

            if not meta:
                # Empty classification (LM unavailable or parsing failed)
                if dry_run:
                    print(
                        f"[DRY-RUN] {logical_name} fragment {fragment_index}: would classify (LM unavailable)",
                        file=sys.stderr,
                    )
                else:
                    # Store empty dict to mark as "attempted"
                    meta = {}

            if dry_run:
                print(
                    f"[DRY-RUN] {logical_name} fragment {fragment_index}: would store meta={json.dumps(meta)}",
                    file=sys.stderr,
                )
                fragments_classified += 1
                continue

            # Update fragment with classification
            conn.execute(
                text(
                    """
                    UPDATE control.doc_fragment
                    SET meta = :meta
                    WHERE id = :fragment_id
                    """
                ),
                {
                    "fragment_id": fragment_id,
                    "meta": json.dumps(meta),
                },
            )

            conn.commit()
            fragments_classified += 1
            print(
                f"[OK] {logical_name} fragment {fragment_index}: classified (subsystem={meta.get('subsystem', 'N/A')}, role={meta.get('doc_role', 'N/A')})",
                file=sys.stderr,
            )

    return {
        "fragments_processed": fragments_processed,
        "fragments_classified": fragments_classified,
        "dry_run": dry_run,
    }


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Classify document fragments with AI metadata")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute classifications but don't write to DB",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of fragments processed",
    )
    parser.add_argument(
        "--all-docs",
        action="store_true",
        help="Process all documents (not just PDFs)",
    )

    args = parser.parse_args()

    pdf_only = not args.all_docs

    try:
        result = classify_fragments(
            dry_run=args.dry_run,
            pdf_only=pdf_only,
            limit=args.limit,
        )

        # Emit JSON summary
        print(json.dumps(result, indent=2))

        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
