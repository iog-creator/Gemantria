#!/usr/bin/env python

"""
Guard: Doc Embeddings Coverage

Purpose
-------
Validate that Tier-0 AGENTS docs have embeddings in control.doc_embedding.

This guard:
- Checks that all AGENTS docs (AGENTS_ROOT + AGENTS::*) have embeddings for the target model
- Reports missing embeddings
- In STRICT mode: fails if any AGENTS doc fragment lacks embeddings
- DB-off tolerant: reports mode="db_off" if DB is unavailable

Output
------
Prints a JSON verdict to stdout:

{
  "ok": bool,
  "mode": "ready" | "db_off" | "partial" | "hint",
  "reason": "...",
  "stats": {
    "total_docs": int,
    "total_fragments": int,
    "fragments_missing_embeddings": int,
    "docs_missing_embeddings": [...],
    "model_name": "..."
  }
}
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict

# Add project root to path for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

from pmagent.db.loader import get_control_engine
from scripts.config.env import get_retrieval_lane_models


def get_embedding_model(model_name: str | None = None) -> str:
    """Get embedding model name from config or override."""
    if model_name:
        return model_name
    cfg = get_retrieval_lane_models()
    model = cfg.get("embedding_model")
    if not model:
        return "unknown"  # Will cause check to fail gracefully
    return model


def main() -> int:
    """Main guard logic."""
    verdict: Dict[str, object] = {
        "ok": False,
        "mode": "unknown",
        "reason": "",
        "stats": {},
    }

    # Check STRICT mode
    strict_mode = os.getenv("STRICT_MODE", "").upper() in ("1", "TRUE", "STRICT")

    # Get model name from env or config
    model_name = os.getenv("DOC_EMBED_MODEL") or get_embedding_model()

    try:
        engine = get_control_engine()
    except Exception as exc:  # pragma: no cover - defensive
        verdict["ok"] = False
        verdict["mode"] = "db_off"
        verdict["reason"] = f"control_engine_error: {exc}"
        verdict["stats"] = {
            "total_docs": 0,
            "total_fragments": 0,
            "fragments_missing_embeddings": 0,
            "docs_missing_embeddings": [],
            "model_name": model_name,
        }
        print(json.dumps(verdict, indent=2, sort_keys=True))
        return 0

    try:
        with engine.connect() as conn:
            # Query AGENTS docs and their fragments
            query = text(
                """
                SELECT
                    dr.doc_id,
                    dr.logical_name,
                    COUNT(DISTINCT df.id) as fragment_count,
                    COUNT(DISTINCT CASE WHEN de.id IS NOT NULL THEN df.id END) as fragments_with_embeddings
                FROM control.doc_registry dr
                INNER JOIN control.doc_fragment df ON dr.doc_id = df.doc_id
                LEFT JOIN control.doc_embedding de
                    ON de.fragment_id = df.id
                    AND de.model_name = :model_name
                WHERE dr.is_ssot = TRUE
                  AND dr.enabled = TRUE
                  AND (dr.logical_name = 'AGENTS_ROOT' OR dr.logical_name LIKE 'AGENTS::%')
                  AND df.content IS NOT NULL
                  AND df.content != ''
                GROUP BY dr.doc_id, dr.logical_name
                ORDER BY dr.logical_name
                """
            )

            rows = conn.execute(query, {"model_name": model_name}).fetchall()

            if not rows:
                verdict["ok"] = True  # No AGENTS docs to check
                verdict["mode"] = "hint"
                verdict["reason"] = "no_agents_docs_in_registry"
                verdict["stats"] = {
                    "total_docs": 0,
                    "total_fragments": 0,
                    "fragments_missing_embeddings": 0,
                    "docs_missing_embeddings": [],
                    "model_name": model_name,
                }
                print(json.dumps(verdict, indent=2, sort_keys=True))
                return 0

            # Compute stats
            total_docs = len(rows)
            total_fragments = sum(row[2] for row in rows)
            fragments_with_embeddings = sum(row[3] for row in rows)
            fragments_missing_embeddings = total_fragments - fragments_with_embeddings

            # Find docs with missing embeddings
            docs_missing_embeddings = [
                row[1]  # logical_name
                for row in rows
                if row[2] > 0 and row[3] < row[2]  # has fragments but not all have embeddings
            ]

            verdict["stats"] = {
                "total_docs": total_docs,
                "total_fragments": total_fragments,
                "fragments_missing_embeddings": fragments_missing_embeddings,
                "docs_missing_embeddings": sorted(docs_missing_embeddings),
                "model_name": model_name,
            }

            # Determine verdict
            if fragments_missing_embeddings == 0:
                verdict["ok"] = True
                verdict["mode"] = "ready"
                verdict["reason"] = "embeddings_complete"
            else:
                verdict["ok"] = False
                if strict_mode:
                    verdict["mode"] = "ready"  # STRICT mode: ready but incomplete
                    verdict["reason"] = "embeddings_incomplete_tier0"
                else:
                    verdict["mode"] = "hint"
                    verdict["reason"] = "embeddings_incomplete_hint"

    except Exception as exc:  # pragma: no cover - defensive
        verdict["ok"] = False
        verdict["mode"] = "db_off"
        verdict["reason"] = f"db_connection_error: {exc}"
        verdict["stats"] = {
            "total_docs": 0,
            "total_fragments": 0,
            "fragments_missing_embeddings": 0,
            "docs_missing_embeddings": [],
            "model_name": model_name,
        }

    print(json.dumps(verdict, indent=2, sort_keys=True))

    # Exit code: 0 for HINT mode, 1 for STRICT failures
    if strict_mode and not verdict["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
