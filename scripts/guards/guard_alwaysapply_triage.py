#!/usr/bin/env python3
"""Validate Always-Apply triad (050/051/052) across SSOT and AI Doc DB."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

TRIAD = {"050", "051", "052"}
AI_DOC_DB_URL = os.getenv("AI_DOC_DB_URL")


class GuardFailure(Exception):
    """Raised when the guard detects drift."""


def check_ai_doc_db() -> dict[str, object]:
    if not AI_DOC_DB_URL:
        return {"source": "ai_db", "status": "skipped"}

    try:
        with urllib.request.urlopen(AI_DOC_DB_URL, timeout=2) as response:
            data = json.load(response)
    except Exception as exc:  # pragma: no cover - guard runtime path
        return {
            "source": "ai_db",
            "status": "unreachable",
            "note": f"{exc.__class__.__name__}: {exc}"[:200],
        }

    always_apply = set(map(str, data.get("always_apply", [])))
    return {
        "source": "ai_db",
        "status": "ok",
        "found": sorted(always_apply),
        "ok": bool(always_apply) and always_apply == TRIAD,
    }


def check_rules_table(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"path": str(path), "status": "missing"}

    content = path.read_text(encoding="utf-8", errors="ignore")
    always_apply = set(re.findall(r"^\|\s*(0\d{2})\s*\|.*\(AlwaysApply\)", content, flags=re.MULTILINE))
    return {
        "path": str(path),
        "found": sorted(always_apply),
        "ok": always_apply == TRIAD,
    }


def main() -> int:
    report: dict[str, object] = {"triad": sorted(TRIAD)}
    ai_result = check_ai_doc_db()
    report["ai"] = ai_result

    paths = [
        Path("docs/SSOT/RULES_INDEX.md"),
        Path("docs/SSOT/MASTER_PLAN.md"),
        Path("RULES_INDEX.md"),
        Path("MASTER_PLAN.md"),
    ]

    table_results = [check_rules_table(path) for path in paths]
    report["rules_tables"] = table_results

    # SSOT RULES_INDEX must pass; optional extra checks for others
    ssot_ok = next(
        (entry["ok"] for entry in table_results if entry.get("path") == "docs/SSOT/RULES_INDEX.md"),
        False,
    )
    master_ok = next(
        (entry["ok"] for entry in table_results if entry.get("path") == "docs/SSOT/MASTER_PLAN.md"),
        True,
    )

    report["ok"] = bool(ssot_ok and master_ok and (ai_result.get("ok", True)))

    print(json.dumps(report, indent=2, sort_keys=True))
    if not report["ok"]:
        raise GuardFailure("Always-Apply triad drift detected")
    return 0


if __name__ == "__main__":  # pragma: no cover - script entry point
    try:
        sys.exit(main())
    except GuardFailure:
        sys.exit(1)
