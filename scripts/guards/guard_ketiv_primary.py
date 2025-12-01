#!/usr/bin/env python3
"""
Guard: Ketiv-Primary Policy Enforcement (Phase 2)

Validates that gematria calculations use Ketiv (written form) as primary,
per ADR-002. Qere (read form) must be recorded as variant, not used for calculations.

Phase 2: Ketiv/Qere Policy - Numeric SSOT enforcement
"""

import json
import sys
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.hebrew_utils import get_ketiv_for_gematria


def validate_ketiv_primary(noun: dict[str, Any]) -> list[str]:
    """
    Validate that a noun follows Ketiv-primary policy.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    surface = noun.get("surface", "")
    variant_surface = noun.get("variant_surface")
    is_ketiv = noun.get("is_ketiv", True)
    variant_type = noun.get("variant_type")

    # If variant exists, ensure Ketiv is in surface
    if variant_surface:
        if not is_ketiv:
            errors.append(f"Noun {noun.get('noun_id', 'unknown')}: surface is Qere but should be Ketiv (per ADR-002)")

        # Verify gematria is calculated from Ketiv (surface), not Qere
        ketiv = get_ketiv_for_gematria(noun)
        if ketiv != surface and is_ketiv:
            errors.append(
                f"Noun {noun.get('noun_id', 'unknown')}: gematria calculation should use Ketiv (surface), not variant"
            )

    # If variant_type is set, ensure it's valid
    if variant_type and variant_type not in ["ketiv", "qere", "other"]:
        errors.append(
            f"Noun {noun.get('noun_id', 'unknown')}: "
            f"invalid variant_type '{variant_type}' (must be ketiv, qere, or other)"
        )

    return errors


def guard_ketiv_primary(export_path: str = "exports/graph_latest.json") -> dict[str, Any]:
    """
    Guard: Validate Ketiv-primary policy in exported graph.

    Args:
        export_path: Path to graph export JSON

    Returns:
        Guard verdict dictionary
    """
    verdict = {
        "guard": "ketiv_primary",
        "version": "1.0",
        "ok": True,
        "errors": [],
        "warnings": [],
        "checked": 0,
        "passed": 0,
        "failed": 0,
    }

    export_file = Path(export_path)
    if not export_file.exists():
        verdict["ok"] = False
        verdict["errors"].append(f"Export file not found: {export_path}")
        return verdict

    try:
        with open(export_file, encoding="utf-8") as f:
            data = json.load(f)

        nodes = data.get("nodes", [])
        verdict["checked"] = len(nodes)

        for node in nodes:
            errors = validate_ketiv_primary(node)
            if errors:
                verdict["failed"] += 1
                verdict["errors"].extend(errors)
            else:
                verdict["passed"] += 1

        if verdict["errors"]:
            verdict["ok"] = False

    except Exception as e:
        verdict["ok"] = False
        verdict["errors"].append(f"Error reading export: {e}")

    return verdict


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Guard: Ketiv-primary policy enforcement")
    parser.add_argument(
        "--export",
        default="exports/graph_latest.json",
        help="Path to graph export JSON",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON verdict",
    )

    args = parser.parse_args()

    verdict = guard_ketiv_primary(args.export)

    if args.json:
        print(json.dumps(verdict, indent=2))
    else:
        if verdict["ok"]:
            print(f"✅ Ketiv-primary guard: PASS ({verdict['passed']}/{verdict['checked']} nodes)")
        else:
            print(f"❌ Ketiv-primary guard: FAIL ({verdict['failed']} errors)")
            for error in verdict["errors"]:
                print(f"  - {error}")

    sys.exit(0 if verdict["ok"] else 1)


if __name__ == "__main__":
    main()
