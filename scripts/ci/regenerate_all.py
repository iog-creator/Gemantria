#!/usr/bin/env python3
"""
PLAN-080 E98 — Full Extraction & Atlas + Exports Regeneration

This orchestrator regenerates all core extraction and export artifacts
from scratch in a deterministic order.

Steps:
1. Export graph_latest.json (via scripts/export_graph.py)
2. Export stats, patterns, temporal, forecast (via scripts/export_stats.py)

Emits evidence/regenerate_all_receipt.json with execution details.
"""

import json
import pathlib
import subprocess
import sys
import time
from datetime import datetime, UTC
from typing import Any, Dict

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT_PATH = ROOT / "evidence" / "regenerate_all_receipt.json"
EXPORTS_DIR = ROOT / "exports"

# Expected artifacts (per SSOT)
EXPECTED_ARTIFACTS = [
    "exports/graph_latest.json",
    "exports/graph_stats.json",
    "exports/graph_patterns.json",
    "exports/temporal_patterns.json",
    "exports/pattern_forecast.json",
]


def run_step(name: str, cmd: list[str], cwd: pathlib.Path) -> Dict[str, Any]:
    """Run a single regeneration step and return timing/exit info."""
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        duration = time.time() - start
        return {
            "name": name,
            "exit_code": result.returncode,
            "duration_s": round(duration, 2),
            "success": result.returncode == 0,
            "stderr": result.stderr[:500] if result.stderr else None,
        }
    except Exception as e:
        duration = time.time() - start
        return {
            "name": name,
            "exit_code": -1,
            "duration_s": round(duration, 2),
            "success": False,
            "error": str(e)[:500],
        }


def check_artifacts() -> list[str]:
    """Check which expected artifacts exist on disk."""
    found = []
    for artifact in EXPECTED_ARTIFACTS:
        path = ROOT / artifact
        if path.exists():
            found.append(artifact)
    return found


def main() -> int:
    """Main regeneration orchestrator."""
    steps: list[Dict[str, Any]] = []
    all_success = True

    # Step 1: Export graph_latest.json
    step1 = run_step(
        "export_graph",
        [sys.executable, "scripts/export_graph.py"],
        ROOT,
    )
    steps.append(step1)
    if not step1["success"]:
        all_success = False

    # Step 2: Export stats, patterns, temporal, forecast
    step2 = run_step(
        "export_stats",
        [sys.executable, "scripts/export_stats.py"],
        ROOT,
    )
    steps.append(step2)
    if not step2["success"]:
        all_success = False

    # Check artifacts
    artifacts = check_artifacts()
    missing_artifacts = [a for a in EXPECTED_ARTIFACTS if a not in artifacts]

    # Build receipt
    receipt = {
        "ok": all_success and len(missing_artifacts) == 0,
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "steps": steps,
        "artifacts": artifacts,
        "missing_artifacts": missing_artifacts,
        "expected_artifacts": EXPECTED_ARTIFACTS,
    }

    # Write receipt
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    # Print summary
    print(json.dumps(receipt, indent=2))

    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
