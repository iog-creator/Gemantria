#!/usr/bin/env python3
"""
PLAN-080 E97 — Gatekeeper / Guard Shim Coverage Manifest

This script performs a lightweight, hermetic coverage audit over the
Phase-1 violation codes used by the Gatekeeper + Guard Shim.

It:
- Defines the Phase-1 violation code set (SSOT).
- Greps the test suite (agentpm/tests) for each violation code string.
- Emits evidence/gatekeeper_coverage.json summarizing which codes
  are referenced by tests.

This is NOT line-by-line coverage; it's a structural "is each violation
code exercised somewhere in tests?" audit, suitable for CI/tagproof.
"""

import json
import pathlib
import subprocess
from typing import Dict

ROOT = pathlib.Path(__file__).resolve().parents[2]
TEST_ROOT = ROOT / "agentpm" / "tests"
OUT_PATH = ROOT / "evidence" / "gatekeeper_coverage.json"

VIOLATION_CODES = [
    "MISSING_POR",
    "ARG_SCHEMA_INVALID",
    "RING_VIOLATION",
    "PROVENANCE_MISMATCH",
    "FORBIDDEN_TOOL",
    "BUDGET_EXCEEDED",
    "RETRY_EXHAUSTED",
]


def grep_for_code(code: str) -> bool:
    """
    Returns True if the violation code string appears anywhere under agentpm/tests.
    Uses `git grep` when available, else falls back to Python scanning.
    """
    if not TEST_ROOT.exists():
        return False

    # Prefer git grep when repo is available
    git_dir = ROOT / ".git"
    if git_dir.exists():
        try:
            result = subprocess.run(
                ["git", "grep", "-n", code, str(TEST_ROOT)],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=False,
            )
            return bool(result.stdout.strip())
        except Exception:
            # Fall back to Python scanning
            pass

    for path in TEST_ROOT.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        if code in text:
            return True
    return False


def main() -> int:
    coverage: Dict[str, bool] = {}
    for code in VIOLATION_CODES:
        coverage[code] = grep_for_code(code)

    payload = {
        "violation_codes": VIOLATION_CODES,
        "coverage": coverage,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
