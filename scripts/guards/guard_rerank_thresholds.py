#!/usr/bin/env python3
"""Guard for rerank threshold validation.

Validates that edge_strength values meet the strict threshold.
Operates in HINT mode by default (non-blocking) or STRICT mode (fail-closed).

Environment variables:
- RERANK_THRESHOLD_STRICT: Strict threshold (default: 0.90)
- STRICT_RERANK_THRESH: Set to '1' for fail-closed behavior

Exit codes:
- 0: HINT mode or STRICT mode passed
- 1: STRICT mode failed (edges below threshold)
- 2: File missing or malformed
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import time


def main() -> int:
    """Check rerank threshold compliance."""
    # Configuration
    report_path = pathlib.Path("share/eval/rerank_blend_report.json")
    strict_thr = float(os.getenv("RERANK_THRESHOLD_STRICT", "0.90"))
    strict = os.getenv("STRICT_RERANK_THRESH") == "1"

    # Check file exists
    if not report_path.exists():
        result = {
            "schema": "guard.rerank-thresholds.v1",
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "ok": False,
            "mode": "STRICT" if strict else "HINT",
            "thresholds": {"strict": strict_thr},
            "note": "share/eval/rerank_blend_report.json not found (run analytics.rerank.blend first)",
        }
        print(json.dumps(result, indent=2))
        return 2 if strict else 0

    # Load and analyze
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        result = {
            "schema": "guard.rerank-thresholds.v1",
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "ok": False,
            "mode": "STRICT" if strict else "HINT",
            "thresholds": {"strict": strict_thr},
            "note": f"JSON parse error: {e}",
        }
        print(json.dumps(result, indent=2))
        return 2 if strict else 0

    # Extract counts from report
    below_strict = data.get("below", {}).get("strict", 0)
    ok_strict = data.get("ok", {}).get("strict", 0)
    total_edges = data.get("total_edges", 0)
    report_thresholds = data.get("thresholds", {})
    report_strict = report_thresholds.get("strict", strict_thr)

    # Use threshold from report if available, otherwise use env/default
    effective_thr = report_strict if report_strict else strict_thr

    # Determine pass/fail (all edges must meet strict threshold)
    passed = below_strict == 0 and total_edges > 0
    if total_edges == 0:
        passed = True  # Empty graph is valid

    result = {
        "schema": "guard.rerank-thresholds.v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "ok": passed,
        "mode": "STRICT" if strict else "HINT",
        "thresholds": {"strict": effective_thr},
        "below": {"strict": below_strict},
        "ok_count": {"strict": ok_strict},
        "counts": {"total_edges": total_edges},
        "note": (
            f"Rerank threshold check: {ok_strict}/{total_edges} edges >= {effective_thr} "
            f"({'✅ PASS' if passed else f'❌ FAIL ({below_strict} edges < {effective_thr})'})"
        ),
    }
    print(json.dumps(result, indent=2))

    # Save to evidence
    pathlib.Path("evidence").mkdir(exist_ok=True)
    evidence_path = pathlib.Path("evidence/guard_rerank_thresholds.json")
    evidence_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    if strict and not passed:
        print(
            f"GUARD FAILED: {below_strict} edges below strict threshold {effective_thr} (STRICT mode)",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
