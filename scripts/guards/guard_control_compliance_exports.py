#!/usr/bin/env python3
"""
Guard for control-plane compliance exports.

Validates that the three compliance export JSON files exist and have the expected structure.
Emits a machine-readable verdict JSON to evidence/guard_control_compliance_exports.json.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, UTC
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

VERDICT_PATH = REPO / "evidence" / "guard_control_compliance_exports.json"

# Expected files and their required keys
EXPECTED_FILES = {
    "compliance.head.json": {
        "required_keys": {"schema", "generated_at", "ok", "connection_ok", "summary"},
        "optional_keys": {"error"},
    },
    "top_violations_7d.json": {
        "required_keys": {"schema", "generated_at", "ok", "connection_ok", "window", "violations"},
        "optional_keys": {"error"},
    },
    "top_violations_30d.json": {
        "required_keys": {"schema", "generated_at", "ok", "connection_ok", "window", "violations"},
        "optional_keys": {"error"},
    },
}


def check_file(file_path: Path, file_name: str, expected: dict) -> tuple[bool, list[str]]:
    """Check if a JSON file exists and has the expected structure."""
    errors = []

    if not file_path.exists():
        return False, [f"File missing: {file_path}"]

    try:
        content = file_path.read_text(encoding="utf-8")
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]
    except Exception as e:
        return False, [f"Failed to read file: {e}"]

    # Check required keys
    required_keys = expected["required_keys"]
    missing_keys = required_keys - set(data.keys())
    if missing_keys:
        errors.append(f"Missing required keys: {sorted(missing_keys)}")

    # Check schema
    if "schema" in data and data["schema"] != "control":
        errors.append(f"Invalid schema: expected 'control', got '{data.get('schema')}'")

    # Check generated_at format (should be ISO format)
    if "generated_at" in data:
        gen_at = data["generated_at"]
        if not isinstance(gen_at, str) or ("T" not in gen_at and "Z" not in gen_at):
            errors.append(f"Invalid generated_at format: {gen_at}")

    # Check ok and connection_ok are booleans
    for key in ["ok", "connection_ok"]:
        if key in data and not isinstance(data[key], bool):
            errors.append(f"Invalid {key}: expected bool, got {type(data[key]).__name__}")

    # Check file-specific structure
    if file_name == "compliance.head.json":
        if "summary" in data and data["summary"] is not None:
            if not isinstance(data["summary"], dict):
                errors.append("summary must be dict or null")
    elif file_name in ["top_violations_7d.json", "top_violations_30d.json"]:
        # Check window
        if "window" in data:
            expected_window = "7d" if "7d" in file_name else "30d"
            if data["window"] != expected_window:
                errors.append(
                    f"Invalid window: expected '{expected_window}', got '{data.get('window')}'"
                )

        # Check violations is a list
        if "violations" in data and not isinstance(data["violations"], list):
            errors.append("violations must be a list")

    return len(errors) == 0, errors


def main() -> int:
    """Run guard and emit verdict."""
    VERDICT_PATH.parent.mkdir(parents=True, exist_ok=True)

    base_dir = REPO / "share" / "atlas" / "control_plane"
    all_ok = True
    all_errors = []
    files_checked = []

    for file_name, expected in EXPECTED_FILES.items():
        file_path = base_dir / file_name
        ok, errors = check_file(file_path, file_name, expected)
        files_checked.append(file_name)

        if not ok:
            all_ok = False
            all_errors.extend([{"file": file_name, "msg": error} for error in errors])

    verdict_data = {
        "schema": "control",
        "generated_at": datetime.now(UTC).isoformat(),
        "ok": all_ok,
        "files_checked": files_checked,
        "errors": all_errors,
    }

    VERDICT_PATH.write_text(json.dumps(verdict_data, indent=2) + "\n", encoding="utf-8")

    if all_ok:
        print(f"[guard_control_compliance_exports] OK: All {len(files_checked)} files validated")
        return 0
    else:
        print(
            f"[guard_control_compliance_exports] FAIL: {len(all_errors)} error(s) found",
            file=sys.stderr,
        )
        print(json.dumps(verdict_data, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
