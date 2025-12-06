#!/usr/bin/env python

"""
GPU-Accelerated Fragment Classification Script

Purpose
-------
High-performance version of classify_fragments.py that uses GPU acceleration
when available, with CPU multiprocessing fallback.

Key Improvements:
- Processes fragments in batches instead of one-by-one
- Uses GPU-accelerated operations when CUDA available
- Falls back to multiprocessing on CPU
- 10-100x faster than LLM-per-fragment approach

Usage:
    python scripts/housekeeping_gpu/classify_fragments_gpu.py [--dry-run] [--limit N]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# Add project root to path for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

from pmagent.db.loader import get_control_engine
from scripts.housekeeping_gpu.gpu_classifier import classify_batch_gpu

REPO_ROOT = Path(__file__).resolve().parents[2]

# Batch size for classification (large batches for GPU efficiency)
DEFAULT_CLASSIFICATION_BATCH = 1000
# Batch size for DB writes (smaller for transaction safety)
DEFAULT_DB_BATCH = 50


def classify_fragments_gpu(
    dry_run: bool = False,
    pdf_only: bool = True,
    limit: int | None = None,
    classification_batch: int = DEFAULT_CLASSIFICATION_BATCH,
    db_batch: int = DEFAULT_DB_BATCH,
    show_progress: bool = True,
) -> dict:
    """
    GPU-accelerated document fragment classification.

    Args:
        dry_run: If True, compute classifications but don't write to DB
        pdf_only: If True, only process PDF documents
        limit: Limit number of fragments processed
        classification_batch: Batch size for GPU classification
        db_batch: Batch size for DB writes
        show_progress: Show progress indicators

    Returns:
        Dictionary with stats
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
        where_clause = """
            WHERE (f.meta IS NULL OR f.meta = '{}'::jsonb)
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
        total_rows = len(rows)

        if total_rows == 0:
            if show_progress:
                print("[INFO] No fragments need classification", file=sys.stderr)
            return {
                "fragments_processed": 0,
                "fragments_classified": 0,
                "dry_run": dry_run,
                "message": "No unclassified fragments found",
            }

        if show_progress:
            print(
                f"[INFO] Processing {total_rows:,} fragments (GPU batch: {classification_batch}, DB batch: {db_batch})",
                file=sys.stderr,
            )

        start_time = time.time()
        last_progress_time = start_time

        # Process in classification batches for GPU efficiency
        for batch_start in range(0, total_rows, classification_batch):
            batch_end = min(batch_start + classification_batch, total_rows)
            batch_rows = rows[batch_start:batch_end]

            # Prepare batch for classification
            batch_fragments = [
                {
                    "fragment_id": row[0],
                    "doc_id": row[1],
                    "fragment_index": row[2],
                    "content": row[3] or "",
                    "logical_name": row[4],
                    "repo_path": row[5] or "",
                }
                for row in batch_rows
            ]

            # GPU-accelerated batch classification
            try:
                batch_meta = classify_batch_gpu(batch_fragments)
            except Exception as exc:
                if show_progress:
                    print(f"[ERROR] Batch classification failed: {exc}", file=sys.stderr)
                continue

            # Write results in smaller DB batches
            db_updates = []
            for fragment, meta in zip(batch_fragments, batch_meta):
                fragments_processed += 1

                if dry_run:
                    fragments_classified += 1
                    continue

                db_updates.append(
                    {
                        "fragment_id": fragment["fragment_id"],
                        "meta": json.dumps(meta),
                    }
                )
                fragments_classified += 1

                # Commit DB batch when full
                if len(db_updates) >= db_batch:
                    update_query = text(
                        """
                        UPDATE control.doc_fragment
                        SET meta = CAST(:meta AS jsonb)
                        WHERE id = :fragment_id
                        """
                    )
                    conn.execute(update_query, db_updates)
                    conn.commit()
                    db_updates.clear()

            # Commit remaining updates
            if db_updates and not dry_run:
                update_query = text(
                    """
                    UPDATE control.doc_fragment
                    SET meta = CAST(:meta AS jsonb)
                    WHERE id = :fragment_id
                    """
                )
                conn.execute(update_query, db_updates)
                conn.commit()
                db_updates.clear()

            # Progress indicator
            current_time = time.time()
            if show_progress and (
                batch_end % 1000 == 0 or batch_end == total_rows or (current_time - last_progress_time) >= 10.0
            ):
                elapsed = current_time - start_time
                rate = fragments_processed / elapsed if elapsed > 0 else 0
                remaining = (total_rows - fragments_processed) / rate if rate > 0 else 0
                print(
                    f"[PROGRESS] {fragments_processed:,}/{total_rows:,} ({fragments_processed / total_rows * 100:.1f}%) | "
                    f"Rate: {rate:.1f}/s | ETA: {remaining / 60:.1f}m",
                    file=sys.stderr,
                )
                last_progress_time = current_time

    # Final stats
    elapsed = time.time() - start_time
    if show_progress:
        print(
            f"\n[COMPLETE] Classified {fragments_classified:,} fragments in {elapsed:.1f}s "
            f"({fragments_classified / elapsed:.1f}/s)",
            file=sys.stderr,
        )

    return {
        "fragments_processed": fragments_processed,
        "fragments_classified": fragments_classified,
        "dry_run": dry_run,
        "elapsed_seconds": elapsed,
        "rate_per_second": fragments_classified / elapsed if elapsed > 0 else 0,
    }


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="GPU-accelerated document fragment classification")
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
    parser.add_argument(
        "--classification-batch",
        type=int,
        default=DEFAULT_CLASSIFICATION_BATCH,
        help=f"Batch size for GPU classification (default: {DEFAULT_CLASSIFICATION_BATCH})",
    )
    parser.add_argument(
        "--db-batch",
        type=int,
        default=DEFAULT_DB_BATCH,
        help=f"Batch size for DB updates (default: {DEFAULT_DB_BATCH})",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress indicators",
    )

    args = parser.parse_args()

    pdf_only = not args.all_docs

    try:
        result = classify_fragments_gpu(
            dry_run=args.dry_run,
            pdf_only=pdf_only,
            limit=args.limit,
            classification_batch=args.classification_batch,
            db_batch=args.db_batch,
            show_progress=not args.no_progress,
        )

        # Emit JSON summary
        print(json.dumps(result, indent=2))

        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
