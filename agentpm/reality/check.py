#!/usr/bin/env python3
"""
Reality Check Module

Phase-8 Integration: Single unified command for system environment validation.
Checks env/DSN, DB/control plane, LM/models, exports, and eval smokes with HINT/STRICT modes.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

# Import existing helpers
from scripts.config.env import get_rw_dsn, get_ro_dsn, get_bible_db_dsn
from scripts.guards.guard_lm_health import check_lm_health
from scripts.control.control_summary import compute_control_summary
from agentpm.lm.lm_status import compute_lm_status


# Hermetic JSON loader pattern from existing code
def load_json_file(path: Path) -> dict[str, Any] | None:
    """Load JSON file, return None if missing or invalid."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def check_env_and_dsn() -> dict[str, Any]:
    """Check env variables and DSN availability.

    Returns:
        Dictionary with env and DSN status.
    """
    result: dict[str, Any] = {
        "ok": False,
        "dsn_ok": False,
        "details": {},
    }

    # Check DSN availability
    try:
        rw_dsn = get_rw_dsn()
        ro_dsn = get_ro_dsn()
        bible_dsn = get_bible_db_dsn()

        result["details"]["dsns"] = {
            "rw": bool(rw_dsn),
            "ro": bool(ro_dsn),
            "bible": bool(bible_dsn),
        }

        # DSN is OK if we have at least RW DSN
        result["dsn_ok"] = bool(rw_dsn)
        result["ok"] = True

    except Exception as e:
        result["details"]["error"] = str(e)

    return result


def check_db_and_control() -> dict[str, Any]:
    """Check DB and control plane status.

    Returns:
        Dictionary with DB and control plane status.
    """
    result: dict[str, Any] = {
        "ok": False,
        "control_schema": "control",
        "tables_expected": 0,
        "tables_present": 0,
    }

    # Use existing control summary helper
    try:
        summary = compute_control_summary()
        result.update(summary)
        result["ok"] = summary.get("ok", False)
    except Exception as e:
        result["details"] = {"error": str(e)}

    return result


def check_lm_health_status() -> dict[str, Any]:
    """Check LM health and status.

    Returns:
        Dictionary with LM health and slot status.
    """
    result: dict[str, Any] = {
        "ok": False,
        "provider": "unknown",
        "slots": {},
    }

    try:
        # Get LM health
        health = check_lm_health()
        result.update(health)

        # Get detailed LM status
        status = compute_lm_status()
        result["slots"] = status.get("slots", {})

    except Exception as e:
        result["details"] = {"error": str(e)}

    return result


def check_control_plane_exports() -> dict[str, Any]:
    """Check control plane export files.

    Returns:
        Dictionary with export file status.
    """
    result: dict[str, Any] = {
        "ok": True,  # Hermetic: missing files are OK in HINT mode
        "lm_indicator": None,
        "compliance_head": None,
        "kb_docs_head": None,
        "mcp_catalog": None,
    }

    share_dir = ROOT / "share" / "atlas" / "control_plane"

    # Check each export file
    exports_to_check = {
        "lm_indicator": "lm_indicator.json",
        "compliance_head": "compliance.head.json",
        "kb_docs_head": "kb_docs.head.json",
        "mcp_catalog": "mcp_catalog.json",
    }

    for key, filename in exports_to_check.items():
        file_path = share_dir / filename
        data = load_json_file(file_path)
        result[key] = data

        # In HINT mode, missing files are OK (None)
        # In STRICT mode, we'll check this in the orchestrator

    return result


def run_eval_smoke() -> dict[str, Any]:
    """Run eval smoke tests via make targets.

    Returns:
        Dictionary with smoke test results.
    """
    result: dict[str, Any] = {
        "ok": True,
        "targets": ["ci.exports.smoke", "eval.graph.calibrate.adv"],
        "messages": [],
    }

    # Run each target
    for target in result["targets"]:
        try:
            proc = subprocess.run(
                ["make", target],
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            if proc.returncode != 0:
                result["ok"] = False
                result["messages"].append(f"{target}: exit {proc.returncode}")
                if proc.stderr.strip():
                    result["messages"].append(f"{target} stderr: {proc.stderr.strip()[:200]}")
            else:
                result["messages"].append(f"{target}: OK")

        except Exception as e:
            result["ok"] = False
            result["messages"].append(f"{target}: exception {e!s}")

    return result


def reality_check(mode: str = "HINT", skip_dashboards: bool = False) -> dict[str, Any]:
    """Run comprehensive reality check.

    Args:
        mode: "HINT" or "STRICT"
        skip_dashboards: If True, skip exports and eval smoke checks

    Returns:
        Dictionary with complete verdict
    """
    timestamp = datetime.now(UTC).isoformat()

    # Run all checks
    env_result = check_env_and_dsn()
    db_result = check_db_and_control()
    lm_result = check_lm_health_status()
    exports_result = check_control_plane_exports() if not skip_dashboards else {"ok": True, "skipped": True}
    eval_result = run_eval_smoke() if not skip_dashboards else {"ok": True, "skipped": True}

    # Build hints based on results
    hints: list[str] = []

    # Determine overall_ok based on mode
    hard_fail = False

    # Core infra (env/DSN, DB/control) must always be OK
    if not env_result.get("ok") or not db_result.get("ok"):
        hard_fail = True
        hints.append("Critical infrastructure failure: env/DSN or DB/control-plane")

    # In STRICT mode, everything must be OK
    if mode == "STRICT":
        if not lm_result.get("ok"):
            hard_fail = True
            hints.append("LM not OK in STRICT mode")
        if not exports_result.get("ok"):
            hard_fail = True
            hints.append("Control plane exports not OK in STRICT mode")
        if not eval_result.get("ok"):
            hard_fail = True
            hints.append("Eval smoke failed in STRICT mode")

    # In HINT mode, add hints for non-critical failures
    elif mode == "HINT":
        if not lm_result.get("ok"):
            hints.append("LM configuration incomplete")
        if not exports_result.get("ok"):
            hints.append("Control plane exports missing or invalid")
        if not eval_result.get("ok"):
            hints.append("Eval smoke tests failed")

    verdict = {
        "command": "reality.check",
        "mode": mode,
        "timestamp": timestamp,
        "env": env_result,
        "db": db_result,
        "lm": lm_result,
        "exports": exports_result,
        "eval_smoke": eval_result,
        "hints": hints,
        "overall_ok": not hard_fail,
    }

    return verdict


def summarize_live_status(verdict: dict[str, Any]) -> str:
    """Build a single-line LIVE STATUS banner based on subsystem health.

    This is human-facing; do not change exit codes here.

    Args:
        verdict: The verdict dictionary

    Returns:
        Single-line banner string
    """
    mode = verdict.get("mode", "UNKNOWN").upper()
    db_ok = verdict.get("db", {}).get("ok", False)
    lm_ok = verdict.get("lm", {}).get("ok", False)

    if db_ok and lm_ok:
        status = "READY"
    else:
        status = "NOT READY"

    parts = [f"LIVE STATUS: {status}", f"MODE={mode}"]
    parts.append(f"DB={'OK' if db_ok else 'OFF'}")
    parts.append(f"LM={'OK' if lm_ok else 'OFF'}")

    # HINT-mode extra note to avoid confusion
    if mode == "HINT":
        parts.append("(HINT is CI/dev-only; this does NOT guarantee services are live)")

    return " | ".join(parts)


def print_human_summary(verdict: dict[str, Any], file=None) -> None:
    """Print human-readable summary of verdict.

    Args:
        verdict: The verdict dictionary
        file: File to write to (default: sys.stderr)
    """
    if file is None:
        file = sys.stderr

    # Print LIVE STATUS banner first
    banner = summarize_live_status(verdict)
    print(banner, file=file)
    print("", file=file)

    mode = verdict.get("mode", "UNKNOWN")
    overall_ok = verdict.get("overall_ok", False)
    hints = verdict.get("hints", [])

    print(f"[pmagent] reality.check (mode={mode})", file=file)
    print("", file=file)

    # Status lines
    components = [
        ("Env / DSN", verdict.get("env", {}).get("ok", False)),
        ("DB / Control", verdict.get("db", {}).get("ok", False)),
        ("LM / Models", verdict.get("lm", {}).get("ok", False)),
        ("Exports / Atlas", verdict.get("exports", {}).get("ok", False)),
        ("Eval smoke", verdict.get("eval_smoke", {}).get("ok", False)),
    ]

    for name, ok in components:
        status = "OK" if ok else "FAIL"
        print(f"{name}: {status}", file=file)

    # Hints section
    if hints:
        print("", file=file)
        print("Hints:", file=file)
        for hint in hints:
            print(f"- {hint}", file=file)

    # Overall result
    print("", file=file)
    result_msg = "PASS" if overall_ok else "FAIL"
    print(f"Result: {mode} mode: overall {result_msg}", file=file)
