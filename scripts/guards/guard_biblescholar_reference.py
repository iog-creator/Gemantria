#!/usr/bin/env python3
"""
Guard for Phase-6P BibleScholar Reference Answer Slice Export.

Validates:
- biblescholar_reference.json exists and has valid structure
- Schema version is correct
- Timestamp is recent (within last 24 hours)
- Questions array is present (may be empty if no data)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, UTC, timedelta
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

EXPORT_FILE = REPO / "share" / "atlas" / "control_plane" / "biblescholar_reference.json"
EVIDENCE_DIR = REPO / "evidence"


def _is_strict_mode() -> bool:
    """Determine if running in STRICT mode."""
    return os.getenv("STRICT_MODE", "0") == "1" or os.getenv("CI") == "true"


def check_file_exists() -> dict[str, bool | str]:
    """Check that biblescholar_reference.json exists."""
    if not EXPORT_FILE.exists():
        return {
            "exists": False,
            "error": f"File not found: {EXPORT_FILE}",
        }
    return {"exists": True}


def check_schema(data: dict) -> dict[str, bool | str]:
    """Check that schema is correct."""
    expected_schema = "biblescholar_reference_v1"
    actual_schema = data.get("schema")
    if actual_schema != expected_schema:
        return {
            "schema_ok": False,
            "error": f"Expected schema '{expected_schema}', got '{actual_schema}'",
        }
    return {"schema_ok": True}


def check_structure(data: dict) -> dict[str, bool | list[str]]:
    """Check that required structure is present."""
    issues = []
    required_keys = ["schema", "generated_at", "ok", "questions", "summary"]
    for key in required_keys:
        if key not in data:
            issues.append(f"Missing required key: {key}")

    if "summary" in data:
        summary = data["summary"]
        required_summary_keys = ["total_questions", "by_mode", "by_verse_ref"]
        for key in required_summary_keys:
            if key not in summary:
                issues.append(f"Missing required summary key: {key}")

    return {
        "structure_ok": len(issues) == 0,
        "issues": issues,
    }


def check_timestamp(data: dict) -> dict[str, bool | str]:
    """Check that timestamp is recent (within last 24 hours)."""
    generated_at_str = data.get("generated_at")
    if not generated_at_str:
        return {
            "timestamp_ok": False,
            "error": "Missing generated_at timestamp",
        }

    try:
        generated_at = datetime.fromisoformat(generated_at_str.replace("Z", "+00:00"))
        now = datetime.now(UTC)
        age = now - generated_at.replace(tzinfo=UTC) if generated_at.tzinfo is None else now - generated_at

        if age > timedelta(hours=24):
            return {
                "timestamp_ok": False,
                "error": f"Export is {age.total_seconds() / 3600:.1f} hours old (max 24h)",
            }

        return {"timestamp_ok": True, "age_hours": age.total_seconds() / 3600}
    except Exception as e:
        return {
            "timestamp_ok": False,
            "error": f"Invalid timestamp format: {e}",
        }


def check_questions_structure(data: dict) -> dict[str, bool | dict]:
    """Check that questions array has valid structure."""
    questions = data.get("questions", [])
    if not isinstance(questions, list):
        return {
            "questions_structure_ok": False,
            "error": "questions must be a list",
        }

    # Validate each question entry if present
    issues = []
    for i, q in enumerate(questions):
        if not isinstance(q, dict):
            issues.append(f"Question {i} is not a dict")
            continue
        required_fields = ["run_id", "question", "created_at", "metadata"]
        for field in required_fields:
            if field not in q:
                issues.append(f"Question {i} missing field: {field}")

    return {
        "questions_structure_ok": len(issues) == 0,
        "total_questions": len(questions),
        "issues": issues if issues else None,
    }


def main() -> int:
    """Run guard checks."""
    parser = argparse.ArgumentParser(description="Guard for Phase-6P BibleScholar Reference Export")
    parser.add_argument(
        "--write-evidence",
        type=str,
        help="Write evidence JSON to this file",
    )
    args = parser.parse_args()

    strict_mode = _is_strict_mode()

    verdict = {
        "guard": "guard_biblescholar_reference",
        "episode": "Phase-6P",
        "mode": "STRICT" if strict_mode else "HINT",
        "overall_ok": True,
        "checks": {},
    }

    # Check file exists
    file_check = check_file_exists()
    verdict["checks"]["file_exists"] = file_check
    if not file_check["exists"]:
        if strict_mode:
            verdict["overall_ok"] = False
            print(f"[guard_biblescholar_reference] FAIL: {file_check.get('error', 'File missing')}", file=sys.stderr)
            if args.write_evidence:
                EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
                evidence_file = EVIDENCE_DIR / args.write_evidence
                evidence_file.write_text(json.dumps(verdict, indent=2))
            return 1
        else:
            print(
                f"[guard_biblescholar_reference] HINT: {file_check.get('error', 'File missing')} (HINT mode)",
                file=sys.stderr,
            )
            if args.write_evidence:
                EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
                evidence_file = EVIDENCE_DIR / args.write_evidence
                evidence_file.write_text(json.dumps(verdict, indent=2))
            return 0

    # Load and parse JSON
    try:
        with EXPORT_FILE.open() as f:
            data = json.load(f)
    except Exception as e:
        if strict_mode:
            verdict["overall_ok"] = False
            print(f"[guard_biblescholar_reference] FAIL: Failed to parse JSON: {e}", file=sys.stderr)
            if args.write_evidence:
                EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
                evidence_file = EVIDENCE_DIR / args.write_evidence
                evidence_file.write_text(json.dumps(verdict, indent=2))
            return 1
        else:
            print(f"[guard_biblescholar_reference] HINT: Failed to parse JSON: {e} (HINT mode)", file=sys.stderr)
            if args.write_evidence:
                EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
                evidence_file = EVIDENCE_DIR / args.write_evidence
                evidence_file.write_text(json.dumps(verdict, indent=2))
            return 0

    # Check schema
    schema_check = check_schema(data)
    verdict["checks"]["schema"] = schema_check
    if not schema_check["schema_ok"]:
        if strict_mode:
            verdict["overall_ok"] = False
            print(f"[guard_biblescholar_reference] FAIL: Schema issue: {schema_check.get('error')}", file=sys.stderr)
        else:
            print(
                f"[guard_biblescholar_reference] HINT: Schema issue: {schema_check.get('error')} (HINT mode)",
                file=sys.stderr,
            )

    # Check structure
    structure_check = check_structure(data)
    verdict["checks"]["structure"] = structure_check
    if not structure_check["structure_ok"]:
        if strict_mode:
            verdict["overall_ok"] = False
            print(
                f"[guard_biblescholar_reference] FAIL: Structure issues: {structure_check['issues']}",
                file=sys.stderr,
            )
        else:
            print(
                f"[guard_biblescholar_reference] HINT: Structure issues: {structure_check['issues']} (HINT mode)",
                file=sys.stderr,
            )

    # Check timestamp
    timestamp_check = check_timestamp(data)
    verdict["checks"]["timestamp"] = timestamp_check
    if not timestamp_check["timestamp_ok"]:
        if strict_mode:
            verdict["overall_ok"] = False
            print(
                f"[guard_biblescholar_reference] FAIL: Timestamp issue: {timestamp_check.get('error')}",
                file=sys.stderr,
            )
        else:
            print(
                f"[guard_biblescholar_reference] HINT: Timestamp issue: {timestamp_check.get('error')} (HINT mode)",
                file=sys.stderr,
            )

    # Check questions structure (non-blocking if ok=false due to empty DB)
    questions_check = check_questions_structure(data)
    verdict["checks"]["questions_structure"] = questions_check
    if not questions_check["questions_structure_ok"]:
        verdict["overall_ok"] = False
        print(
            f"[guard_biblescholar_reference] Questions structure issues: {questions_check.get('issues')}",
            file=sys.stderr,
        )

    # Print verdict
    if verdict["overall_ok"]:
        print("[guard_biblescholar_reference] Verdict: PASS")
    else:
        print("[guard_biblescholar_reference] Verdict: FAIL", file=sys.stderr)

    # Write evidence if requested
    if args.write_evidence:
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        # Handle both relative and absolute paths
        if Path(args.write_evidence).is_absolute():
            evidence_file = Path(args.write_evidence)
        else:
            evidence_file = EVIDENCE_DIR / args.write_evidence
        evidence_file.parent.mkdir(parents=True, exist_ok=True)
        evidence_file.write_text(json.dumps(verdict, indent=2))
        print(f"[guard_biblescholar_reference] Evidence: {evidence_file}")

    return 0 if verdict["overall_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
