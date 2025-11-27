#!/usr/bin/env python3
"""
Guard for Phase-6D Control-Plane Widget Adapters.

Validates:
- Adapter module exists and is importable
- Widget props functions work correctly
- Export files are accessible (if present)
- Offline-safe defaults work when files are missing
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

EVIDENCE_DIR = REPO / "evidence"


def _is_strict_mode() -> bool:
    """Determine if running in STRICT mode."""
    return os.getenv("STRICT_MODE", "0") == "1" or os.getenv("CI") == "true"


def check_adapter_import() -> dict[str, bool | str]:
    """Check that adapter module can be imported."""
    try:
        from agentpm.control_widgets.adapter import (  # noqa: F401
            load_biblescholar_reference_widget_props,
            load_graph_compliance_widget_props,
        )

        return {
            "ok": True,
            "message": "Adapter module imported successfully",
        }
    except ImportError as e:
        return {
            "ok": False,
            "error": f"Failed to import adapter module: {e}",
        }


def check_widget_functions() -> dict[str, bool | str]:
    """Check that widget functions work (even with missing files)."""
    try:
        from agentpm.control_widgets.adapter import (
            load_biblescholar_reference_widget_props,
            load_graph_compliance_widget_props,
        )

        # Test graph compliance (should work even if file missing)
        compliance_props = load_graph_compliance_widget_props()
        if not isinstance(compliance_props, dict):
            return {
                "ok": False,
                "error": "load_graph_compliance_widget_props() did not return dict",
            }
        if "status" not in compliance_props:
            return {
                "ok": False,
                "error": "Graph compliance props missing 'status' field",
            }

        # Test BibleScholar reference (should work even if file missing)
        reference_props = load_biblescholar_reference_widget_props()
        if not isinstance(reference_props, dict):
            return {
                "ok": False,
                "error": "load_biblescholar_reference_widget_props() did not return dict",
            }
        if "status" not in reference_props:
            return {
                "ok": False,
                "error": "BibleScholar reference props missing 'status' field",
            }

        return {
            "ok": True,
            "message": "Widget functions work correctly",
            "graph_compliance_status": compliance_props["status"],
            "biblescholar_reference_status": reference_props["status"],
        }
    except Exception as e:
        return {
            "ok": False,
            "error": f"Widget functions failed: {e}",
        }


def check_export_files() -> dict[str, bool | str]:
    """Check that export files exist (advisory in HINT, required in STRICT)."""
    graph_compliance_path = REPO / "share" / "atlas" / "control_plane" / "graph_compliance.json"
    biblescholar_reference_path = REPO / "share" / "atlas" / "control_plane" / "biblescholar_reference.json"
    strict_mode = _is_strict_mode()

    result: dict[str, bool | str] = {
        "ok": True,
        "graph_compliance_exists": graph_compliance_path.exists(),
        "biblescholar_reference_exists": biblescholar_reference_path.exists(),
    }

    # In STRICT mode, files must exist
    if strict_mode:
        if not graph_compliance_path.exists():
            result["ok"] = False
            result["error"] = "graph_compliance.json missing (required in STRICT mode)"
            return result
        if not biblescholar_reference_path.exists():
            result["ok"] = False
            result["error"] = "biblescholar_reference.json missing (required in STRICT mode)"
            return result

    # Validate JSON structure if files exist
    if graph_compliance_path.exists():
        try:
            data = json.loads(graph_compliance_path.read_text(encoding="utf-8"))
            if "schema" not in data:
                result["ok"] = False
                result["error"] = "graph_compliance.json missing 'schema' field"
        except json.JSONDecodeError as e:
            result["ok"] = False
            result["error"] = f"graph_compliance.json invalid JSON: {e}"

    if biblescholar_reference_path.exists():
        try:
            data = json.loads(biblescholar_reference_path.read_text(encoding="utf-8"))
            if "schema" not in data:
                result["ok"] = False
                result["error"] = "biblescholar_reference.json missing 'schema' field"
        except json.JSONDecodeError as e:
            result["ok"] = False
            result["error"] = f"biblescholar_reference.json invalid JSON: {e}"

    return result


def main() -> int:
    """Run guard checks."""
    parser = argparse.ArgumentParser(description="Guard for Phase-6D control-plane widgets")
    parser.add_argument(
        "--write-evidence",
        type=str,
        help="Write evidence JSON to this file (relative to evidence/)",
    )
    args = parser.parse_args()

    strict_mode = _is_strict_mode()

    checks = {
        "adapter_import": check_adapter_import(),
        "widget_functions": check_widget_functions(),
        "export_files": check_export_files(),
    }

    all_ok = all(check.get("ok", False) for check in checks.values())

    verdict = {
        "guard": "guard_control_widgets",
        "phase": "6D",
        "mode": "STRICT" if strict_mode else "HINT",
        "overall_ok": all_ok,
        "checks": checks,
    }

    # Write evidence if requested
    if args.write_evidence:
        evidence_path = EVIDENCE_DIR / args.write_evidence
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(json.dumps(verdict, indent=2), encoding="utf-8")
        print(f"Evidence written to {evidence_path}", file=sys.stderr)

    # Print verdict
    print(json.dumps(verdict, indent=2))

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
