#!/usr/bin/env python3
"""
OA Tools Interface (Phase 27.E Batch 3)

Thin, typed wrappers for pmagent commands that OA is allowed to invoke.
All functions are pure read-only; no DSPy imports.

OA must use these wrappers rather than arbitrary shell commands.
Each function corresponds 1:1 with an entry in docs/SSOT/oa/OA_TOOLS_REGISTRY.md.

Safety constraints:
- No writes to git, DB, or kernel surfaces
- No direct subprocess calls except via existing pmagent helpers
- All functions return typed dict structures for DSPy consumption
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


# Paths relative to repo root
ROOT = Path(__file__).resolve().parents[2]
SHARE = ROOT / "share"

# Kernel surface paths
PM_BOOTSTRAP_STATE = SHARE / "PM_BOOTSTRAP_STATE.json"
SSOT_SURFACE = SHARE / "SSOT_SURFACE_V17.json"
REALITY_GREEN_SUMMARY = SHARE / "REALITY_GREEN_SUMMARY.json"
HANDOFF_KERNEL = SHARE / "HANDOFF_KERNEL.json"

# Guards directory
GUARDS_DIR = ROOT / "scripts" / "guards"

# Allowed guard names for oa.guard.run
ALLOWED_GUARDS = frozenset(
    {
        "db_health",
        "lm_health",
        "oa_state",
        "agents_md_sync",
        "share_sync",
        "dms_alignment",
        "dms_share_alignment",
        "bootstrap_consistency",
        "reality_green",
    }
)


class OAToolError(Exception):
    """Raised when an OA tool invocation fails."""

    pass


def _load_json_surface(path: Path) -> dict[str, Any]:
    """Load a JSON surface file, returning empty dict if missing."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        raise OAToolError(f"Failed to load {path.name}: {e}") from e


def kernel_status() -> dict[str, Any]:
    """
    OA tool: oa.kernel_status

    Get current kernel mode, health, and interpretation.
    Wraps `pmagent handoff kernel-interpret --format json`.

    Returns:
        dict with mode, health, interpretation keys

    Raises:
        OAToolError: If kernel interpret fails
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pmagent.handoff.commands", "kernel-interpret", "--format", "json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            # Try to parse error from output
            error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
            raise OAToolError(f"kernel-interpret failed: {error_msg}")

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise OAToolError(f"Invalid JSON from kernel-interpret: {e}") from e

    except subprocess.TimeoutExpired as e:
        raise OAToolError("kernel-interpret timed out") from e
    except FileNotFoundError as e:
        raise OAToolError(f"pmagent not found: {e}") from e


def reality_check() -> dict[str, Any]:
    """
    OA tool: oa.reality_check

    Run reality.green validation and return structured results.
    Instead of running the full guard (which may take time), loads the
    cached REALITY_GREEN_SUMMARY.json for quick access.

    For a fresh check, use run_guard("reality_green").

    Returns:
        dict with reality_green, total_checks, passed_checks, failed_checks, checks
    """
    summary = get_reality_summary()

    if not summary:
        return {
            "reality_green": False,
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": ["No reality summary available"],
            "checks": [],
            "error": "REALITY_GREEN_SUMMARY.json not found",
        }

    # Normalize to expected format
    checks = summary.get("checks", [])
    passed = [c for c in checks if c.get("passed", False)]
    failed = [c for c in checks if not c.get("passed", True)]

    return {
        "reality_green": summary.get("reality_green", False),
        "total_checks": len(checks),
        "passed_checks": len(passed),
        "failed_checks": [c.get("name", "unknown") for c in failed],
        "checks": checks,
    }


def run_guard(name: str) -> dict[str, Any]:
    """
    OA tool: oa.guard.run

    Run a specific guard script and return results.
    Only guards in ALLOWED_GUARDS can be run.

    Args:
        name: Guard name (e.g., "db_health", "oa_state")

    Returns:
        dict with guard results (structure varies by guard)

    Raises:
        OAToolError: If guard name not allowed or guard fails
    """
    # Normalize guard name
    guard_name = name.lower().replace("-", "_")

    if guard_name not in ALLOWED_GUARDS:
        allowed_list = ", ".join(sorted(ALLOWED_GUARDS))
        raise OAToolError(f"Guard '{name}' not in allowed list: {allowed_list}")

    guard_script = GUARDS_DIR / f"guard_{guard_name}.py"

    if not guard_script.exists():
        raise OAToolError(f"Guard script not found: {guard_script}")

    try:
        result = subprocess.run(
            [sys.executable, str(guard_script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Try to parse JSON output
        output = result.stdout.strip()
        if output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                # Return raw output if not JSON
                return {
                    "ok": result.returncode == 0,
                    "guard": guard_name,
                    "output": output,
                    "stderr": result.stderr.strip() if result.stderr else None,
                }

        return {
            "ok": result.returncode == 0,
            "guard": guard_name,
            "stderr": result.stderr.strip() if result.stderr else None,
        }

    except subprocess.TimeoutExpired as e:
        raise OAToolError(f"Guard {name} timed out") from e
    except FileNotFoundError as e:
        raise OAToolError(f"Python not found: {e}") from e


def get_bootstrap_state() -> dict[str, Any]:
    """
    OA tool: oa.bootstrap_state

    Load and return PM_BOOTSTRAP_STATE.json content.

    Returns:
        dict with PM boot envelope, or empty dict if missing
    """
    return _load_json_surface(PM_BOOTSTRAP_STATE)


def get_ssot_surface() -> dict[str, Any]:
    """
    OA tool: oa.ssot_surface

    Load and return SSOT_SURFACE_V17.json content.

    Returns:
        dict with phase index, or empty dict if missing
    """
    return _load_json_surface(SSOT_SURFACE)


def get_reality_summary() -> dict[str, Any]:
    """
    OA tool: oa.reality_summary

    Load and return REALITY_GREEN_SUMMARY.json content.

    Returns:
        dict with health status, or empty dict if missing
    """
    return _load_json_surface(REALITY_GREEN_SUMMARY)


def get_handoff_kernel() -> dict[str, Any]:
    """
    OA tool: oa.handoff_kernel

    Load and return HANDOFF_KERNEL.json content.
    This is the kernel bundle used for agent handoffs.

    Returns:
        dict with handoff kernel, or empty dict if missing
    """
    return _load_json_surface(HANDOFF_KERNEL)


# Tool registry for introspection
OA_TOOLS = {
    "oa.kernel_status": kernel_status,
    "oa.reality_check": reality_check,
    "oa.guard.run": run_guard,
    "oa.bootstrap_state": get_bootstrap_state,
    "oa.ssot_surface": get_ssot_surface,
    "oa.reality_summary": get_reality_summary,
    "oa.handoff_kernel": get_handoff_kernel,
}


def get_available_tools() -> list[str]:
    """Return list of all available OA tool IDs."""
    return sorted(OA_TOOLS.keys())


if __name__ == "__main__":
    # Quick test of tools

    print("OA Tools Interface Test")
    print("=" * 40)

    print("\n1. Available tools:")
    for tool_id in get_available_tools():
        print(f"   - {tool_id}")

    print("\n2. Bootstrap state (first 3 keys):")
    bs = get_bootstrap_state()
    if bs:
        for k in list(bs.keys())[:3]:
            print(f"   - {k}: {type(bs[k]).__name__}")
    else:
        print("   (empty)")

    print("\n3. Reality summary (green status):")
    rs = get_reality_summary()
    if rs:
        print(f"   reality_green: {rs.get('reality_green', 'N/A')}")
    else:
        print("   (empty)")

    print("\n4. Reality check (normalized):")
    rc = reality_check()
    print(f"   passed: {rc.get('passed_checks')}/{rc.get('total_checks')}")

    print("\n✓ All tools callable")
