#!/usr/bin/env python3
"""
SSOT Schema Verification Guard

Validates exports against SSOT schemas for graph-stats, graph-patterns, temporal-patterns.
"""

import json
import glob
import sys
from jsonschema import validate, Draft202012Validator


def load(p):
    """Load JSON file."""
    return json.load(open(p))


def main():
    """Main SSOT verification."""
    schemas = {
        "graph-stats": "docs/SSOT/schemas/graph-stats.schema.json",
        "graph-patterns": "docs/SSOT/schemas/graph-patterns.schema.json",
        "temporal-patterns": "docs/SSOT/schemas/temporal-patterns.schema.json",
    }

    targets = {
        "graph-stats": sorted(glob.glob("share/exports/graph_stats*.json")),
        "graph-patterns": sorted(glob.glob("share/exports/graph_patterns*.json")),
        "temporal-patterns": sorted(glob.glob("share/exports/temporal_patterns*.json")),
    }

    all_passed = True

    for k, schema_path in schemas.items():
        try:
            schema = load(schema_path)
        except FileNotFoundError:
            print(f"SSOT_SKIP {k}: schema not found at {schema_path}")
            continue

        Draft202012Validator.check_schema(schema)

        for t in targets[k]:
            try:
                validate(load(t), schema)
                print(f"SSOT_OK {k}: {t}")
            except Exception as e:
                print(f"SSOT_FAIL {k}: {t} - {e}")
                all_passed = False

    if not all_passed:
        sys.exit(1)

    print("SSOT_VERIFY_OK")


if __name__ == "__main__":
    main()
