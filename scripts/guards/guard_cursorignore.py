#!/usr/bin/env python3
"""
Guard: Cursor Ignore Policy Enforcement

Validates that `.cursorignore` does not ignore the `share/` directory.
The `share/` directory must be visible to Cursor for proper governance and DMS sync visibility.

Rule Reference: Governance gap identified in PM analysis (2025-12-01)
- `.cursorignore` is not currently governed by DMS or SSOT rules
- This guard enforces the policy that `share/**` must NOT be in `.cursorignore`

Mode Support:
- HINT mode: Emits hints if `share/**` is found (non-blocking)
- STRICT mode: Fails closed if `share/**` is found (blocking)

Usage:
    python scripts/guards/guard_cursorignore.py
    # Or via reality-check integration
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def _is_strict_mode() -> bool:
    """Determine if running in STRICT mode."""
    return os.getenv("STRICT_MODE", "0") == "1" or os.getenv("CI") == "true"


def guard_cursorignore(mode: str = "HINT") -> dict[str, Any]:
    """
    Guard: Check that `.cursorignore` does not ignore `share/**`.

    Args:
        mode: "HINT" (advisory) or "STRICT" (fail-closed)

    Returns:
        Dictionary with guard verdict:
        {
            "ok": bool,
            "mode": str,
            "message": str,
            "details": {
                "cursorignore_path": str,
                "share_pattern_found": bool,
                "line_number": int | None,
                "file_exists": bool,
            },
            "hints": list[str] (if ok=false and mode=HINT)
        }
    """
    cursorignore_path = ROOT / ".cursorignore"
    verdict: dict[str, Any] = {
        "ok": True,
        "mode": mode,
        "message": "",
        "details": {
            "cursorignore_path": str(cursorignore_path),
            "share_pattern_found": False,
            "line_number": None,
            "file_exists": False,
        },
    }

    # Check if file exists
    if not cursorignore_path.exists():
        verdict["ok"] = False
        verdict["message"] = ".cursorignore file is missing"
        verdict["details"]["file_exists"] = False
        if mode == "HINT":
            verdict["hints"] = [".cursorignore file is missing - this may cause Cursor visibility issues"]
        return verdict

    verdict["details"]["file_exists"] = True

    # Read file and check for share/** pattern
    try:
        content = cursorignore_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Check for share/** pattern (exact match or with whitespace)
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            # Match: "share/**" or "share/**" with leading/trailing whitespace
            if stripped == "share/**" or stripped.endswith("share/**"):
                verdict["ok"] = False
                verdict["message"] = (
                    f".cursorignore contains 'share/**' on line {i} - this prevents Cursor from seeing share/ directory"
                )
                verdict["details"]["share_pattern_found"] = True
                verdict["details"]["line_number"] = i
                if mode == "HINT":
                    verdict["hints"] = [
                        f".cursorignore line {i} contains 'share/**' - remove this line to restore Cursor visibility of share/ directory",
                        "This is a tool visibility issue: share/ files exist and DMS sync works, but Cursor cannot see them",
                    ]
                break

    except Exception as e:
        verdict["ok"] = False
        verdict["message"] = f"Error reading .cursorignore: {e}"
        if mode == "HINT":
            verdict["hints"] = [f"Failed to read .cursorignore: {e}"]

    return verdict


def main() -> int:
    """Run guard and print JSON verdict."""
    mode = "STRICT" if _is_strict_mode() else "HINT"
    verdict = guard_cursorignore(mode=mode)

    # Print JSON verdict to stdout
    print(json.dumps(verdict, indent=2))

    # Exit code: 0 if ok, 1 if not ok (STRICT mode only)
    if mode == "STRICT" and not verdict["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
