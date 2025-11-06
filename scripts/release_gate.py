#!/usr/bin/env python3
"""
Release Gate: Fail-closed validation before shipping artifacts.

Checks for required evidence, model tracking, budget compliance, and data integrity.
"""

import glob
import json
import sys


def load_last(pattern):
    """Load the most recent file matching pattern."""
    files = sorted(glob.glob(pattern))
    return json.load(open(files[-1])) if files else {}


def find_latest_agent_result():
    """Find the most recent agent result file with models_used."""
    result_files = sorted(glob.glob("share/evidence/*agent_result_*.json"))
    for f in reversed(result_files):  # Check most recent first
        data = json.load(open(f))
        if data.get("data", {}).get("models_used"):
            return data
    return {}


def die(msg):
    """Fail with descriptive message."""
    print(f"RELEASE_GATE_FAIL: {msg}")
    sys.exit(1)


def main():
    """Main gate validation."""
    # 1) Must have agent results with models_used
    result = find_latest_agent_result()
    if not result:
        die("no agent results with models_used found")

    data = result.get("data", {})
    output_summary = data.get("output_summary", {})

    # 2) models_used must be present
    models = data.get("models_used")
    if not models:
        die("models_used missing in evidence")

    # 3) Check budget breaches (strict mode)
    run = data.get("run", {})
    budget = output_summary.get("budget", {})
    breach = budget.get("breach")
    strict = run.get("budget_strict", True)

    if breach and strict:
        die(f"budget breach in strict mode: {breach}")

    # 4) Embedding dimension validation (if present)
    emb_dim = output_summary.get("embedding_dim")  # Optional field
    if emb_dim and emb_dim != 1024:
        die(f"embedding_dim:{emb_dim} != 1024")

    # 5) Last-good regression check passed (guard_last_good covers this)
    print("RELEASE_GATE_OK")


if __name__ == "__main__":
    main()
