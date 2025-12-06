#!/usr/bin/env python
"""
Check if DMS ingestion work is needed (fast-path for routine housekeeping).

Purpose
-------
Quickly determine if classification or embedding work is needed before
running expensive operations. Returns exit code 0 if work is needed, 1 if not.

This enables fast-path for routine housekeeping when no new work exists.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

from pmagent.db.loader import get_control_engine


def check_work_needed() -> dict:
    """
    Check if classification or embedding work is needed.

    Returns:
        Dict with: {needs_classification: bool, needs_embeddings: bool, counts: {...}}
    """
    try:
        engine = get_control_engine()
    except Exception as exc:
        # If DB unavailable, assume work is needed (fail-safe)
        return {
            "needs_classification": True,
            "needs_embeddings": True,
            "error": str(exc),
            "counts": {},
        }

    with engine.connect() as conn:
        # Check unclassified fragments (must match classify_fragments.py query)
        unclassified_result = conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM control.doc_fragment f
                JOIN control.doc_registry d ON f.doc_id = d.doc_id
                WHERE (f.meta IS NULL OR f.meta = '{}'::jsonb)
                """
            )
        )
        unclassified_count = unclassified_result.fetchone()[0]

        # Check unembedded fragments (for default model)
        # Get default embedding model name
        from scripts.config.env import get_retrieval_lane_models

        try:
            cfg = get_retrieval_lane_models()
            model_name = cfg.get("embedding_model", "granite-embedding:278m")
        except Exception:
            model_name = "granite-embedding:278m"

        unembedded_result = conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM control.doc_fragment df
                INNER JOIN control.doc_registry dr ON df.doc_id = dr.doc_id
                LEFT JOIN control.doc_embedding de
                    ON de.fragment_id = df.id
                    AND de.model_name = :model_name
                WHERE de.id IS NULL
                  AND df.content IS NOT NULL
                  AND df.content != ''
                  AND dr.enabled = true
                """
            ),
            {"model_name": model_name},
        )
        unembedded_count = unembedded_result.fetchone()[0]

        return {
            "needs_classification": unclassified_count > 0,
            "needs_embeddings": unembedded_count > 0,
            "counts": {
                "unclassified": unclassified_count,
                "unembedded": unembedded_count,
            },
        }


def main() -> int:
    """CLI entry point. Exit 0 if work needed, 1 if not."""
    result = check_work_needed()

    if result.get("error"):
        # DB unavailable - assume work needed (fail-safe)
        print(f"[WARN] DB check failed: {result['error']}", file=sys.stderr)
        return 0

    needs_classification = result["needs_classification"]
    needs_embeddings = result["needs_embeddings"]
    counts = result["counts"]

    if needs_classification or needs_embeddings:
        print(
            f"[INFO] Work needed: {counts['unclassified']} unclassified, {counts['unembedded']} unembedded",
            file=sys.stderr,
        )
        return 0  # Work needed
    else:
        print("[INFO] No DMS work needed (all fragments classified and embedded)", file=sys.stderr)
        return 1  # No work needed


if __name__ == "__main__":
    raise SystemExit(main())
