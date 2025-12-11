import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHARE = ROOT / "share"
PM_BOOT = SHARE / "pm_boot"


def copy_if_exists(src: Path, dst: Path):
    if not src.exists():
        print(f"[WARN] missing source: {src}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"[OK] {src} -> {dst}")


def main():
    PM_BOOT.mkdir(parents=True, exist_ok=True)
    (PM_BOOT / "logs").mkdir(parents=True, exist_ok=True)

    # Canonical surfaces for PM/OA boot
    candidates = [
        # Kernel + bootstrap + reality summary (from share/)
        (SHARE / "handoff" / "PM_KERNEL.json", PM_BOOT / "PM_KERNEL.json"),
        (SHARE / "PM_BOOTSTRAP_STATE.json", PM_BOOT / "PM_BOOTSTRAP_STATE.json"),
        (SHARE / "REALITY_GREEN_SUMMARY.json", PM_BOOT / "REALITY_GREEN_SUMMARY.json"),
        (SHARE / "HANDOFF_KERNEL.json", PM_BOOT / "HANDOFF_KERNEL.json"),
        # Planning context (if present)
        (SHARE / "planning_context.json", PM_BOOT / "planning_context.json"),
        # Phase index surfaces (from SSOT docs)
        (ROOT / "docs" / "SSOT" / "PHASE24_INDEX.md", PM_BOOT / "PHASE24_INDEX.md"),
        (ROOT / "docs" / "SSOT" / "PHASE25_INDEX.md", PM_BOOT / "PHASE25_INDEX.md"),
        (ROOT / "docs" / "SSOT" / "PHASE26_INDEX.md", PM_BOOT / "PHASE26_INDEX.md"),
        (ROOT / "docs" / "SSOT" / "PHASE27_INDEX.md", PM_BOOT / "PHASE27_INDEX.md"),
        # Share/ layout & analysis
        (ROOT / "docs" / "SSOT" / "SHARE_FOLDER_ANALYSIS.md", PM_BOOT / "SHARE_FOLDER_ANALYSIS.md"),
        # Directory namespace cleanup (Phase 27.I)
        (
            ROOT / "docs" / "SSOT" / "DIRECTORY_DUPLICATION_MAP.md",
            PM_BOOT / "DIRECTORY_DUPLICATION_MAP.md",
        ),
        (
            ROOT / "docs" / "SSOT" / "PHASE27I_DIRECTORY_UNIFICATION_PLAN.md",
            PM_BOOT / "PHASE27I_DIRECTORY_UNIFICATION_PLAN.md",
        ),
        # Governance contracts
        (ROOT / "docs" / "SSOT" / "EXECUTION_CONTRACT.md", PM_BOOT / "EXECUTION_CONTRACT.md"),
        (
            ROOT / "docs" / "SSOT" / "GITHUB_WORKFLOW_CONTRACT.md",
            PM_BOOT / "GITHUB_WORKFLOW_CONTRACT.md",
        ),
        (ROOT / "docs" / "SSOT" / "ORCHESTRATOR_REALITY.md", PM_BOOT / "ORCHESTRATOR_REALITY.md"),
        # Agent framework map
        (ROOT / "AGENTS.md", PM_BOOT / "AGENTS.md"),
    ]

    for src, dst in candidates:
        copy_if_exists(src, dst)

    # Behavioral contracts (PM/OPS/Cursor interaction rules)
    behavior_exports = [
        # PM contracts and behavior
        (ROOT / "docs" / "SSOT" / "PM_CONTRACT.md", PM_BOOT / "PM_CONTRACT.md"),
        (
            ROOT / "docs" / "SSOT" / "PM_AND_OPS_BEHAVIOR_CONTRACT.md",
            PM_BOOT / "PM_AND_OPS_BEHAVIOR_CONTRACT.md",
        ),
        (ROOT / "docs" / "SSOT" / "PM_BOOT_CONTRACT.md", PM_BOOT / "PM_BOOT_CONTRACT.md"),
        (
            ROOT / "docs" / "SSOT" / "PM_CONTRACT_STRICT_SSOT_DMS.md",
            PM_BOOT / "PM_CONTRACT_STRICT_SSOT_DMS.md",
        ),
        (ROOT / "docs" / "SSOT" / "PM_BEHAVIOR_CONTRACT.md", PM_BOOT / "PM_BEHAVIOR_CONTRACT.md"),
        (
            ROOT / "docs" / "SSOT" / "PM_STATE_PACKAGE_SPEC.md",
            PM_BOOT / "PM_STATE_PACKAGE_SPEC.md",
        ),
        # Cursor workflow
        (
            ROOT / "docs" / "SSOT" / "CURSOR_WORKFLOW_CONTRACT.md",
            PM_BOOT / "CURSOR_WORKFLOW_CONTRACT.md",
        ),
        (
            ROOT / "docs" / "SSOT" / "CURSOR_WORKFLOW_CONTRACT_INSTALLED.md",
            PM_BOOT / "CURSOR_WORKFLOW_CONTRACT_INSTALLED.md",
        ),
        # OPS boot spec (optional, but useful)
        (ROOT / "docs" / "SSOT" / "PHASE26_OPS_BOOT_SPEC.md", PM_BOOT / "PHASE26_OPS_BOOT_SPEC.md"),
        # OPS rules 050/051/052
        (ROOT / ".cursor" / "rules" / "050-ops-contract.mdc", PM_BOOT / "050-ops-contract.mdc"),
        (ROOT / ".cursor" / "rules" / "051-cursor-insight.mdc", PM_BOOT / "051-cursor-insight.mdc"),
        (ROOT / ".cursor" / "rules" / "052-tool-priority.mdc", PM_BOOT / "052-tool-priority.mdc"),
    ]

    for src, dst in behavior_exports:
        copy_if_exists(src, dst)

    print("[DONE] pm_boot surface seeded (see [WARN] lines for any missing sources).")


if __name__ == "__main__":
    main()
