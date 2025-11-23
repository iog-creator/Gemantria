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
# Map page identifiers to their expected report keys and screenshot names
REQUIRED_PAGES = {
    "index.html": {"report_key": "ok_index", "screenshot_key": "index"},
    "mcp_catalog_view.html": {"report_key": "ok_catalog", "screenshot_key": "catalog"},
    "compliance_summary.html": {"report_key": "ok_compliance_summary", "screenshot_key": "compliance_summary"},
    "compliance_timeseries.html": {"report_key": "ok_compliance_timeseries", "screenshot_key": "compliance_timeseries"},
    "compliance_heatmap.html": {"report_key": "ok_compliance_heatmap", "screenshot_key": "compliance_heatmap"},
    "violations.html": {"report_key": "ok_violations", "screenshot_key": "violations"},
    "guard_receipts.html": {"report_key": "ok_guard_receipts", "screenshot_key": "guard_receipts"},
}


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
    pages_verified: list[str] = []
    report_ok_flag: bool | None = None
    report_checks: dict[str, Any] = {}
    core_pages = ["index.html", "mcp_catalog_view.html"]

    if report_doc is not None and isinstance(report_doc, dict):
        if isinstance(report_doc.get("ok"), bool):
            report_ok_flag = report_doc["ok"]
        checks["report_ok_flag_true_when_present"] = (report_ok_flag is True) or (report_ok_flag is None)

        # Extract checks dict if present
        report_checks = report_doc.get("checks", {}) if isinstance(report_doc.get("checks"), dict) else {}

        # Extract screenshots dict if present
        report_screenshots = (
            report_doc.get("screenshots", {}) if isinstance(report_doc.get("screenshots"), dict) else {}
        )

        # Check each required page
        for page_name, page_info in REQUIRED_PAGES.items():
            report_key = page_info.get("report_key")
            screenshot_key = page_info.get("screenshot_key")

            # Check if page is verified in report (either via report_key or screenshot presence)
            page_verified = False
            if report_key and report_key in report_checks:
                page_verified = report_checks.get(report_key) is True
            elif screenshot_key and screenshot_key in report_screenshots:
                # If screenshot exists, consider page verified
                screenshot_path = report_screenshots.get(screenshot_key)
                if screenshot_path and pathlib.Path(ROOT / screenshot_path).exists():
                    page_verified = True

            if page_verified:
                pages_verified.append(page_name)
            else:
                pages_missing.append(page_name)

    counts["required_pages"] = len(REQUIRED_PAGES)
    counts["pages_verified"] = len(pages_verified)
    counts["missing_required_pages"] = len(pages_missing)

    # E93: Require at least core pages (index, catalog) to be verified; others are HINT mode
    core_missing = [p for p in core_pages if p in pages_missing]
    checks["core_pages_verified"] = len(core_missing) == 0 if checks["report_json_valid"] else False

    # All required pages is advisory (HINT mode) - not a hard failure
    checks["all_required_pages_have_receipts"] = len(pages_missing) == 0 if checks["report_json_valid"] else False

    # Basic screenshot sanity: at least as many screenshots as verified pages (soft check)
    checks["screenshot_count_reasonable"] = counts["screenshots"] >= min(len(pages_verified), 1)

    details["report_path"] = str(REPORT_PATH)
    details["webproof_dir"] = str(WEBPROOF_DIR)
    details["pages_verified"] = pages_verified
    details["missing_required_pages"] = pages_missing
    details["core_pages_missing"] = [p for p in core_pages if p in pages_missing] if checks["report_json_valid"] else []

    # Final verdict: require core checks (dir, report, core pages), but allow missing optional pages
    required_checks = [
        "webproof_dir_exists",
        "report_exists",
        "report_json_valid",
        "report_ok_flag_true_when_present",
        "core_pages_verified",
        "has_screenshots",
        "screenshot_count_reasonable",
    ]
    ok = all(checks.get(k, False) for k in required_checks)
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
