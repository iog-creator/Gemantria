"""
Handoff Status Helpers

Helper functions for pmagent handoff status and boot commands.
Implements Phase 26.B boot envelope generation per PHASE26_PMAGENT_BOOT_SPEC.md.
"""

from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

# Default paths
REPO_ROOT = Path(".").resolve()
SHARE_DIR = REPO_ROOT / "share"
HANDOFF_DIR = SHARE_DIR / "handoff"


def load_kernel(kernel_path: Path | None = None) -> dict[str, Any]:
    """
    Load PM_KERNEL.json.

    Args:
        kernel_path: Path to kernel JSON (default: share/handoff/PM_KERNEL.json)

    Returns:
        Kernel dict with fields: current_phase, branch, ground_truth_files, etc.

    Raises:
        FileNotFoundError: If kernel file doesn't exist
        json.JSONDecodeError: If kernel is malformed
    """
    if kernel_path is None:
        kernel_path = HANDOFF_DIR / "PM_KERNEL.json"

    if not kernel_path.exists():
        raise FileNotFoundError(f"Kernel not found: {kernel_path}")

    with open(kernel_path, encoding="utf-8") as f:
        return json.load(f)


def load_bootstrap(bootstrap_path: Path | None = None) -> dict[str, Any]:
    """
    Load PM_BOOTSTRAP_STATE.json.

    Args:
        bootstrap_path: Path to bootstrap JSON (default: share/PM_BOOTSTRAP_STATE.json)

    Returns:
        Bootstrap dict with meta, phases, surfaces, etc.

    Raises:
        FileNotFoundError: If bootstrap file doesn't exist
        json.JSONDecodeError: If bootstrap is malformed
    """
    if bootstrap_path is None:
        bootstrap_path = SHARE_DIR / "PM_BOOTSTRAP_STATE.json"

    if not bootstrap_path.exists():
        raise FileNotFoundError(f"Bootstrap not found: {bootstrap_path}")

    with open(bootstrap_path, encoding="utf-8") as f:
        return json.load(f)


def load_reality_green(reality_path: Path | None = None) -> dict[str, Any] | None:
    """
    Load REALITY_GREEN_SUMMARY.json if it exists.

    Args:
        reality_path: Path to reality green summary (default: share/REALITY_GREEN_SUMMARY.json)

    Returns:
        Reality green dict or None if file doesn't exist

    Raises:
        json.JSONDecodeError: If file exists but is malformed
    """
    if reality_path is None:
        reality_path = SHARE_DIR / "REALITY_GREEN_SUMMARY.json"

    if not reality_path.exists():
        return None

    with open(reality_path, encoding="utf-8") as f:
        return json.load(f)


def check_consistency(kernel: dict[str, Any], bootstrap: dict[str, Any]) -> list[str]:
    """
    Check kernel ↔ bootstrap consistency.

    Args:
        kernel: Kernel dict
        bootstrap: Bootstrap dict

    Returns:
        List of warning messages (empty if consistent)
    """
    warnings = []

    # Check current_phase match
    kernel_phase = kernel.get("current_phase")
    bootstrap_phase = bootstrap.get("meta", {}).get("current_phase")

    if kernel_phase != bootstrap_phase:
        warnings.append(f"Phase mismatch: kernel={kernel_phase}, bootstrap={bootstrap_phase}")

    # Check last_completed_phase match
    kernel_last = kernel.get("last_completed_phase")
    bootstrap_last = bootstrap.get("meta", {}).get("last_completed_phase")

    if kernel_last != bootstrap_last:
        warnings.append(f"Last completed phase mismatch: kernel={kernel_last}, bootstrap={bootstrap_last}")

    # Check branch match
    kernel_branch = kernel.get("branch")
    bootstrap_branch = bootstrap.get("branch")

    if bootstrap_branch and kernel_branch != bootstrap_branch:
        warnings.append(f"Branch mismatch: kernel={kernel_branch}, bootstrap={bootstrap_branch}")

    return warnings


def compute_degraded_mode(
    kernel: dict[str, Any],
    bootstrap: dict[str, Any],
    health: dict[str, Any] | None,
    consistency_warnings: list[str],
) -> bool:
    """
    Compute whether system is in DEGRADED mode.

    Args:
        kernel: Kernel dict
        bootstrap: Bootstrap dict
        health: Reality green summary or None
        consistency_warnings: List of consistency warnings

    Returns:
        True if degraded, False if normal
    """
    # Degraded if reality_green is false
    if health and not health.get("reality_green", False):
        return True

    # Degraded if kernel/bootstrap inconsistent
    if consistency_warnings:
        return True

    # Degraded if any ground truth files missing
    ground_truth = kernel.get("ground_truth_files", [])
    for file_path in ground_truth:
        if not (REPO_ROOT / file_path).exists():
            return True

    return False


def build_status_envelope(
    kernel: dict[str, Any],
    bootstrap: dict[str, Any],
    health: dict[str, Any] | None,
    consistency_warnings: list[str],
) -> dict[str, Any]:
    """
    Build status handoff envelope.

    Args:
        kernel: Kernel dict
        bootstrap: Bootstrap dict
        health: Reality green summary or None
        consistency_warnings: List of consistency warnings

    Returns:
        Status envelope dict matching PHASE26_PMAGENT_BOOT_SPEC.md schema
    """
    degraded = compute_degraded_mode(kernel, bootstrap, health, consistency_warnings)

    # Extract health info
    health_section = {
        "reality_green": health.get("reality_green", True) if health else True,
        "failed_checks": health.get("failed_checks", []) if health else [],
        "source": "share/REALITY_GREEN_SUMMARY.json" if health else None,
    }

    return {
        "ok": True,
        "kernel": {
            "current_phase": kernel.get("current_phase"),
            "last_completed_phase": kernel.get("last_completed_phase"),
            "branch": kernel.get("branch"),
            "generated_at_utc": kernel.get("generated_at_utc"),
            "ground_truth_files": kernel.get("ground_truth_files", []),
        },
        "health": health_section,
        "degraded": degraded,
        "warnings": consistency_warnings,
    }


def build_boot_envelope(
    kernel: dict[str, Any],
    bootstrap: dict[str, Any],
    health: dict[str, Any] | None,
    consistency_warnings: list[str],
) -> dict[str, Any]:
    """
    Build PM boot envelope.

    Args:
        kernel: Kernel dict
        bootstrap: Bootstrap dict
        health: Reality green summary or None
        consistency_warnings: List of consistency warnings

    Returns:
        Boot envelope dict matching PHASE26_PMAGENT_BOOT_SPEC.md schema
    """
    degraded = compute_degraded_mode(kernel, bootstrap, health, consistency_warnings)
    mode = "DEGRADED" if degraded else "NORMAL"

    # Extract current phase surfaces from bootstrap
    current_phase = kernel.get("current_phase")
    phases = bootstrap.get("phases", {})
    current_phase_surfaces = []

    if current_phase and current_phase in phases:
        # Collect values from phase dict (these are surface paths)
        phase_data = phases[current_phase]
        if isinstance(phase_data, dict):
            current_phase_surfaces = [
                v for v in phase_data.values() if v and isinstance(v, str) and not v.startswith("Phase")
            ]

    # Add phase index if available
    phase_index = f"docs/SSOT/PHASE{current_phase}_INDEX.md"
    if (REPO_ROOT / phase_index).exists() and phase_index not in current_phase_surfaces:
        current_phase_surfaces.insert(0, phase_index)

    # Build health section with remediation docs
    failed_checks = health.get("failed_checks", []) if health else []
    remediation_docs = []

    # Map common failures to docs
    for check in failed_checks:
        if "DB" in check or "Database" in check:
            remediation_docs.append("docs/hints/HINT-DB-002-postgres-not-running.md")
            remediation_docs.append("docs/SSOT/DMS_QUERY_PROTOCOL.md")
        elif "DMS" in check or "Alignment" in check:
            remediation_docs.append("docs/SSOT/DMS_QUERY_PROTOCOL.md")
        elif "Bootstrap" in check:
            remediation_docs.append("docs/SSOT/PM_HANDOFF_PROTOCOL.md")
        elif "Backup" in check:
            remediation_docs.append("docs/SSOT/PHASE24_INDEX.md")

    # Remove duplicates
    remediation_docs = list(dict.fromkeys(remediation_docs))

    # Recommended behavior
    if mode == "DEGRADED":
        pm_script = [
            "Halt phase work.",
            "Explain degraded mode to user.",
            "Define remediation scope only.",
        ]
        oa_behavior = [
            "Explain degraded mode to user.",
            "Refuse normal analysis until remediation is defined.",
        ]
        ops_behavior = [
            "Run only PM-approved remediation commands.",
            "Do not run destructive targets.",
        ]
    else:
        pm_script = [
            f"Review Phase {current_phase} objectives.",
            "Proceed with phase work using kernel ground truth files.",
        ]
        oa_behavior = [
            f"Assist with Phase {current_phase} objectives.",
            "Use kernel surfaces as authoritative references.",
        ]
        ops_behavior = [
            "Execute PM-authorized commands with kernel preflight.",
            "Verify guards before destructive operations.",
        ]

    return {
        "ok": True,
        "mode": mode,
        "snapshot": {
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "source": "pmagent boot pm",
            "version": "1.0",
        },
        "kernel": {
            "current_phase": kernel.get("current_phase"),
            "last_completed_phase": kernel.get("last_completed_phase"),
            "branch": kernel.get("branch"),
            "generated_at_utc": kernel.get("generated_at_utc"),
            "ground_truth_files": kernel.get("ground_truth_files", []),
        },
        "bootstrap": {
            "phases": phases,
            "current_phase_surfaces": current_phase_surfaces,
            "kb_registry_path": "share/kb_registry.json",
        },
        "health": {
            "reality_green": health.get("reality_green", True) if health else True,
            "failed_checks": failed_checks,
            "remediation_docs": remediation_docs,
            "source": "share/REALITY_GREEN_SUMMARY.json" if health else None,
        },
        "recommended_behavior": {"pm": pm_script, "oa": oa_behavior, "ops": ops_behavior},
    }


def format_status_human(envelope: dict[str, Any]) -> str:
    """
    Format status envelope as human-readable text.

    Args:
        envelope: Status envelope dict

    Returns:
        Human-readable status string
    """
    kernel = envelope["kernel"]
    health = envelope["health"]
    degraded = envelope["degraded"]
    warnings = envelope.get("warnings", [])

    status_icon = "❌" if degraded else "✅"
    status_text = "DEGRADED" if degraded else "GREEN"

    lines = [
        f"{status_icon} Handoff Status: {status_text}",
        f"   Phase: {kernel['current_phase']} (last completed: {kernel['last_completed_phase']})",
        f"   Branch: {kernel['branch']}",
        f"   reality.green: {'FAIL' if not health['reality_green'] else 'PASS'}",
    ]

    if degraded:
        lines.append("")
        if health["failed_checks"]:
            lines.append("   Failed checks:")
            for check in health["failed_checks"]:
                lines.append(f"   - {check}")

        if warnings:
            lines.append("")
            lines.append("   Warnings:")
            for warning in warnings:
                lines.append(f"   - {warning}")

        lines.append("")
        lines.append("   ⚠️  Normal work blocked. Define remediation scope only.")
    else:
        lines.append("")
        lines.append("   Next actions:")
        lines.append(f"   - Review Phase {kernel['current_phase']} objectives")
        lines.append("   - Run kernel check (make kernel.check)")

    return "\n".join(lines)


def format_boot_seed(envelope: dict[str, Any]) -> str:
    """
    Format boot envelope as natural-language seed for PM chat.

    Args:
        envelope: Boot envelope dict

    Returns:
        Natural-language seed text
    """
    kernel = envelope["kernel"]
    mode = envelope["mode"]
    health = envelope["health"]

    lines = [
        "You are the PM of Gemantria.",
        "",
        f"Kernel says: phase {kernel['current_phase']}, branch {kernel['branch']}, mode {mode}.",
    ]

    if mode == "DEGRADED":
        lines.append("")
        if health["failed_checks"]:
            lines.append("Failed checks:")
            for check in health["failed_checks"]:
                docs = [d for d in health.get("remediation_docs", []) if check.lower() in d.lower()]
                doc_ref = f" (see {docs[0]})" if docs else ""
                lines.append(f"- {check}{doc_ref}")

        lines.append("")
        lines.append("You must halt phase work and only define remediation scope until these are fixed.")
    else:
        phase_index = f"PHASE{kernel['current_phase']}_INDEX.md"
        lines.append("")
        lines.append(f"System is healthy. Use {phase_index} as your phase guide.")

    return "\n".join(lines)
