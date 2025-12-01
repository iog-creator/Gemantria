# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""Sync metrics views to contract per ADR-021."""

import json
import os
import glob

METRICS_CONTRACT = "docs/metrics_contract.json"  # SSOT contract location
BADGES_DIR = "share/eval/badges/*.svg"
DASHBOARDS_DIR = "docs/dashboards/*.md"  # Dashboard views


def load_contract():
    """Load the metrics contract."""
    if not os.path.exists(METRICS_CONTRACT):
        raise FileNotFoundError(f"Metrics contract not found at {METRICS_CONTRACT}")
    with open(METRICS_CONTRACT) as f:
        return json.load(f)


def check_sync(contract):
    """Check that metrics views are synchronized with contract."""
    # Required metrics from contract
    required_metrics = contract.get("metrics", [])

    # Check badges exist
    existing_badges = [os.path.basename(b).replace(".svg", "") for b in glob.glob(BADGES_DIR)]
    missing_badges = [m for m in required_metrics if m not in existing_badges]

    if missing_badges:
        raise ValueError(f"Missing badges for metrics: {missing_badges}")

    # Check dashboards exist (if specified in contract)
    required_dashboards = contract.get("dashboards", [])
    existing_dashboards = [
        os.path.basename(d).replace(".md", "") for d in glob.glob(DASHBOARDS_DIR)
    ]
    missing_dashboards = [d for d in required_dashboards if d not in existing_dashboards]

    if missing_dashboards:
        raise ValueError(f"Missing dashboards: {missing_dashboards}")

    # Threshold validation (stub - can be expanded)
    thresholds = contract.get("thresholds", {})
    for _metric, _threshold in thresholds.items():
        # Add specific threshold checks here if needed
        pass

    print("Metrics contract synchronized ✓")


if __name__ == "__main__":
    try:
        contract = load_contract()
        check_sync(contract)
    except Exception as e:
        print(f"Metrics contract sync failed: {e}")
        exit(1)
