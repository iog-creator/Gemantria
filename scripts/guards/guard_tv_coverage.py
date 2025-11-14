#!/usr/bin/env python3
"""
PLAN-080 E96 — Guard: TV Coverage Receipt

Guard verifies:
- evidence/tv_coverage_receipt.json exists
- JSON is valid
- ok == True (all TVs passed)
- pytest_exit_code == 0

Outputs JSON verdict:

{
  "ok": bool,
  "checks": {...},
  "counts": {...},
  "details": {...}
}
"""

import json
import pathlib
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
RECEIPT_PATH = ROOT / "evidence" / "tv_coverage_receipt.json"


def main() -> int:
    checks: dict[str, bool] = {}
    counts: dict[str, int] = {}
    details: dict[str, Any] = {}

    exists = RECEIPT_PATH.exists()
    checks["receipt_exists"] = exists
    if not exists:
        verdict = {
            "ok": False,
            "checks": checks,
            "counts": counts,
            "details": {"reason": "missing_receipt", "path": str(RECEIPT_PATH)},
        }
        print(json.dumps(verdict, indent=2))
        return 1

    try:
        doc = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        verdict = {
            "ok": False,
            "checks": {"receipt_exists": True, "receipt_json_valid": False},
            "counts": counts,
            "details": {
                "path": str(RECEIPT_PATH),
                "error": str(e),
            },
        }
        print(json.dumps(verdict, indent=2))
        return 1

    checks["receipt_json_valid"] = True
    ok_flag = bool(doc.get("ok"))
    checks["tv_suite_ok"] = ok_flag

    exit_code = doc.get("pytest_exit_code")
    checks["pytest_exit_zero"] = exit_code == 0
    counts["pytest_exit_code"] = int(exit_code) if isinstance(exit_code, int) else -1

    details["path"] = str(RECEIPT_PATH)
    details["suite"] = doc.get("suite")
    details["timestamp"] = doc.get("timestamp")

    ok = all(checks.values())
    verdict = {
        "ok": ok,
        "checks": checks,
        "counts": counts,
        "details": details,
    }
    print(json.dumps(verdict, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
