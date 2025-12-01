# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Validate new noun probe outputs against golden examples.
Usage: python3 scripts/validate_examples.py --new <new_output.jsonl> --golden <golden.jsonl>
"""

import argparse
import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load JSONL file into list of dicts."""
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def validate_structure(records: list[dict[str, Any]]) -> list[str]:
    """Validate that records have expected structure matching enrichment node output."""
    errors = []

    # Required fields from enrichment node output
    core_fields = ["hebrew", "name", "confidence", "insights", "tokens", "source"]

    for i, record in enumerate(records):
        # Check required fields
        missing_core = [f for f in core_fields if f not in record]
        if missing_core:
            errors.append(f"Record {i + 1}: missing required fields {missing_core}")

        # Type checks for required fields
        if "confidence" in record and not isinstance(record["confidence"], int | float):
            errors.append(
                f"Record {i + 1}: confidence should be numeric, got {type(record['confidence'])}"
            )

        if "tokens" in record and not isinstance(record["tokens"], int):
            errors.append(f"Record {i + 1}: tokens should be int, got {type(record['tokens'])}")

        if "insights" in record and not isinstance(record["insights"], str):
            errors.append(f"Record {i + 1}: insights should be str, got {type(record['insights'])}")

        if "hebrew" in record and not isinstance(record["hebrew"], str):
            errors.append(f"Record {i + 1}: hebrew should be str, got {type(record['hebrew'])}")

        if "name" in record and not isinstance(record["name"], str):
            errors.append(f"Record {i + 1}: name should be str, got {type(record['name'])}")

        # Optional fields from collection phase (may be present)
        if "primary_verse" in record and not isinstance(record["primary_verse"], str):
            errors.append(
                f"Record {i + 1}: primary_verse should be str, got {type(record['primary_verse'])}"
            )

        if "freq" in record and not isinstance(record["freq"], int):
            errors.append(f"Record {i + 1}: freq should be int, got {type(record['freq'])}")

        if "book" in record and not isinstance(record["book"], str):
            errors.append(f"Record {i + 1}: book should be str, got {type(record['book'])}")

        if (
            "chapter" in record
            and record["chapter"] is not None
            and not isinstance(record["chapter"], int)
        ):
            errors.append(
                f"Record {i + 1}: chapter should be int or null, got {type(record['chapter'])}"
            )

        # Validate insight length (should be substantial theological analysis)
        if "insights" in record:
            word_count = len(record["insights"].split())
            if word_count < 150:
                errors.append(
                    f"Record {i + 1}: insights too short ({word_count} words), expected 150-300 words"
                )

        # Validate confidence range
        if "confidence" in record:
            conf = record["confidence"]
            if not (0.0 <= conf <= 1.0):
                errors.append(f"Record {i + 1}: confidence {conf} out of range [0,1]")

    return errors


def compare_outputs(
    new_records: list[dict[str, Any]], golden_records: list[dict[str, Any]]
) -> dict[str, Any]:
    """Compare new output against golden example."""
    results = {
        "structure_valid": True,
        "count_match": len(new_records) == len(golden_records),
        "field_coverage": {},
        "confidence_range": {},
        "source_distribution": {},
        "errors": [],
    }

    # Structure validation
    struct_errors = validate_structure(new_records)
    if struct_errors:
        results["structure_valid"] = False
        results["errors"].extend(struct_errors)

    # Field coverage
    golden_fields = set()
    for r in golden_records:
        golden_fields.update(r.keys())

    new_fields = set()
    for r in new_records:
        new_fields.update(r.keys())

    results["field_coverage"] = {
        "golden_fields": sorted(golden_fields),
        "new_fields": sorted(new_fields),
        "missing_in_new": sorted(golden_fields - new_fields),
        "extra_in_new": sorted(new_fields - golden_fields),
    }

    # Confidence stats
    if new_records and "confidence" in new_records[0]:
        confidences = [r.get("confidence", 0) for r in new_records if "confidence" in r]
        results["confidence_range"] = {
            "min": min(confidences) if confidences else None,
            "max": max(confidences) if confidences else None,
            "avg": sum(confidences) / len(confidences) if confidences else None,
        }

    # Source distribution
    sources = {}
    for r in new_records:
        src = r.get("source", "unknown")
        sources[src] = sources.get(src, 0) + 1
    results["source_distribution"] = sources

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Validate noun probe outputs against golden examples"
    )
    parser.add_argument("--new", required=True, help="Path to new output JSONL file")
    parser.add_argument("--golden", required=True, help="Path to golden example JSONL file")
    parser.add_argument("--quiet", action="store_true", help="Only show errors/summary")

    args = parser.parse_args()

    new_path = Path(args.new)
    golden_path = Path(args.golden)

    if not new_path.exists():
        print(f"ERROR: New file not found: {new_path}")
        return 1

    if not golden_path.exists():
        print(f"ERROR: Golden file not found: {golden_path}")
        return 1

    try:
        new_records = load_jsonl(new_path)
        golden_records = load_jsonl(golden_path)
    except Exception as e:
        print(f"ERROR: Failed to load files: {e}")
        return 1

    results = compare_outputs(new_records, golden_records)

    if not args.quiet:
        print(
            f"[validate] Comparing {len(new_records)} new records vs {len(golden_records)} golden"
        )
        print(f"[validate] Structure valid: {results['structure_valid']}")
        print(f"[validate] Count match: {results['count_match']}")

        cov = results["field_coverage"]
        if cov["missing_in_new"]:
            print(f"[validate] WARNING: Missing fields in new: {cov['missing_in_new']}")
        if cov["extra_in_new"]:
            print(f"[validate] INFO: Extra fields in new: {cov['extra_in_new']}")

        conf = results["confidence_range"]
        if conf["min"] is not None:
            print(
                f"[validate] Confidence range: {conf['min']:.2f} - {conf['max']:.2f} (avg: {conf['avg']:.2f})"
            )

        print(f"[validate] Source distribution: {results['source_distribution']}")

    if results["errors"]:
        print("\n[validate] ERRORS:")
        for err in results["errors"]:
            print(f"  {err}")
        return 1

    if not results["structure_valid"]:
        print("[validate] FAIL: Structure validation failed")
        return 1

    print("[validate] PASS: All validations passed")
    return 0


if __name__ == "__main__":
    exit(main())
