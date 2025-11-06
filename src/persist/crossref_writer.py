#!/usr/bin/env python3
"""
Cross-reference Writer

Handles persistence of OSIS-normalized verse cross-references extracted from enrichment insights.
"""

import os
from typing import List, Dict, Any

import psycopg

from src.infra.structured_logger import get_logger, log_json

LOG = get_logger("gematria.crossref_writer")

GEMATRIA_DSN = os.getenv("GEMATRIA_DSN")


def write_crossrefs(run_id: str, enriched_nouns: List[Dict[str, Any]]) -> int:
    """
    Write cross-references from enriched nouns to the database.

    Args:
        run_id: Unique identifier for this pipeline run
        enriched_nouns: List of enriched noun dictionaries with crossrefs

    Returns:
        Number of cross-reference records written
    """
    if not GEMATRIA_DSN:
        log_json(LOG, 30, "crossref_persistence_skipped", reason="no GEMATRIA_DSN")
        return 0

    if not enriched_nouns:
        log_json(LOG, 20, "crossref_persistence_skipped", reason="no enriched nouns")
        return 0

    crossrefs = []
    for noun in enriched_nouns:
        noun_crossrefs = noun.get("enrichment", {}).get("crossrefs", [])
        if not noun_crossrefs:
            continue

        # Get source reference info
        sources = noun.get("sources", [])
        if not sources:
            continue

        osis_ref_src = sources[0].get("ref", "")
        surface = noun.get("surface", "")
        confidence = noun.get("confidence", 0.0)

        if not osis_ref_src or not surface:
            continue

        # Build cross-reference records
        for ref in noun_crossrefs:
            crossrefs.append(
                {
                    "run_id": run_id,
                    "osis_ref_src": osis_ref_src,
                    "surface": surface,
                    "target_osis": ref.get("osis", ""),
                    "target_label": ref.get("label", ""),
                    "confidence": confidence,
                }
            )

    if not crossrefs:
        log_json(LOG, 20, "crossref_persistence_skipped", reason="no crossrefs found")
        return 0

    # Persist to database
    try:
        with psycopg.connect(GEMATRIA_DSN) as conn:
            with conn.cursor() as cur:
                # Insert cross-references
                cur.executemany(
                    """INSERT INTO gematria.enrichment_crossrefs
                       (run_id, osis_ref_src, surface, target_osis, target_label, confidence)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    [
                        (
                            cr["run_id"],
                            cr["osis_ref_src"],
                            cr["surface"],
                            cr["target_osis"],
                            cr["target_label"],
                            cr["confidence"],
                        )
                        for cr in crossrefs
                    ],
                )

            conn.commit()

        log_json(LOG, 20, "crossrefs_persisted", count=len(crossrefs), run_id=run_id)
        return len(crossrefs)

    except Exception as e:
        log_json(LOG, 40, "crossref_persistence_failed", error=str(e), run_id=run_id)
        return 0


def get_crossref_count(run_id: str) -> int:
    """
    Get the count of cross-references for a given run_id.

    Args:
        run_id: Pipeline run identifier

    Returns:
        Number of cross-reference records for this run
    """
    if not GEMATRIA_DSN:
        return 0

    try:
        with psycopg.connect(GEMATRIA_DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM gematria.enrichment_crossrefs WHERE run_id = %s", (run_id,))
                result = cur.fetchone()
                return result[0] if result else 0

    except Exception as e:
        log_json(LOG, 30, "crossref_count_query_failed", error=str(e), run_id=run_id)
        return 0


def cleanup_run_crossrefs(run_id: str) -> int:
    """
    Clean up cross-references for a given run_id (useful for retries).

    Args:
        run_id: Pipeline run identifier

    Returns:
        Number of records deleted
    """
    if not GEMATRIA_DSN:
        return 0

    try:
        with psycopg.connect(GEMATRIA_DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM gematria.enrichment_crossrefs WHERE run_id = %s", (run_id,))
                deleted_count = cur.rowcount
            conn.commit()

        if deleted_count > 0:
            log_json(LOG, 20, "crossrefs_cleaned", run_id=run_id, deleted=deleted_count)

        return deleted_count

    except Exception as e:
        log_json(LOG, 30, "crossref_cleanup_failed", error=str(e), run_id=run_id)
        return 0
