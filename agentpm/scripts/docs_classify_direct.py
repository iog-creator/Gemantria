"""
Direct document classification script.

Allows direct classification of documents without requiring preview file editing.
Updates control.kb_document with canonical/archive_candidate status.

Usage:
    python agentpm/scripts/docs_classify_direct.py --canonical path1 path2 ...
    python agentpm/scripts/docs_classify_direct.py --archive path1 path2 ...
    python agentpm/scripts/docs_classify_direct.py --batch-review  # Review current batch
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

# Add repo root to path for imports
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import psycopg
from scripts.config.env import get_rw_dsn


def classify_documents(paths: List[str], status: str, is_canonical: bool) -> tuple[int, int]:
    """
    Classify documents in the database.

    Args:
        paths: List of document paths to classify
        status: Status value ('canonical' or 'archive_candidate')
        is_canonical: Boolean flag for is_canonical field

    Returns:
        (updated_count, missing_count)
    """
    dsn = get_rw_dsn()
    if not dsn:
        raise SystemExit("ERROR: GEMATRIA_DSN not set")

    updated = 0
    missing = 0

    with psycopg.connect(dsn) as conn:
        conn.autocommit = False
        with conn.cursor() as cur:
            for path in paths:
                cur.execute(
                    """
                    UPDATE control.kb_document
                    SET is_canonical = %s, status = %s
                    WHERE path = %s
                    """,
                    (is_canonical, status, path),
                )
                if cur.rowcount == 0:
                    missing += 1
                    print(f"⚠  Not found in DB: {path}")
                else:
                    updated += cur.rowcount
                    print(f"✓  Updated: {path} → {status}")

        conn.commit()

    return updated, missing


def review_current_batch() -> None:
    """Review and classify the current unreviewed batch using heuristics."""
    import json

    batch_file = REPO_ROOT / "share" / "exports" / "docs-control" / "unreviewed-batch.json"
    if not batch_file.exists():
        raise SystemExit(f"ERROR: Batch file not found: {batch_file}")

    with batch_file.open() as f:
        batch = json.load(f)

    items = batch.get("items", [])
    if not items:
        print("No unreviewed items in current batch")
        return

    print(f"\n📋 Reviewing batch of {len(items)} documents\n")
    print("=" * 80)

    canonical_paths = []
    archive_paths = []

    # Heuristics from DM-002:
    # 1. Prefer paths under docs/SSOT/ as canonical
    # 2. AGENTS.md files should be canonical
    # 3. .cursor/rules/ files should be canonical
    # 4. docs/runbooks/ should be canonical
    # 5. Root-level status/walkthrough docs are archive candidates
    # 6. Temporary/outdated docs are archive candidates

    for item in items:
        path = item["path"]
        doc_type = item.get("doc_type", "unknown")
        # title = item.get("title", "")  # Not used in classification logic

        # Classification logic (DM-002 heuristics)
        # 1. Prefer paths under docs/SSOT/ as canonical
        # 2. AGENTS.md files should be canonical
        # 3. .cursor/rules/ files should be canonical
        # 4. docs/runbooks/ should be canonical
        # 5. Root-level status/walkthrough docs are archive candidates

        if path.startswith("docs/SSOT/"):
            canonical_paths.append(path)
            print(f"✓ CANONICAL: {path} (SSOT directory)")
        elif path.endswith("AGENTS.md"):
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
        elif path in ["SEMANTIC_SEARCH_STATUS.md", "walkthrough.md"]:
            archive_paths.append(path)
            print(f"→ ARCHIVE: {path} (Status/walkthrough doc)")
        elif path in ["NEXT_STEPS.md", "PROGRESS_SUMMARY.md", "MASTER_PLAN.md"]:
            # Planning docs - keep as canonical for active reference
            canonical_paths.append(path)
            print(f"✓ CANONICAL: {path} (Planning doc)")
        elif path.startswith("MCP_") and path.endswith(".md"):
            # MCP registration/docs - canonical
            canonical_paths.append(path)
            print(f"✓ CANONICAL: {path} (MCP documentation)")
        else:
            # Default: mark as canonical if it's a reference doc and not in archive
            if path.endswith(".md") and not path.startswith("archive/"):
                canonical_paths.append(path)
                print(f"✓ CANONICAL: {path} (Default: reference doc)")
            else:
                archive_paths.append(path)
                print(f"→ ARCHIVE: {path} (Default: archive candidate)")

    print("\n" + "=" * 80)
    print("\n📊 Summary:")
    print(f"   Canonical: {len(canonical_paths)}")
    print(f"   Archive: {len(archive_paths)}")

    if canonical_paths or archive_paths:
        response = input("\n❓ Apply these classifications? (yes/no): ").strip().lower()
        if response in ["yes", "y"]:
            if canonical_paths:
                updated, missing = classify_documents(canonical_paths, "canonical", True)
                print(f"\n✓ Classified {updated} as canonical ({missing} not found)")

            if archive_paths:
                updated, missing = classify_documents(archive_paths, "archive_candidate", False)
                print(f"✓ Classified {updated} as archive candidates ({missing} not found)")

            print("\n✅ Classification complete! Run 'pmagent docs dashboard-refresh' to update exports.")
        else:
            print("\n❌ Classification cancelled")
    else:
        print("\n⚠  No documents to classify")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Direct document classification")
    parser.add_argument("--canonical", nargs="+", help="Mark paths as canonical")
    parser.add_argument("--archive", nargs="+", help="Mark paths as archive candidates")
    parser.add_argument("--batch-review", action="store_true", help="Review and classify current batch")

    args = parser.parse_args()

    if args.batch_review:
        review_current_batch()
    elif args.canonical:
        updated, missing = classify_documents(args.canonical, "canonical", True)
        print(f"\n✓ Updated {updated} documents ({missing} not found)")
    elif args.archive:
        updated, missing = classify_documents(args.archive, "archive_candidate", False)
        print(f"\n✓ Updated {updated} documents ({missing} not found)")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
