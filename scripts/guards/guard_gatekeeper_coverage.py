#!/usr/bin/env python3
"""
PLAN-080 E97 — Guard: Gatekeeper / Guard Shim Coverage Audit

Guard semantics:

- evidence/gatekeeper_coverage.json must exist.
- JSON must be valid and contain:
    - "violation_codes": list[str]
    - "coverage": mapping[str, bool]
- Every violation code listed must appear in coverage.
- All violation codes must be marked True (covered_by_tests).

Verdict JSON:

{
  "ok": bool,
  "checks": {...},
  "counts": {...},
  "details": {...},
}
"""

import json
import pathlib
from typing import Any, Dict

ROOT = pathlib.Path(__file__).resolve().parents[2]
COVERAGE_PATH = ROOT / "evidence" / "gatekeeper_coverage.json"


def main() -> int:
    checks: Dict[str, bool] = {}
    counts: Dict[str, int] = {}
    details: Dict[str, Any] = {}

    exists = COVERAGE_PATH.exists()
    checks["coverage_exists"] = exists
    if not exists:
        verdict = {
            "ok": False,
            "checks": checks,
            "counts": counts,
            "details": {"reason": "missing_coverage_manifest", "path": str(COVERAGE_PATH)},
        }
        print(json.dumps(verdict, indent=2))
        return 1

    try:
        doc = json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        verdict = {
            "ok": False,
            "checks": {"coverage_exists": True, "coverage_json_valid": False},
            "counts": counts,
            "details": {"path": str(COVERAGE_PATH), "error": str(e)},
        }
        print(json.dumps(verdict, indent=2))
        return 1

    checks["coverage_json_valid"] = True
    codes = doc.get("violation_codes") or []
    coverage = doc.get("coverage") or {}

    if not isinstance(codes, list) or not all(isinstance(c, str) for c in codes):
        verdict = {
            "ok": False,
            "checks": {"coverage_exists": True, "coverage_json_valid": True, "codes_valid": False},
            "counts": counts,
            "details": {"path": str(COVERAGE_PATH), "reason": "invalid_violation_codes"},
        }
        print(json.dumps(verdict, indent=2))
        return 1

    checks["codes_valid"] = True
    missing_keys = [c for c in codes if c not in coverage]
    uncovered = [c for c, v in coverage.items() if not v]

    counts["violation_codes"] = len(codes)
    counts["missing_coverage_entries"] = len(missing_keys)
    counts["uncovered_codes"] = len(uncovered)

    checks["all_codes_present_in_coverage"] = len(missing_keys) == 0
    checks["all_codes_marked_covered"] = len(uncovered) == 0

    details["path"] = str(COVERAGE_PATH)
    details["missing_coverage_entries"] = missing_keys
    details["uncovered_codes"] = uncovered

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
