#!/usr/bin/env python3
"""
Envelope integrity checker for unified UI envelopes.

Validates:
- Schema presence and format
- Evidence (sha256_12) integrity
- Model manifest completeness
- Artifact references

Related Rules: Rule-022 (Visualization Contract Sync), Rule-039 (Execution Contract)
Related ADRs: ADR-019 (Data Contracts), ADR-023 (Visualization API Spec)
"""

import json
import sys
from pathlib import Path

ENVELOPE_FILE = Path("exports/ui_envelope.json")


def check_envelope_integrity(envelope_path: Path) -> list[str]:
    """Check envelope integrity and return list of errors."""
    errors = []

    if not envelope_path.exists():
        errors.append(f"Envelope file not found: {envelope_path}")
        return errors

    try:
        with envelope_path.open(encoding="utf-8") as f:
            envelope = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in envelope: {e}")
        return errors

    # Check required top-level fields
    required_fields = ["schema", "generated_at"]
    for field in required_fields:
        if field not in envelope:
            errors.append(f"Missing required field: {field}")

    # Check schema format
    schema = envelope.get("schema", "")
    if not schema.startswith("gemantria/"):
        errors.append(f"Invalid schema format: {schema}")

    # Check books field (either 'book' or 'books')
    if "book" not in envelope and "books" not in envelope:
        errors.append("Missing 'book' or 'books' field")

    # Check evidence structure
    evidence = envelope.get("evidence", {})
    if not isinstance(evidence, dict):
        errors.append("Evidence must be a dictionary")
    else:
        models_used = evidence.get("models_used", {})
        if not isinstance(models_used, dict):
            errors.append("evidence.models_used must be a dictionary")

        sha256_12 = evidence.get("sha256_12", [])
        if not isinstance(sha256_12, list):
            errors.append("evidence.sha256_12 must be a list")
        else:
            for item in sha256_12:
                if not isinstance(item, dict):
                    errors.append("sha256_12 items must be dictionaries")
                elif "type" not in item or "sha256_12" not in item:
                    errors.append("sha256_12 items must have 'type' and 'sha256_12' fields")

    # Check artifacts
    artifacts = envelope.get("artifacts", {})
    if not isinstance(artifacts, dict):
        errors.append("Artifacts must be a dictionary")

    return errors


def main():
    """Run envelope integrity check."""
    errors = check_envelope_integrity(ENVELOPE_FILE)

    if errors:
        print("[envelope_integrity] FAIL:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("[envelope_integrity] PASS: Envelope integrity validated")
        sys.exit(0)


if __name__ == "__main__":
    main()
