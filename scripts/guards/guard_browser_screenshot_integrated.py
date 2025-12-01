#!/usr/bin/env python3
"""
PLAN-080 E99 — Integrated Browser + Screenshot Verification Guard

Aggregates PLAN-079 guards (E91-E95) into a single integrated verdict:
- E91: Receipts index guard (guard_atlas_guard_receipts.py)
- E92: Screenshot manifest guard (guard_screenshot_manifest.py)
- E93: Browser verification guard (guard_browser_verification.py)
- E94: Tagproof screenshots guard (guard_tagproof_screenshots.py)
- E95: Atlas links guard (guard_atlas_links.py)

Outputs integrated JSON verdict:
{
  "ok": bool,
  "checks": {
    "receipts_guard_ok": bool,
    "screenshot_manifest_guard_ok": bool,
    "browser_verification_guard_ok": bool,
    "tagproof_screenshots_guard_ok": bool,
    "atlas_links_guard_ok": bool
  },
  "counts": {
    "guards_total": 5,
    "guards_ok": int,
    "guards_failed": int,
    "broken_links": int,
    "missing_screenshots": int
  },
  "details": {
    "receipts_guard": {...},
    "screenshot_manifest_guard": {...},
    "browser_verification_guard": {...},
    "tagproof_screenshots_guard": {...},
    "atlas_links_guard": {...}
  }
}

This guard is hermetic and DB-off tolerant: only invokes underlying guards via subprocess.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "evidence"

# Guard script paths
GUARD_SCRIPTS = {
    "receipts_guard": ROOT / "scripts" / "guards" / "guard_atlas_guard_receipts.py",
    "screenshot_manifest_guard": ROOT / "scripts" / "guards" / "guard_screenshot_manifest.py",
    "browser_verification_guard": ROOT / "scripts" / "guards" / "guard_browser_verification.py",
    "tagproof_screenshots_guard": ROOT / "scripts" / "guards" / "guard_tagproof_screenshots.py",
    "atlas_links_guard": ROOT / "scripts" / "guards" / "guard_atlas_links.py",
}


def _truncate_details(details: dict[str, Any], max_size: int = 1200) -> dict[str, Any]:
    """Truncate large detail fields to keep output manageable."""
    truncated = {}
    for k, v in details.items():
        s = json.dumps(v) if not isinstance(v, str) else v
        if len(s) > max_size:
            truncated[k] = f"<truncated {len(s)} chars>"
        else:
            truncated[k] = v
    return truncated


def _run_guard(script_path: Path) -> tuple[bool, dict[str, Any] | None, str | None]:
    """
    Run a guard script and parse its JSON output.

    Returns:
        (ok, verdict_dict, error_message)
    """
    if not script_path.exists():
        return False, None, f"guard script not found: {script_path}"

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return False, None, "guard script timed out after 60s"
    except Exception as e:
        return False, None, f"guard script execution failed: {e}"

    if not result.stdout.strip():
        return False, None, "guard script produced no output"

    try:
        verdict = json.loads(result.stdout.strip())
        ok = verdict.get("ok", False) if isinstance(verdict, dict) else False
        return ok, verdict, None
    except json.JSONDecodeError as e:
        return False, None, f"guard output is not valid JSON: {e}"


def _extract_counts(verdict: dict[str, Any] | None, guard_name: str) -> dict[str, int]:
    """Extract relevant counts from a guard verdict."""
    if not verdict or not isinstance(verdict, dict):
        return {}

    counts = verdict.get("counts", {})
    extracted = {}

    # Extract broken links from atlas_links_guard
    if guard_name == "atlas_links_guard":
        extracted["broken_links"] = counts.get("broken_internal_links", 0) + counts.get(
            "unmarked_external_links", 0
        )

    # Extract missing screenshots from screenshot/tagproof guards
    if guard_name == "screenshot_manifest_guard":
        extracted["missing_screenshots"] = counts.get("atlas_pages_uncovered", 0)
    elif guard_name == "tagproof_screenshots_guard":
        extracted["missing_screenshots"] = counts.get("unlisted_screenshots", 0) + counts.get(
            "orphan_manifest_entries", 0
        )

    return extracted


def main() -> int:
    """Run all underlying guards and emit integrated verdict."""
    checks: dict[str, bool] = {}
    counts: dict[str, int] = {
        "guards_total": len(GUARD_SCRIPTS),
        "guards_ok": 0,
        "guards_failed": 0,
        "broken_links": 0,
        "missing_screenshots": 0,
    }
    details: dict[str, Any] = {}

    # Run each guard
    for guard_name, script_path in GUARD_SCRIPTS.items():
        ok, verdict, error = _run_guard(script_path)

        check_key = f"{guard_name}_ok"
        checks[check_key] = ok

        if ok:
            counts["guards_ok"] += 1
        else:
            counts["guards_failed"] += 1

        # Store verdict or error in details
        if error:
            details[guard_name] = {"error": error, "ok": False}
        elif verdict:
            # Truncate large details to keep output manageable
            details[guard_name] = _truncate_details(verdict, max_size=1200)

        # Extract counts from verdict
        extracted = _extract_counts(verdict, guard_name)
        for key, value in extracted.items():
            counts[key] = max(counts.get(key, 0), value)  # Take max across guards

    # Integrated ok is False if any guard failed
    integrated_ok = all(checks.values())

    verdict = {
        "ok": integrated_ok,
        "checks": checks,
        "counts": counts,
        "details": details,
    }

    # Write evidence file if requested
    if "--write-evidence" in sys.argv:
        idx = sys.argv.index("--write-evidence")
        if idx + 1 < len(sys.argv):
            evidence_path = Path(sys.argv[idx + 1])
        else:
            evidence_path = EVIDENCE_DIR / "browser_screenshot_integrated.json"
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        with evidence_path.open("w") as f:
            json.dump(verdict, f, indent=2)

    print(json.dumps(verdict, indent=2))
    return 0 if integrated_ok else 1


if __name__ == "__main__":
    sys.exit(main())
