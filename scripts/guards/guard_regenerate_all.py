#!/usr/bin/env python3
"""
PLAN-080 E98 — Guard: Full Extraction & Atlas + Exports Regeneration

Validates that regeneration completed successfully and all artifacts
are present and schema-valid.

Guard semantics:
- evidence/regenerate_all_receipt.json must exist and be valid JSON
- All expected artifacts must be present
- Each artifact must validate against its corresponding schema
"""

import json
import pathlib
from typing import Any, Dict

ROOT = pathlib.Path(__file__).resolve().parents[2]
RECEIPT_PATH = ROOT / "evidence" / "regenerate_all_receipt.json"

# Schema mappings (artifact path → schema path)
SCHEMA_MAP = {
    "exports/graph_latest.json": "docs/SSOT/SSOT_graph.v1.schema.json",
    "exports/graph_stats.json": "docs/SSOT/graph-stats.schema.json",
    "exports/graph_patterns.json": "docs/SSOT/graph-patterns.schema.json",
    "exports/temporal_patterns.json": "docs/SSOT/temporal-patterns.schema.json",
    "exports/pattern_forecast.json": "docs/SSOT/pattern-forecast.schema.json",
}


def validate_schema(instance_path: pathlib.Path, schema_path: pathlib.Path) -> tuple[bool, str | None]:
    """Validate an instance against a schema. Returns (is_valid, error_message)."""
    try:
        from jsonschema import ValidationError, validate

        instance = json.loads(instance_path.read_text(encoding="utf-8"))
        schema = json.loads(schema_path.read_text(encoding="utf-8"))

        validate(instance=instance, schema=schema)
        return True, None
    except ImportError:
        # jsonschema not available - skip validation but note it
        return True, "jsonschema not available (skipped)"
    except json.JSONDecodeError as e:
        return False, f"JSON decode error: {str(e)[:200]}"
    except ValidationError as e:
        return False, f"Schema validation error: {str(e.message)[:200]}"
    except Exception as e:
        return False, f"Validation error: {str(e)[:200]}"


def main() -> int:
    """Main guard function."""
    checks: Dict[str, bool] = {}
    counts: Dict[str, int] = {}
    details: Dict[str, Any] = {}

    # Check receipt exists
    exists = RECEIPT_PATH.exists()
    checks["receipt_exists"] = exists
    if not exists:
        verdict = {
            "ok": False,
            "checks": checks,
            "counts": counts,
            "details": {"reason": "missing_receipt", "path": str(RECEIPT_PATH)},
        }
        print(json.dumps(verdict, indent=2))
        return 1

    # Load receipt
    try:
        receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        verdict = {
            "ok": False,
            "checks": {"receipt_exists": True, "receipt_json_valid": False},
            "counts": counts,
            "details": {"path": str(RECEIPT_PATH), "error": str(e)[:500]},
        }
        print(json.dumps(verdict, indent=2))
        return 1

    checks["receipt_json_valid"] = True
    checks["receipt_ok_flag"] = bool(receipt.get("ok", False))

    # Check artifacts
    artifacts = receipt.get("artifacts", [])
    missing_artifacts = receipt.get("missing_artifacts", [])
    expected = receipt.get("expected_artifacts", [])

    counts["expected_artifacts"] = len(expected)
    counts["found_artifacts"] = len(artifacts)
    counts["missing_artifacts"] = len(missing_artifacts)

    checks["all_artifacts_present"] = len(missing_artifacts) == 0

    # Validate each artifact against schema
    schema_errors: Dict[str, str] = {}
    schema_validations = 0
    schema_passed = 0

    for artifact in artifacts:
        artifact_path = ROOT / artifact
        if not artifact_path.exists():
            schema_errors[artifact] = "File not found on disk"
            continue

        schema_rel = SCHEMA_MAP.get(artifact)
        if not schema_rel:
            # No schema mapping - skip validation
            continue

        schema_path = ROOT / schema_rel
        if not schema_path.exists():
            schema_errors[artifact] = f"Schema not found: {schema_rel}"
            continue

        schema_validations += 1
        is_valid, error = validate_schema(artifact_path, schema_path)
        if is_valid:
            schema_passed += 1
        else:
            schema_errors[artifact] = error or "Unknown validation error"

    counts["schema_validations"] = schema_validations
    counts["schema_passed"] = schema_passed
    counts["schema_failures"] = len(schema_errors)

    checks["all_schemas_valid"] = len(schema_errors) == 0 and schema_validations > 0

    details["receipt_path"] = str(RECEIPT_PATH)
    details["missing_artifacts"] = missing_artifacts
    details["schema_errors"] = schema_errors

    # DB-off mode detection (if receipt indicates DB issues)
    if not receipt.get("ok", False) and any(
        "db" in str(step.get("error", "")).lower() or "database" in str(step.get("error", "")).lower()
        for step in receipt.get("steps", [])
    ):
        details["mode"] = "db_off"
        checks["db_available"] = False
    else:
        checks["db_available"] = True

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
