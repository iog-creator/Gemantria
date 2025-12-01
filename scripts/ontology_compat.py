# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""Check ontology forward compatibility per ADR-020."""

import json
import os

ONTOLOGY_PATH = "share/exports/ontology.json"  # Assume export location
REQUIRED_VERSION = "v1.0"  # Forward compat baseline


def load_ontology():
    """Load the ontology data."""
    if not os.path.exists(ONTOLOGY_PATH):
        raise FileNotFoundError(f"Ontology not found at {ONTOLOGY_PATH}")
    with open(ONTOLOGY_PATH) as f:
        return json.load(f)


def check_compat(ontology):
    """Check ontology forward compatibility."""
    # Version check
    current_version = ontology.get("version", "v0.0")
    if current_version < REQUIRED_VERSION:
        raise ValueError(
            f"Ontology version {current_version} incompatible (required: {REQUIRED_VERSION})"
        )

    # Required fields check
    required = ["nodes", "edges", "temporal"]
    missing = [k for k in required if k not in ontology]
    if missing:
        raise ValueError(f"Missing required ontology keys: {missing}")

    # Schema validation stubs (can be expanded)
    if "nodes" in ontology:
        if not isinstance(ontology["nodes"], list):
            raise ValueError("Ontology nodes must be a list")

    if "edges" in ontology:
        if not isinstance(ontology["edges"], list):
            raise ValueError("Ontology edges must be a list")

    print("Ontology forward compatible ✓")


if __name__ == "__main__":
    try:
        ontology = load_ontology()
        check_compat(ontology)
    except Exception as e:
        print(f"Ontology compatibility check failed: {e}")
        exit(1)
