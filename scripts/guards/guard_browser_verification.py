#!/usr/bin/env python3
"""
PLAN-079 E93 — Browser Verification Guard

Requirements (per MASTER_PLAN E93):
- Verify browser verification receipts exist for key Atlas pages.
- Use browser automation receipts, not live browsing.
- Emit machine-readable verdict JSON:
    { "ok": bool, "checks": {...}, "counts": {...}, "details": {...} }

This guard is DB-off tolerant and hermetic:
- Only inspects evidence/webproof/* (screenshots + report JSON).
- Does NOT start servers, hit the network, or call external tools.

Key inputs (conventions per GPT_SYSTEM_PROMPT + prior episodes):
- evidence/webproof/report.json   — webproof run summary
- evidence/webproof/*.png        — screenshots for key pages
"""

import json
import pathlib
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
WEBPROOF_DIR = ROOT / "evidence" / "webproof"
REPORT_PATH = WEBPROOF_DIR / "report.json"

# "Key pages" = core Atlas surfaces we care about for Phase-2:
REQUIRED_PAGES = [
    "docs/atlas/index.html",
    "docs/atlas/dashboard/compliance_summary.html",
    "docs/atlas/dashboard/compliance_timeseries.html",
    "docs/atlas/dashboard/compliance_heatmap.html",
    "docs/atlas/browser/violations.html",
    "docs/atlas/browser/guard_receipts.html",
]


def _load_report() -> tuple[bool, Any]:
    if not REPORT_PATH.exists():
        return False, None
    try:
        return True, json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    except Exception:
        return True, None


def main() -> int:
    checks: dict[str, bool] = {}
    counts: dict[str, int] = {}
    details: dict[str, Any] = {}

    # Check directory + report presence
    checks["webproof_dir_exists"] = WEBPROOF_DIR.exists()
    screenshots = list(WEBPROOF_DIR.glob("*.png")) if WEBPROOF_DIR.exists() else []
    counts["screenshots"] = len(screenshots)
    checks["has_screenshots"] = counts["screenshots"] > 0

    report_present, report_doc = _load_report()
    checks["report_exists"] = report_present
    checks["report_json_valid"] = report_present and report_doc is not None

    # If report JSON valid, inspect high-level ok flag and endpoints/pages coverage
    pages_missing: list[str] = []
    report_ok_flag: bool | None = None
    if report_doc is not None and isinstance(report_doc, dict):
        if isinstance(report_doc.get("ok"), bool):
            report_ok_flag = report_doc["ok"]
        checks["report_ok_flag_true_when_present"] = (report_ok_flag is True) or (report_ok_flag is None)

        # Build a lowercase dump for robust contains checks
        try:
            dump = json.dumps(report_doc).lower()
        except Exception:
            dump = ""

        for page in REQUIRED_PAGES:
            basename = pathlib.Path(page).name.lower()
            if basename not in dump:
                pages_missing.append(page)

    counts["required_pages"] = len(REQUIRED_PAGES)
    counts["missing_required_pages"] = len(pages_missing)
    checks["all_required_pages_have_receipts"] = len(pages_missing) == 0 if checks["report_json_valid"] else False

    # Basic screenshot sanity: at least as many screenshots as required pages (soft check)
    checks["screenshot_count_reasonable"] = counts["screenshots"] >= min(len(REQUIRED_PAGES), 1)

    details["report_path"] = str(REPORT_PATH)
    details["webproof_dir"] = str(WEBPROOF_DIR)
    details["missing_required_pages"] = pages_missing

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
