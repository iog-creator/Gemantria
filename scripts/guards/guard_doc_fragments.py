#!/usr/bin/env python

"""
Guard: Doc Fragments Coverage

Purpose
-------
Validate that Tier-0 AGENTS docs have fragments in control.doc_fragment.

This guard:
- Checks that all AGENTS docs (AGENTS_ROOT + AGENTS::*) have at least one fragment
- Reports missing/zero fragments
- In STRICT mode: fails if any AGENTS doc has zero fragments
- DB-off tolerant: reports mode="db_off" if DB is unavailable

Output
------
Prints a JSON verdict to stdout:

{
  "ok": bool,
  "mode": "ready" | "db_off" | "partial" | "hint",
  "reason": "...",
  "stats": {
    "agents_docs_count": int,
    "docs_with_fragments": int,
    "docs_with_zero_fragments": int,
    "total_fragments": int,
    "missing_docs": [...]
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

    try:
        engine = get_control_engine()
    except Exception as exc:  # pragma: no cover - defensive
        verdict["ok"] = False
        verdict["mode"] = "db_off"
        verdict["reason"] = f"control_engine_error: {exc}"
        verdict["stats"] = {
            "agents_docs_count": 0,
            "docs_with_fragments": 0,
            "docs_with_zero_fragments": 0,
            "total_fragments": 0,
            "missing_docs": [],
        }
        print(json.dumps(verdict, indent=2, sort_keys=True))
        return 0

    try:
        with engine.connect() as conn:
            # Query AGENTS docs from registry
            rows = conn.execute(
                text(
                    """
                    SELECT doc_id, logical_name
                    FROM control.doc_registry
                    WHERE is_ssot = TRUE
                    AND enabled = TRUE
                    AND (logical_name = 'AGENTS_ROOT' OR logical_name LIKE 'AGENTS::%')
                    ORDER BY logical_name
                    """
                )
            ).fetchall()

            agents_docs = {row[0]: row[1] for row in rows}
            agents_docs_count = len(agents_docs)

            if not agents_docs:
                verdict["ok"] = True  # No AGENTS docs to check
                verdict["mode"] = "hint"
                verdict["reason"] = "no_agents_docs_in_registry"
                verdict["stats"] = {
                    "agents_docs_count": 0,
                    "docs_with_fragments": 0,
                    "docs_with_zero_fragments": 0,
                    "total_fragments": 0,
                    "missing_docs": [],
                }
                print(json.dumps(verdict, indent=2, sort_keys=True))
                return 0

            # Count fragments per doc
            fragment_counts = {}
            total_fragments = 0

            for doc_id, logical_name in agents_docs.items():
                rows = conn.execute(
                    text(
                        """
                        SELECT COUNT(*) as frag_count
                        FROM control.doc_fragment
                        WHERE doc_id = :doc_id
                        AND doc_id IS NOT NULL
                        """
                    ),
                    {"doc_id": doc_id},
                ).fetchone()

                count = rows[0] if rows else 0
                fragment_counts[doc_id] = count
                total_fragments += count

            # Compute stats
            docs_with_fragments = sum(1 for count in fragment_counts.values() if count > 0)
            docs_with_zero_fragments = sum(1 for count in fragment_counts.values() if count == 0)
            missing_docs = [agents_docs[doc_id] for doc_id, count in fragment_counts.items() if count == 0]

            verdict["stats"] = {
                "agents_docs_count": agents_docs_count,
                "docs_with_fragments": docs_with_fragments,
                "docs_with_zero_fragments": docs_with_zero_fragments,
                "total_fragments": total_fragments,
                "missing_docs": sorted(missing_docs),
            }

            # Determine verdict
            if docs_with_zero_fragments == 0:
                verdict["ok"] = True
                verdict["mode"] = "ready"
                verdict["reason"] = "agents_fragments_complete"
            else:
                verdict["ok"] = False
                if strict_mode:
                    verdict["mode"] = "partial"
                    verdict["reason"] = "agents_fragments_incomplete"
                else:
                    verdict["mode"] = "hint"
                    verdict["reason"] = "agents_fragments_incomplete_hint"

    except Exception as exc:  # pragma: no cover - defensive
        verdict["ok"] = False
        verdict["mode"] = "db_off"
        verdict["reason"] = f"db_connection_error: {exc}"
        verdict["stats"] = {
            "agents_docs_count": 0,
            "docs_with_fragments": 0,
            "docs_with_zero_fragments": 0,
            "total_fragments": 0,
            "missing_docs": [],
        }

    print(json.dumps(verdict, indent=2, sort_keys=True))

    # Exit code: 0 for HINT mode, 1 for STRICT failures
    if strict_mode and not verdict["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
