#!/usr/bin/env python

"""
Guard: Docs DB SSOT

Purpose
-------
Validate that the pmagent control-plane DMS (control-plane doc registry in Postgres) is in sync with the
canonical documentation files in the repo:

- AGENTS.md
- MASTER_PLAN.md
- RULES_INDEX.md
- docs/SSOT/** (SSOT docs)
- docs/runbooks/** (runbooks)

This guard is:

- DB-off tolerant: if the DB is unreachable, it reports mode="db_off" and
  ok=False, but exits 0 in HINT mode (non-blocking), exits 1 in STRICT mode (blocking).
- Read-only: it never mutates the database.
- Mode-aware: Supports HINT (advisory) and STRICT (fail-closed) modes via STRICT_MODE env var.

Output
------
Prints a JSON verdict to stdout of the form:

{
  "ok": bool,
  "mode": "ready" | "db_off" | "partial",
  "reason": "...",
  "details": {
    "missing_registry_docs": [...],
    "missing_versions": [...],
    "total_local_docs": int,
    "total_registry_docs": int
  },
  "hints": [...]  # Present in HINT mode when ok=false
}

Exit codes:
- HINT mode: Always 0 (non-blocking)
- STRICT mode: 0 if ok=true, 1 if ok=false (blocking)
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, List

# Add project root to path for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

from pmagent.db.loader import get_control_engine
from scripts.governance import ingest_docs_to_db as ingest_mod


REPO_ROOT = ingest_mod.REPO_ROOT


def _is_strict_mode() -> bool:
    """Determine if running in STRICT mode."""
    return os.getenv("STRICT_MODE", "0") == "1" or os.getenv("CI") == "true"


@dataclass
class LocalDoc:
    logical_name: str
    path: Path


def discover_local_docs() -> List[LocalDoc]:
    """Reuse ingest_docs_to_db's discovery logic to find local docs."""
    docs: List[LocalDoc] = []
    for t in ingest_mod.CANONICAL_DOCS:
        if t.repo_path.is_file():
            docs.append(LocalDoc(logical_name=t.logical_name, path=t.repo_path))

    for t in ingest_mod.iter_additional_docs():
        if t.repo_path.is_file():
            docs.append(LocalDoc(logical_name=t.logical_name, path=t.repo_path))

    return docs


def main() -> int:
    strict_mode = _is_strict_mode()
    verdict: Dict[str, object] = {
        "ok": False,
        "mode": "db_off",
        "reason": "",
        "details": {},
        "generated_at": datetime.now(UTC).isoformat(),
    }

    local_docs = discover_local_docs()
    local_names = {d.logical_name for d in local_docs}

    if not local_docs:
        verdict["ok"] = False
        verdict["mode"] = "partial"
        verdict["reason"] = "no_local_docs_found"
        verdict["details"] = {
            "missing_registry_docs": [],
            "missing_versions": [],
            "total_local_docs": 0,
            "total_registry_docs": 0,
        }
        if not strict_mode:
            verdict["hints"] = ["No local docs found. Run docs ingestion to populate registry."]
        print(json.dumps(verdict, indent=2, sort_keys=True))
        return 1 if strict_mode else 0

    try:
        engine = get_control_engine()
    except Exception as exc:  # pragma: no cover - defensive
        verdict["ok"] = False
        verdict["mode"] = "db_off"
        verdict["reason"] = f"control_engine_error: {exc}"
        verdict["details"] = {
            "missing_registry_docs": sorted(local_names),
            "missing_versions": sorted(local_names),
            "total_local_docs": len(local_names),
            "total_registry_docs": 0,
        }
        if not strict_mode:
            verdict["hints"] = [
                f"Database unreachable: {exc}",
                "In HINT mode, this is non-blocking. Set STRICT_MODE=1 to require DB access.",
            ]
        print(json.dumps(verdict, indent=2, sort_keys=True))
        return 1 if strict_mode else 0

    missing_registry: List[str] = []
    missing_versions: List[str] = []
    total_registry = 0

    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    """
                    SELECT logical_name, doc_id
                    FROM control.doc_registry
                    WHERE logical_name = ANY(:names)
                    """
                ),
                {"names": list(local_names)},
            ).fetchall()

            registry_map: Dict[str, str] = {row[0]: row[1] for row in rows}
            total_registry = len(registry_map)

            for ln in local_names:
                if ln not in registry_map:
                    missing_registry.append(ln)

            if registry_map:
                rows = conn.execute(
                    text(
                        """
                        SELECT d.logical_name
                        FROM control.doc_registry d
                        LEFT JOIN control.doc_version v
                          ON v.doc_id = d.doc_id
                        WHERE d.logical_name = ANY(:names)
                        GROUP BY d.logical_name
                        HAVING COUNT(v.id) = 0
                        """
                    ),
                    {"names": list(local_names)},
                ).fetchall()
                missing_versions = sorted(row[0] for row in rows)
    except Exception as exc:  # pragma: no cover - defensive
        verdict["ok"] = False
        verdict["mode"] = "db_off"
        verdict["reason"] = f"db_connection_error: {exc}"
        verdict["details"] = {
            "missing_registry_docs": sorted(local_names),
            "missing_versions": sorted(local_names),
            "total_local_docs": len(local_names),
            "total_registry_docs": 0,
        }
        if not strict_mode:
            verdict["hints"] = [
                f"Database connection error: {exc}",
                "In HINT mode, this is non-blocking. Set STRICT_MODE=1 to require DB access.",
            ]
        print(json.dumps(verdict, indent=2, sort_keys=True))
        return 1 if strict_mode else 0

    verdict["details"] = {
        "missing_registry_docs": sorted(missing_registry),
        "missing_versions": missing_versions,
        "total_local_docs": len(local_names),
        "total_registry_docs": total_registry,
    }

    if not missing_registry and not missing_versions:
        verdict["ok"] = True
        verdict["mode"] = "ready"
        verdict["reason"] = "docs_db_ssot_in_sync"
    else:
        verdict["ok"] = False
        verdict["mode"] = "partial"
        verdict["reason"] = "docs_db_ssot_mismatch"
        if not strict_mode:
            hints = []
            if missing_registry:
                hints.append(
                    f"{len(missing_registry)} docs missing from registry: {', '.join(missing_registry[:5])}"
                    + (f" and {len(missing_registry) - 5} more" if len(missing_registry) > 5 else "")
                )
            if missing_versions:
                hints.append(
                    f"{len(missing_versions)} docs missing versions: {', '.join(missing_versions[:5])}"
                    + (f" and {len(missing_versions) - 5} more" if len(missing_versions) > 5 else "")
                )
            hints.append("Run 'make governance.ingest.docs' to sync docs to registry.")
            verdict["hints"] = hints

    print(json.dumps(verdict, indent=2, sort_keys=True))
    return 0 if verdict["ok"] or not strict_mode else 1


if __name__ == "__main__":
    raise SystemExit(main())
