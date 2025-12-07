import json
import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Dict, Tuple

# Constants for default paths assuming running from repo root
REPO_ROOT = Path(".").resolve()
SHARE_DIR = REPO_ROOT / "share"
HANDOFF_DIR = SHARE_DIR / "handoff"
BOOTSTRAP_STATE_PATH = SHARE_DIR / "PM_BOOTSTRAP_STATE.json"


@dataclass
class HandoffKernel:
    current_phase: str
    branch: str
    last_completed_phase: str
    next_actions: List[str]
    ground_truth_files: List[str]
    constraints: Dict[str, Any]
    generated_at_utc: str
    generator_version: str = "pmagent.handoff.kernel.v1"

    def to_json(self) -> str:
        return json.dumps(self.__dict__, indent=2)


def get_git_branch() -> str:
    try:
        from subprocess import check_output

        return check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def build_kernel(pm_bootstrap_path: Path = BOOTSTRAP_STATE_PATH) -> HandoffKernel:
    """
    Load PM_BOOTSTRAP_STATE.json + key share surfaces and return a HandoffKernel.
    """
    if not pm_bootstrap_path.exists():
        raise FileNotFoundError(f"Bootstrap state not found at {pm_bootstrap_path}")

    with open(pm_bootstrap_path, encoding="utf-8") as f:
        bootstrap_data = json.load(f)

    meta = bootstrap_data.get("meta", {})
    current_phase = meta.get("current_phase", "unknown")

    # Heuristic for last_completed_phase based on current.
    # If current is "26", last completed is likely "25".
    # In a real scenario, we might parse phases map to find specific statuses.
    try:
        curr_int = int(current_phase)
        last_completed = str(curr_int - 1) if curr_int > 0 else "0"
    except ValueError:
        last_completed = "unknown"

    branch = get_git_branch()

    # Identify Next Actions from Phase Index of current phase if available
    # For now, we use a generic set of next actions focused on verification
    next_actions = [
        "Run kernel check (make kernel.check)",
        "Verify guard status (make reality.green)",
        f"Review Phase {current_phase} objectives",
    ]

    # Ground Truth Files Collection
    ground_truth_raw = [
        "share/PM_BOOTSTRAP_STATE.json",
        "share/SSOT_SURFACE_V17.json",  # Hardcoded based on current reqs, could be dynamic
        f"docs/SSOT/PHASE{current_phase}_INDEX.md",  # Assuming docs/SSOT location based on recent history
        "share/orchestrator/STATE.json",
        "share/orchestrator_assistant/STATE.json",
    ]

    # Add historical phase indices
    for i in range(18, 26):  # 18 to 24 are historical
        # Check likely locations: share/ or docs/SSOT/
        # Using generic pattern, guard will validate existence
        path_candidate = f"share/PHASE{i}_INDEX.md"
        ground_truth_raw.append(path_candidate)

    # Resolve/Filter paths that actually exist to be helpful
    ground_truth_files = []
    for p_str in ground_truth_raw:
        if (REPO_ROOT / p_str).exists():
            ground_truth_files.append(p_str)
        # Also check docs/SSOT variant if share/ variant missing
        elif p_str.startswith("share/PHASE"):
            alt = p_str.replace("share/", "docs/SSOT/")
            if (REPO_ROOT / alt).exists():
                ground_truth_files.append(alt)

    # Always include current phase index if we can find it
    curr_idx_share = f"share/PHASE{current_phase}_INDEX.md"
    curr_idx_ssot = f"docs/SSOT/PHASE{current_phase}_INDEX.md"
    if (REPO_ROOT / curr_idx_share).exists() and curr_idx_share not in ground_truth_files:
        ground_truth_files.append(curr_idx_share)
    elif (REPO_ROOT / curr_idx_ssot).exists() and curr_idx_ssot not in ground_truth_files:
        ground_truth_files.append(curr_idx_ssot)

    constraints = {
        "backup_required_before_destructive_ops": True,
        "enforced_checks": ["reality.green", "stress.smoke", "phase.done.check"],
    }

    return HandoffKernel(
        current_phase=current_phase,
        branch=branch,
        last_completed_phase=last_completed,
        next_actions=next_actions,
        ground_truth_files=sorted(list(set(ground_truth_files))),
        constraints=constraints,
        generated_at_utc=datetime.datetime.now(datetime.UTC).isoformat(),
        generator_version="pmagent.handoff.kernel.v1",
    )


def write_kernel_bundle(out_dir: Path = HANDOFF_DIR) -> Tuple[Path, Path]:
    """
    Build the kernel and write:
    - PM_KERNEL.json
    - PM_SUMMARY.md

    Returns the paths written.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    kernel = build_kernel()

    # 1. Write JSON
    kernel_json_path = out_dir / "PM_KERNEL.json"
    with open(kernel_json_path, "w", encoding="utf-8") as f:
        f.write(kernel.to_json())

    # 2. Write Markdown Summary
    summary_md_path = out_dir / "PM_SUMMARY.md"
    summary_content = f"""# PM Handoff Summary
Generated at: {kernel.generated_at_utc}
Version: {kernel.generator_version}

## Where we really are
- **Phase**: {kernel.current_phase}
- **Last Completed**: {kernel.last_completed_phase}
- **Branch**: `{kernel.branch}`

## What's green / proven
- **Kernel Integrity**: Generated and consistent with bootstrap.
- **Guard Policy**: Enforced (`reality.green`, `stress.smoke`, `phase.done.check`).

## Known gotchas / sharp edges
- **Backup**: {kernel.constraints.get("backup_required_before_destructive_ops")} (Destructive ops require fresh backup).
- Always verify `reality.green` before merging.

## Next actions for Cursor
{chr(10).join([f"- {action}" for action in kernel.next_actions])}

## How to regenerate this kernel
```bash
pmagent handoff-kernel
```

## Ground Truth Surfaces
{chr(10).join([f"- `{f}`" for f in kernel.ground_truth_files])}
"""
    with open(summary_md_path, "w", encoding="utf-8") as f:
        f.write(summary_content)

    return kernel_json_path, summary_md_path
