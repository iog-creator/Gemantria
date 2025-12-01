#!/usr/bin/env python3
"""
PLAN-080 E96 — TV Coverage Runner

Re-runs TV-01..TV-05 and writes a machine-readable coverage receipt:
  evidence/tv_coverage_receipt.json

Assumptions:
- Test vectors live in agentpm/tests/test_guarded_calls_tv.py
- Pytest is configured via pytest.ini
- Exit code 0 => all TVs passed

This script is hermetic and DB-off tolerant: it just invokes pytest
for the TV suite and writes a summary JSON.
"""

import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_PATH = ROOT / "evidence" / "tv_coverage_receipt.json"


def run_tv_tests() -> int:
    cmd = [sys.executable, "-m", "pytest", "-q", "agentpm/tests/test_guarded_calls_tv.py"]
    result = subprocess.run(cmd, cwd=ROOT)
    return result.returncode


def main() -> int:
    exit_code = run_tv_tests()
    ok = exit_code == 0
    receipt = {
        "ok": ok,
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "pytest_exit_code": exit_code,
        "suite": "TV-01..TV-05",
        "notes": (
            "All test vectors passed."
            if ok
            else "One or more TV-01..TV-05 tests failed; see pytest output."
        ),
    }
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    # Return pytest exit code so CI can still fail if TVs fail
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
