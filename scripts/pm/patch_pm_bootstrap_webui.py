#!/usr/bin/env python3
"""
patch_pm_bootstrap_webui.py

Wrapper around scripts/pm/generate_pm_bootstrap_state.py that preserves
the existing `webui.console_v2` section in share/PM_BOOTSTRAP_STATE.json.

Behavior:
- If share/PM_BOOTSTRAP_STATE.json exists, read and remember `.webui.console_v2`.
- Run the original generator script.
- Read the newly written PM_BOOTSTRAP_STATE.json.
- If an old `.webui.console_v2` existed, merge it back into the new state.
- Write the merged state back to disk.

This script is the canonical entrypoint for regenerating PM bootstrap in
Phase 23 and beyond.

Usage:
    python scripts/pm/patch_pm_bootstrap_webui.py

Or via Make:
    make pm.bootstrap.state
"""

from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP_PATH = REPO_ROOT / "share" / "PM_BOOTSTRAP_STATE.json"
GENERATOR_PATH = REPO_ROOT / "scripts" / "pm" / "generate_pm_bootstrap_state.py"


def load_json(path: Path) -> dict:
    """Load JSON from path, returning empty dict on failure."""
    try:
        text = path.read_text(encoding="utf-8")
        return json.loads(text)
    except Exception:
        return {}


def save_json(path: Path, data: dict) -> None:
    """Save dict as JSON to path."""
    text = json.dumps(data, indent=2, sort_keys=True)
    path.write_text(text + "\n", encoding="utf-8")


def merge_console_section(old_state: dict, new_state: dict) -> dict:
    """Merge old webui.console_v2 into new_state if present.

    - If old_state has webui.console_v2, ensure new_state["webui"]["console_v2"]
      matches it (overwriting any auto-generated stub).
    - If new_state has no "webui" key, it will be created.
    """
    old_webui = old_state.get("webui") or {}
    old_console_v2 = old_webui.get("console_v2")
    if not old_console_v2:
        # Nothing to preserve
        return new_state

    merged = deepcopy(new_state)
    merged_webui = merged.get("webui") or {}
    merged_webui["console_v2"] = old_console_v2
    merged["webui"] = merged_webui
    return merged


def run_generator() -> None:
    """Run the existing bootstrap generator script."""
    cmd = [sys.executable, str(GENERATOR_PATH)]
    completed = subprocess.run(cmd, cwd=REPO_ROOT)
    if completed.returncode != 0:
        raise SystemExit(f"generate_pm_bootstrap_state.py failed with exit code {completed.returncode}")


def main() -> None:
    print("[patch_pm_bootstrap_webui] Starting...", file=sys.stderr)

    # Load old state (if any)
    old_state = {}
    if BOOTSTRAP_PATH.exists():
        old_state = load_json(BOOTSTRAP_PATH)
        old_console = old_state.get("webui", {}).get("console_v2")
        if old_console:
            print(
                "[patch_pm_bootstrap_webui] Found existing webui.console_v2, will preserve",
                file=sys.stderr,
            )

    # Run the original generator
    print("[patch_pm_bootstrap_webui] Running generate_pm_bootstrap_state.py...", file=sys.stderr)
    run_generator()

    # Load new state
    new_state = load_json(BOOTSTRAP_PATH)
    if not new_state:
        raise SystemExit(f"Expected JSON at {BOOTSTRAP_PATH}, but file is missing or invalid.")

    # Merge old webui.console_v2 into new state (if it existed)
    merged_state = merge_console_section(old_state, new_state)

    # Save merged state
    save_json(BOOTSTRAP_PATH, merged_state)

    # Print confirmation
    has_console = bool(merged_state.get("webui", {}).get("console_v2"))
    status = "PRESERVED" if has_console else "NO_PREVIOUS_CONSOLE_V2"
    print(
        f"[patch_pm_bootstrap_webui] Completed. console_v2 status: {status}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
