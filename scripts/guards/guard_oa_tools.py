#!/usr/bin/env python3
"""
Guard: OA Tools Registry Sync (Phase 27.E Batch 3)

Verifies that docs/SSOT/oa/OA_TOOLS_REGISTRY.md is in sync with
pmagent/oa/tools.py implementation.

Checks performed:
1. OA_TOOLS_REGISTRY.md exists and is parseable
2. pmagent.oa.tools is importable
3. Each tool_id in registry has corresponding function in tools.py
4. Each function in tools.py is documented in registry

Mode:
- STRICT: Exit non-zero on any mismatch
- HINT: Report mismatches but exit 0

Usage:
    python scripts/guards/guard_oa_tools.py [--mode STRICT|HINT]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "docs" / "SSOT" / "oa" / "OA_TOOLS_REGISTRY.md"


def parse_registry_tool_ids(registry_path: Path) -> set[str]:
    """
    Parse tool_ids from OA_TOOLS_REGISTRY.md.

    Looks for table rows like: | `oa.kernel_status` | ...
    """
    if not registry_path.exists():
        return set()

    content = registry_path.read_text(encoding="utf-8")

    # Pattern to match tool_id in markdown table
    # Matches: | `oa.something` | or | `oa.something.nested` |
    pattern = r"\|\s*`(oa\.[a-z_\.]+)`\s*\|"
    matches = re.findall(pattern, content)

    return set(matches)


def get_tools_module_tool_ids() -> tuple[set[str], str | None]:
    """
    Import pmagent.oa.tools and get registered tool IDs.

    Returns:
        (set of tool_ids, error message or None)
    """
    try:
        # Add project root to path
        sys.path.insert(0, str(ROOT))
        from pmagent.oa.tools import get_available_tools

        return set(get_available_tools()), None
    except ImportError as e:
        return set(), f"Failed to import pmagent.oa.tools: {e}"
    except Exception as e:
        return set(), f"Error loading tools module: {e}"


def run_guard(mode: str = "HINT") -> dict:
    """
    Run the OA tools sync guard.

    Returns:
        dict with ok, mode, issues, details
    """
    issues = []
    details = {}

    # Check 1: Registry file exists
    if not REGISTRY_PATH.exists():
        issues.append(f"OA_TOOLS_REGISTRY.md not found at {REGISTRY_PATH}")
        return {
            "ok": False,
            "mode": mode,
            "issues": issues,
            "details": details,
        }

    # Check 2: Parse registry
    registry_tools = parse_registry_tool_ids(REGISTRY_PATH)
    details["registry_tools"] = sorted(registry_tools)
    details["registry_count"] = len(registry_tools)

    if not registry_tools:
        issues.append("No tool_ids found in OA_TOOLS_REGISTRY.md")

    # Check 3: Import tools module
    module_tools, import_error = get_tools_module_tool_ids()
    details["module_tools"] = sorted(module_tools)
    details["module_count"] = len(module_tools)

    if import_error:
        issues.append(import_error)
        return {
            "ok": False,
            "mode": mode,
            "issues": issues,
            "details": details,
        }

    # Check 4: Compare registry vs module
    in_registry_not_module = registry_tools - module_tools
    in_module_not_registry = module_tools - registry_tools

    if in_registry_not_module:
        issues.append(f"Tools in registry but not in module: {sorted(in_registry_not_module)}")
        details["missing_from_module"] = sorted(in_registry_not_module)

    if in_module_not_registry:
        issues.append(f"Tools in module but not in registry: {sorted(in_module_not_registry)}")
        details["missing_from_registry"] = sorted(in_module_not_registry)

    # Determine overall status
    ok = len(issues) == 0

    return {
        "ok": ok,
        "mode": mode,
        "issues": issues,
        "details": details,
    }


def main():
    parser = argparse.ArgumentParser(description="Guard: OA Tools Registry Sync")
    parser.add_argument(
        "--mode",
        choices=["STRICT", "HINT"],
        default="HINT",
        help="STRICT exits non-zero on issues, HINT reports only",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON only",
    )
    args = parser.parse_args()

    result = run_guard(mode=args.mode)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Human-readable output
        print(f"[guard_oa_tools] Mode: {args.mode}")
        print(f"[guard_oa_tools] Registry tools: {result['details'].get('registry_count', 0)}")
        print(f"[guard_oa_tools] Module tools: {result['details'].get('module_count', 0)}")

        if result["ok"]:
            print("[guard_oa_tools] ✅ OA Tools registry in sync with implementation")
        else:
            print("[guard_oa_tools] ⚠️  Issues found:")
            for issue in result["issues"]:
                print(f"  - {issue}")

        # Also print JSON for machine consumption
        print(json.dumps(result, indent=2))

    # Exit code based on mode
    if args.mode == "STRICT" and not result["ok"]:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
