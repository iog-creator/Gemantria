#!/usr/bin/env python
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PM_BOOT = ROOT / "share" / "pm_boot"

REQUIRED_FILES = [
    "PM_KERNEL.json",
    "PM_BOOTSTRAP_STATE.json",
    "REALITY_GREEN_SUMMARY.json",
    "HANDOFF_KERNEL.json",
    "PHASE24_INDEX.md",
    "PHASE25_INDEX.md",
    "PHASE26_INDEX.md",
    "PHASE27_INDEX.md",
    "SHARE_FOLDER_ANALYSIS.md",
    "EXECUTION_CONTRACT.md",
    "GITHUB_WORKFLOW_CONTRACT.md",
    "ORCHESTRATOR_REALITY.md",
    "AGENTS.md",
    "PM_CONTRACT.md",
    "PM_AND_OPS_BEHAVIOR_CONTRACT.md",
    "PM_BOOT_CONTRACT.md",
    "PM_BEHAVIOR_CONTRACT.md",
    "CURSOR_WORKFLOW_CONTRACT.md",
    "050-ops-contract.mdc",
    "051-cursor-insight.mdc",
    "052-tool-priority.mdc",
]

OPTIONAL_FILES = [
    "planning_context.json",
    "PM_CONTRACT_STRICT_SSOT_DMS.md",
    "CURSOR_WORKFLOW_CONTRACT_INSTALLED.md",
    "PHASE26_OPS_BOOT_SPEC.md",
]


def main() -> int:
    result = {
        "ok": True,
        "pm_boot_dir": str(PM_BOOT),
        "missing_required": [],
        "missing_optional": [],
        "logs_dir_present": False,
    }

    if not PM_BOOT.exists():
        result["ok"] = False
        result["missing_required"] = REQUIRED_FILES.copy()
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1

    # Check required files
    for name in REQUIRED_FILES:
        path = PM_BOOT / name
        if not path.exists():
            result["ok"] = False
            result["missing_required"].append(name)

    # Check optional files
    for name in OPTIONAL_FILES:
        path = PM_BOOT / name
        if not path.exists():
            result["missing_optional"].append(name)

    # Check logs directory presence (retention policy can come later)
    logs_dir = PM_BOOT / "logs"
    result["logs_dir_present"] = logs_dir.exists()

    if not result["logs_dir_present"]:
        # For now we only warn if logs/ is missing, we don't fail.
        result.setdefault("warnings", []).append("logs directory missing; retention policy not enforced yet")

    # Exit code based on required files only
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
