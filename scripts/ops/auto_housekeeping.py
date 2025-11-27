#!/usr/bin/env python3
"""
Automatic Housekeeping Enforcement.

Wrapper around `make housekeeping` that detects file changes via git,
runs housekeeping automatically, and fails-closed if housekeeping fails.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def detect_file_changes() -> list[str]:
    """Detect changed files via git."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )
        changed_files = []
        for line in result.stdout.strip().split("\n"):
            if line:
                # git status --porcelain format: XY filename
                # X = index status, Y = working tree status
                status = line[:2]
                filename = line[3:].strip()
                if status != "??":  # Ignore untracked files
                    changed_files.append(filename)
        return changed_files
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Not a git repo or git not available
        return []


def run_auto_housekeeping() -> dict[str, Any]:
    """
    Run automatic housekeeping and return result.

    Returns:
        Dict with keys: ok (bool), output (str), changed_files (list[str])
    """
    changed_files = detect_file_changes()
    timestamp = datetime.now(UTC).isoformat()

    result: dict[str, Any] = {
        "ok": False,
        "timestamp": timestamp,
        "changed_files": changed_files,
        "output": "",
        "error": None,
    }

    try:
        # Run make housekeeping
        print("🔧 Running `make housekeeping`...")
        proc = subprocess.run(
            ["make", "housekeeping"],
            capture_output=True,
            text=True,
            check=True,
        )
        result["ok"] = True
        result["output"] = proc.stdout + proc.stderr
        print("✅ Housekeeping completed successfully")

        # Log to evidence directory
        evidence_dir = Path("evidence/pmagent")
        evidence_dir.mkdir(parents=True, exist_ok=True)
        log_path = evidence_dir / f"housekeeping-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}.json"
        with open(log_path, "w") as f:
            json.dump(result, f, indent=2)

    except subprocess.CalledProcessError as e:
        result["ok"] = False
        result["error"] = str(e)
        result["output"] = e.stdout + e.stderr
        print(f"❌ Housekeeping failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")

    except FileNotFoundError:
        result["ok"] = False
        result["error"] = "make command not found"
        print("❌ `make` command not found - cannot run housekeeping")

    return result


def main() -> int:
    """CLI entry point."""
    result = run_auto_housekeeping()
    if not result["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
