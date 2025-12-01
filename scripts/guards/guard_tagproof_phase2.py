#!/usr/bin/env python3
"""
PLAN-080 E100 — Phase-2 Tagproof Bundle Guard

Validates the Phase-2 tagproof bundle posture according to explicit policy:
- All required components must exist
- Component verdicts must pass (with STRICT/HINT mode handling)
- Emits machine-readable JSON verdict for CI/tag lanes
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "evidence"
BUNDLE_PATH = EVIDENCE_DIR / "tagproof_phase2_bundle.json"
VERDICT_PATH = EVIDENCE_DIR / "guard_tagproof_phase2.json"


# Determine mode (STRICT on tags, HINT on PRs) - evaluated at runtime
def _is_strict_mode() -> bool:
    return os.getenv("STRICT_MODE", "0") == "1" or os.getenv("CI") == "true"


def _load_bundle() -> dict[str, Any] | None:
    """Load the Phase-2 tagproof bundle."""
    if not BUNDLE_PATH.exists():
        return None
    try:
        return json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None


def _get_component_ok(component: dict[str, Any], component_name: str) -> tuple[bool, str | None]:
    """
    Extract ok status from a component.

    Returns:
        (ok, error_message)
    """
    if "error" in component:
        return False, component.get("error", "unknown error")

    # Check for guard-style verdict with "ok" field
    if "ok" in component:
        ok = component["ok"]
        if not ok:
            # Try to extract a reason from details
            details = component.get("details", {})
            if isinstance(details, dict):
                error_msg = details.get("reason") or str(details.get("schema_errors", ""))[:200]
                return False, error_msg or "component ok is false"
        return ok, None

    # If no "ok" field, consider it valid (e.g., raw coverage JSON)
    return True, None


def main() -> int:
    """Run the Phase-2 tagproof guard."""
    checks: dict[str, bool] = {}
    counts: dict[str, int] = {
        "components_total": 4,  # Will be updated dynamically later
        "components_missing": 0,
        "components_ok": 0,
        "components_failed": 0,
    }
    details: dict[str, Any] = {
        "mode": "STRICT" if _is_strict_mode() else "HINT",
        "missing_components": [],
        "component_errors": {},
    }

    bundle = _load_bundle()
    if bundle is None:
        verdict = {
            "ok": False,
            "checks": {"bundle_exists": False},
            "counts": counts,
            "details": {**details, "error": "bundle file not found"},
        }
        VERDICT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with VERDICT_PATH.open("w") as f:
            json.dump(verdict, f, indent=2)
        print(json.dumps(verdict, indent=2))
        return 1

    checks["bundle_exists"] = True
    components = bundle.get("components", {})

    # Required components (base set)
    required_components = {
        "tv_coverage": "tv_coverage",
        "gatekeeper_coverage": "gatekeeper_coverage",
        "regeneration": "regeneration_guard",  # Use guard verdict, not receipt
        "browser_screenshot": "browser_screenshot",
    }

    # Add MCP RO guard as required in STRICT mode (PLAN-091 E102)
    if _is_strict_mode():
        required_components["mcp_db_ro"] = "mcp_db_ro_guard"

    # Dynamic components_total based on required_components
    components_total = len(required_components)
    counts: dict[str, int] = {
        "components_total": components_total,
        "components_missing": 0,
        "components_ok": 0,
        "components_failed": 0,
    }

    for check_name, component_key in required_components.items():
        if component_key not in components:
            # Component is completely missing from bundle
            checks[f"{check_name}_ok"] = False
            counts["components_missing"] += 1
            details["missing_components"].append(component_key)
            details["component_errors"][component_key] = "missing from bundle"
        elif "error" in components[component_key]:
            # Component exists but has an error field (legacy handling)
            checks[f"{check_name}_ok"] = False
            counts["components_missing"] += 1
            details["missing_components"].append(component_key)
            details["component_errors"][component_key] = components[component_key].get("error", "missing")
        else:
            ok, error_msg = _get_component_ok(components[component_key], component_key)
            check_key = f"{check_name}_ok"
            # Don't set check yet - we'll set it after HINT mode adjustments
            initial_ok = ok

            if initial_ok:
                counts["components_ok"] += 1
            else:
                counts["components_failed"] += 1
                if error_msg:
                    details["component_errors"][component_key] = error_msg

            # Set check after counting (will be adjusted by HINT mode below)
            checks[check_key] = initial_ok

    # Special handling for gatekeeper_coverage in HINT mode
    if not _is_strict_mode() and not checks.get("gatekeeper_coverage_ok", True):
        # In HINT mode, allow gatekeeper failures if uncovered codes are flagged
        gatekeeper = components.get("gatekeeper_coverage", {})
        uncovered = gatekeeper.get("coverage", {}).get("BUDGET_EXCEEDED") is False
        if uncovered:
            # This is expected in HINT mode (BUDGET_EXCEEDED not covered yet)
            # Adjust counts: was failed, now ok
            if counts["components_failed"] > 0:
                counts["components_failed"] -= 1
            counts["components_ok"] += 1
            checks["gatekeeper_coverage_ok"] = True
            details["component_errors"].pop("gatekeeper_coverage", None)
            details["hint_mode_override"] = "gatekeeper_coverage allowed in HINT mode"

    # Special handling for browser_screenshot in HINT mode
    # Only override if component exists but failed (not if it's missing)
    if (
        not _is_strict_mode()
        and not checks.get("browser_screenshot_ok", True)
        and "browser_screenshot" not in details["missing_components"]
    ):
        # In HINT mode, allow browser/screenshot failures during dev
        # Adjust counts: was failed, now ok
        if counts["components_failed"] > 0:
            counts["components_failed"] -= 1
        counts["components_ok"] += 1
        checks["browser_screenshot_ok"] = True
        details["component_errors"].pop("browser_screenshot", None)
        if "hint_mode_override" not in details:
            details["hint_mode_override"] = []
        if not isinstance(details["hint_mode_override"], list):
            details["hint_mode_override"] = [details["hint_mode_override"]]
        details["hint_mode_override"].append("browser_screenshot allowed in HINT mode")

    # Final verdict
    ok = all(checks.values()) if checks else False

    verdict = {
        "ok": ok,
        "checks": checks,
        "counts": counts,
        "details": details,
    }

    VERDICT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with VERDICT_PATH.open("w") as f:
        json.dump(verdict, f, indent=2)

    print(json.dumps(verdict, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
