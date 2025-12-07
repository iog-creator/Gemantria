#!/usr/bin/env python

"""

Guard: DB SSOT for Cursor Rules

Purpose

-------

Validate that control.rule_definition / control.rule_source are in sync with:

- .cursor/rules/*.mdc

- RULES_INDEX.md

This is intentionally minimal for the first pass:

- It checks that every rule file has a corresponding rule_definition row.

- It checks that at least one rule_source row exists for each rule.

- It returns a JSON verdict to stdout with ok/mode/reason.

Modes

-----

- ok: True/False

- mode: "ready" | "db_off" | "partial"

This script is DB-off tolerant: if the DB is unavailable, it reports mode=db_off

with ok=False but exits with status 0 in HINT posture. STRICT posture wiring

can be added later via environment variables and Makefile targets.

"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

# Add project root to path for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

from pmagent.db.loader import get_control_engine

REPO_ROOT = Path(__file__).resolve().parents[2]

CURSOR_RULES_DIR = REPO_ROOT / ".cursor" / "rules"


def main() -> int:
    verdict: Dict[str, object] = {
        "ok": False,
        "mode": "db_off",
        "reason": "",
        "details": {},
    }
    # Discover local rules
    rule_files = sorted(CURSOR_RULES_DIR.glob("*.mdc"))
    rule_ids = []
    for path in rule_files:
        stem = path.stem
        parts = stem.split("-", 1)
        rule_id = parts[0]
        rule_ids.append(rule_id)
    try:
        engine = get_control_engine()
    except Exception as exc:  # pragma: no cover - defensive
        verdict["ok"] = False
        verdict["mode"] = "db_off"
        verdict["reason"] = f"control_engine_error: {exc}"
        print(json.dumps(verdict, indent=2, sort_keys=True))
        return 0

    if not rule_ids:
        verdict["ok"] = False
        verdict["mode"] = "partial"
        verdict["reason"] = "no_local_rules_found"
        print(json.dumps(verdict, indent=2, sort_keys=True))
        return 0

    missing_definitions: List[str] = []
    missing_sources: List[str] = []
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT rule_id FROM control.rule_definition WHERE rule_id = ANY(:ids)"),
                {"ids": rule_ids},
            ).fetchall()
            present_ids = {row[0] for row in rows}
            for rid in rule_ids:
                if rid not in present_ids:
                    missing_definitions.append(rid)
            rows = conn.execute(
                text(
                    """
            SELECT DISTINCT rule_id
            FROM control.rule_source
            WHERE rule_id = ANY(:ids)
            """
                ),
                {"ids": rule_ids},
            ).fetchall()
            present_source_ids = {row[0] for row in rows}
            for rid in rule_ids:
                if rid not in present_source_ids:
                    missing_sources.append(rid)
    except Exception as exc:
        verdict["ok"] = False
        verdict["mode"] = "db_off"
        verdict["reason"] = f"db_connection_error: {exc}"
        print(json.dumps(verdict, indent=2, sort_keys=True))
        return 0

    verdict["details"] = {
        "local_rule_count": len(rule_ids),
        "missing_definitions": sorted(missing_definitions),
        "missing_sources": sorted(missing_sources),
    }
    if not missing_definitions and not missing_sources:
        verdict["ok"] = True
        verdict["mode"] = "ready"
        verdict["reason"] = "db_ssot_in_sync"
    else:
        verdict["ok"] = False
        verdict["mode"] = "partial"
        verdict["reason"] = "db_ssot_mismatch"
    print(json.dumps(verdict, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
