#!/usr/bin/env python3
"""
Bulk document classification script.

Classifies all unreviewed documents in control.kb_document using DM-002 heuristics.
This is a batch operation that processes all unreviewed documents at once.

Usage:
    python agentpm/scripts/docs_classify_bulk.py [--dry-run] [--limit N]
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Tuple

# Add repo root to path for imports
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import psycopg
from scripts.config.env import get_rw_dsn


def classify_unreviewed_documents(dry_run: bool = False, limit: int | None = None) -> Tuple[int, int, int]:
    """
    Classify all unreviewed documents using DM-002 heuristics.

    Returns:
        (canonical_count, archive_count, skipped_count)
    """
    dsn = get_rw_dsn()
    if not dsn:
        raise SystemExit("ERROR: GEMATRIA_DSN not set")

    canonical_paths: List[str] = []
    archive_paths: List[str] = []
    skipped_paths: List[str] = []

    with psycopg.connect(dsn) as conn:
        # Fetch all unreviewed documents
        limit_sql = f"LIMIT {limit}" if limit else ""
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT path, title, doc_type
                FROM control.kb_document
                WHERE status = 'unreviewed'
                ORDER BY path
                {limit_sql}
                """
            )
            rows = cur.fetchall()

        print(f"\n📋 Processing {len(rows)} unreviewed documents\n")
        print("=" * 80)

        # Apply DM-002 heuristics
        for path, _title, doc_type in rows:
            doc_type = doc_type or "unknown"

            # Heuristics from DM-002:
            # 1. Prefer paths under docs/SSOT/ as canonical
            # 2. AGENTS.md files should be canonical
            # 3. .cursor/rules/ files should be canonical
            # 4. docs/runbooks/ should be canonical
            # 5. Root-level status/walkthrough docs are archive candidates
            # 6. Files under archive/ are archive candidates
            # 7. Empty or very small files may be archive candidates

            if path.startswith("docs/SSOT/"):
                canonical_paths.append(path)
                print(f"✓ CANONICAL: {path} (SSOT directory)")
            elif path.endswith("AGENTS.md") or path.endswith("/AGENTS.md"):
                canonical_paths.append(path)
                print(f"✓ CANONICAL: {path} (AGENTS.md file)")
            elif path.startswith(".cursor/rules/"):
                canonical_paths.append(path)
                print(f"✓ CANONICAL: {path} (Rule file)")
            elif path.startswith("docs/runbooks/"):
                canonical_paths.append(path)
                print(f"✓ CANONICAL: {path} (Runbook)")
            elif doc_type == "ssot":
                canonical_paths.append(path)
                print(f"✓ CANONICAL: {path} (SSOT doc_type)")
            elif path.startswith("archive/"):
                archive_paths.append(path)
                print(f"→ ARCHIVE: {path} (Archive directory)")
            elif path in ["SEMANTIC_SEARCH_STATUS.md", "walkthrough.md", "walkthrough.md.resolved"]:
                archive_paths.append(path)
                print(f"→ ARCHIVE: {path} (Status/walkthrough doc)")
            elif path in ["NEXT_STEPS.md", "PROGRESS_SUMMARY.md", "MASTER_PLAN.md", "RULES_INDEX.md"]:
                canonical_paths.append(path)
                print(f"✓ CANONICAL: {path} (Planning/governance doc)")
            elif path.startswith("MCP_") and path.endswith(".md"):
                canonical_paths.append(path)
                print(f"✓ CANONICAL: {path} (MCP documentation)")
            elif path.startswith("docs/ADRs/"):
                canonical_paths.append(path)
                print(f"✓ CANONICAL: {path} (ADR)")
            elif path.startswith("docs/analysis/"):
                # Analysis docs are usually canonical reference material
                canonical_paths.append(path)
                print(f"✓ CANONICAL: {path} (Analysis doc)")
            elif path.startswith("docs/SSOT/"):
                canonical_paths.append(path)
                print(f"✓ CANONICAL: {path} (SSOT)")
            elif path.endswith(".md") and not path.startswith("archive/"):
                # Default: mark as canonical if it's a reference doc and not in archive
                canonical_paths.append(path)
                print(f"✓ CANONICAL: {path} (Default: reference doc)")
            else:
                archive_paths.append(path)
                print(f"→ ARCHIVE: {path} (Default: archive candidate)")

        print("\n" + "=" * 80)
        print("\n📊 Summary:")
        print(f"   Canonical: {len(canonical_paths)}")
        print(f"   Archive: {len(archive_paths)}")
        print(f"   Skipped: {len(skipped_paths)}")

        if dry_run:
            print("\n🔍 DRY RUN - No changes made")
            return len(canonical_paths), len(archive_paths), len(skipped_paths)

        # Apply classifications
        if canonical_paths or archive_paths:
            with conn.cursor() as cur:
                if canonical_paths:
                    for path in canonical_paths:
                        cur.execute(
                            """
                            UPDATE control.kb_document
                            SET is_canonical = TRUE, status = 'canonical'
                            WHERE path = %s AND status = 'unreviewed'
                            """,
                            (path,),
                        )
                    print(f"\n✓ Classified {len(canonical_paths)} as canonical")

                if archive_paths:
                    for path in archive_paths:
                        cur.execute(
                            """
                            UPDATE control.kb_document
                            SET is_canonical = FALSE, status = 'archive_candidate'
                            WHERE path = %s AND status = 'unreviewed'
                            """,
                            (path,),
                        )
                    print(f"✓ Classified {len(archive_paths)} as archive candidates")

            conn.commit()
            print("\n✅ Classification complete!")
        else:
            print("\n⚠  No documents to classify")

    return len(canonical_paths), len(archive_paths), len(skipped_paths)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Bulk classify unreviewed documents")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--limit", type=int, help="Limit number of documents to process")

    args = parser.parse_args()

    try:
        canonical, archive, skipped = classify_unreviewed_documents(dry_run=args.dry_run, limit=args.limit)
        print(f"\n📈 Final counts: {canonical} canonical, {archive} archive, {skipped} skipped")
        if not args.dry_run:
            print("\n💡 Next step: Run 'pmagent docs dashboard-refresh' to update exports.")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
