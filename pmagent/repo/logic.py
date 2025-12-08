from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, List, Set, Tuple

EVIDENCE_DIR = Path("evidence/repo")
SHARE_EXPORT_DIR = Path("share/exports/repo")

EXCLUDED_DIR_PARTS: Set[str] = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    ".idea",
    ".vscode",
    "dist",
    "build",
    ".coverage",
}


@dataclass
class SemanticInventorySummary:
    total_repo_files: int
    dms_tracked_files: int
    layer4_tracked_files: int  # reserved for future use; 0 for now
    core_files_count: int
    untracked_files_count_raw: int
    untracked_source_files_count_filtered: int
    ignored_files_count: int


def _walk_repo_files(base: Path = Path(".")) -> Tuple[List[str], int]:
    """
    Return a list of relative file paths (POSIX-style) that are considered
    "source-ish" plus a count of how many files were ignored because they
    live under excluded dirs.

    This is intentionally conservative and read-only.
    """
    paths: List[str] = []
    ignored = 0
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        # any excluded dir in the path?
        if any(part in EXCLUDED_DIR_PARTS for part in p.parts):
            ignored += 1
            continue
        rel = p.relative_to(base).as_posix()
        paths.append(rel)
    return paths, ignored


def _load_dms_tracked_paths() -> Set[str]:
    """
    Load pmagent control-plane DMS-tracked repo paths from the KB registry (built from pmagent control-plane DMS).

    Primary source of truth:
      - share/kb_registry.json (JSON export from pmagent control-plane DMS)

    Legacy compatibility:
      - If kb_registry.json is missing but doc_registry.md exists, fall back
        to parsing the markdown table.

    Markdown is treated as a *derived view* only, for humans/OA sharing.
    JSON is the SSOT for machine consumption.
    """
    import json

    kb_json_path = Path("share/kb_registry.json")
    md_path = Path("share/doc_registry.md")
    tracked: Set[str] = set()

    # Primary: Use kb_registry.json if available
    if kb_json_path.exists():
        data = json.loads(kb_json_path.read_text(encoding="utf-8"))

        # Handle both {"documents": [...]} and raw list formats
        if isinstance(data, dict) and "documents" in data:
            docs = data["documents"]
        elif isinstance(data, list):
            docs = data
        else:
            raise RuntimeError(
                f"Unrecognized kb_registry.json structure: expected dict with 'documents' key or list, got {type(data)}"
            )

        for doc in docs:
            # Only track enabled documents with a repo_path
            if not doc.get("enabled", False):
                continue
            repo_path = doc.get("repo_path") or doc.get("path")
            if repo_path:
                tracked.add(repo_path)

        return tracked

    # Legacy fallback: doc_registry.md (for backward compatibility)
    if md_path.exists():
        lines = md_path.read_text(encoding="utf-8").splitlines()
        header: List[str] | None = None
        repo_idx: int | None = None

        for line in lines:
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]

            # header row detection
            if header is None and any(c.lower() == "repo_path" for c in cells):
                header = cells
                try:
                    repo_idx = [c.lower() for c in cells].index("repo_path")
                except ValueError as exc:
                    raise RuntimeError("Could not find 'repo_path' column in share/doc_registry.md header") from exc
                continue

            if header is None or repo_idx is None:
                continue

            # skip separator rows like | --- | --- |
            if all(set(c) <= {"-", ":"} for c in cells):
                continue

            if len(cells) <= repo_idx:
                continue
            repo_path = cells[repo_idx]
            if repo_path:
                tracked.add(repo_path)

        return tracked

    # Neither source available - this is now an error
    raise RuntimeError(
        f"Neither {kb_json_path} nor {md_path} could be used as a registry source. "
        "Run 'make share.sync' or housekeeping to generate the KB registry."
    )


def build_semantic_inventory() -> Dict:
    """
    Build the full semantic inventory structure:

    - summary counters
    - core_files (tracked by DMS & present in repo)
    - untracked_source_files (present in repo, not tracked by DMS)
    """
    repo_files, ignored_count = _walk_repo_files()
    repo_set = set(repo_files)

    dms_tracked = _load_dms_tracked_paths()
    core_files = sorted(repo_set & dms_tracked)
    untracked_source = sorted(repo_set - dms_tracked)

    summary = SemanticInventorySummary(
        total_repo_files=len(repo_files) + ignored_count,
        dms_tracked_files=len(dms_tracked),
        layer4_tracked_files=0,  # can be wired later to Layer-4-specific tables
        core_files_count=len(core_files),
        untracked_files_count_raw=len(untracked_source),
        untracked_source_files_count_filtered=len(untracked_source),
        ignored_files_count=ignored_count,
    )

    return {
        "summary": {
            "total_repo_files": summary.total_repo_files,
            "dms_tracked_files": summary.dms_tracked_files,
            "layer4_tracked_files": summary.layer4_tracked_files,
            "core_files_count": summary.core_files_count,
            "untracked_files_count_raw": summary.untracked_files_count_raw,
            "untracked_source_files_count_filtered": summary.untracked_source_files_count_filtered,
            "ignored_files_count": summary.ignored_files_count,
        },
        "core_files": core_files,
        "untracked_source_files": untracked_source,
        "ignored_files_count": summary.ignored_files_count,
    }


def _by_top_level_dir(untracked_source_files: List[str]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for path in untracked_source_files:
        top = path.split("/", 1)[0]
        counts[top] = counts.get(top, 0) + 1
    return counts


# ============================================================================
# Git Branch Management (Workflow Automation)
# ============================================================================


def _run_git(args: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run git command and return result."""
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=check,
    )


def create_branch(branch_name: str, base: str = "main") -> Dict[str, any]:
    """
    Create new branch from fresh main (or specified base).

    Automatically:
    1. Fetches latest from origin
    2. Checks out base branch
    3. Pulls latest
    4. Creates new branch

    Returns status dict with success/error info.
    """
    result = {"success": False, "branch": branch_name, "base": base, "messages": []}

    try:
        # Fetch latest
        result["messages"].append("Fetching latest from origin...")
        _run_git(["fetch", "origin"])

        # Checkout base
        result["messages"].append(f"Checking out {base}...")
        _run_git(["checkout", base])

        # Pull latest
        result["messages"].append(f"Pulling latest {base}...")
        _run_git(["pull", "origin", base])

        # Create and checkout new branch
        result["messages"].append(f"Creating branch {branch_name}...")
        _run_git(["checkout", "-b", branch_name])

        result["success"] = True
        result["messages"].append(f"✅ Branch {branch_name} created from latest {base}")

    except subprocess.CalledProcessError as e:
        result["error"] = e.stderr
        result["messages"].append(f"❌ Failed: {e.stderr}")

    return result


def update_branch_from_main(strategy: str = "merge") -> Dict[str, any]:
    """
    Update current branch with latest main.

    Args:
        strategy: "merge" or "rebase"

    Returns status dict.
    """
    result = {"success": False, "strategy": strategy, "messages": []}

    try:
        # Get current branch
        current = _run_git(["branch", "--show-current"]).stdout.strip()
        if not current:
            result["error"] = "Not on a branch (detached HEAD)"
            return result

        if current == "main":
            result["error"] = "Already on main - nothing to update"
            return result

        result["branch"] = current

        # Fetch latest
        result["messages"].append("Fetching latest from origin...")
        _run_git(["fetch", "origin"])

        # Update main
        result["messages"].append("Updating local main...")
        _run_git(["checkout", "main"])
        _run_git(["pull", "origin", "main"])

        # Back to feature branch
        _run_git(["checkout", current])

        # Merge or rebase
        if strategy == "merge":
            result["messages"].append(f"Merging main into {current}...")
            _run_git(["merge", "main"])
        else:
            result["messages"].append(f"Rebasing {current} onto main...")
            _run_git(["rebase", "main"])

        result["success"] = True
        result["messages"].append(f"✅ Branch {current} updated from main via {strategy}")

    except subprocess.CalledProcessError as e:
        result["error"] = e.stderr
        result["messages"].append(f"❌ Failed: {e.stderr}")

    return result


def safe_merge_to_main(force: bool = False) -> Dict[str, any]:
    """
    Safely merge current branch to main with guard checks.

    Args:
        force: Skip guard checks (dangerous!)

    Returns status dict.
    """
    result = {"success": False, "messages": [], "guard_checks": {}}

    try:
        # Get current branch
        current = _run_git(["branch", "--show-current"]).stdout.strip()
        if not current:
            result["error"] = "Not on a branch (detached HEAD)"
            return result

        if current == "main":
            result["error"] = "Already on main - nothing to merge"
            return result

        result["branch"] = current

        # Run guard checks (unless forced)
        if not force:
            result["messages"].append("Running merge guard checks...")
            guard_result = _run_git(["diff", "--shortstat", "main...HEAD"], check=False)

            if guard_result.stdout:
                stats = guard_result.stdout.strip()
                result["guard_checks"]["stats"] = stats

                # Parse insertions/deletions

                insertions = int(re.search(r"(\d+) insertion", stats).group(1)) if "insertion" in stats else 0
                deletions = int(re.search(r"(\d+) deletion", stats).group(1)) if "deletion" in stats else 0

                result["guard_checks"]["insertions"] = insertions
                result["guard_checks"]["deletions"] = deletions

                # Check for destructive merge
                if deletions > insertions:
                    net = deletions - insertions
                    result["error"] = f"BLOCKED: Would delete {net} net lines (potential destructive merge)"
                    result["messages"].append("❌ Merge blocked - use force=True to override")
                    result["guard_checks"]["blocked"] = True
                    return result

        # Update main first
        result["messages"].append("Updating main...")
        _run_git(["checkout", "main"])
        _run_git(["pull", "origin", "main"])

        # Merge feature branch
        result["messages"].append(f"Merging {current} into main...")
        _run_git(["merge", current, "--no-ff", "-m", f"feat: merge {current}"])

        # Push to origin
        result["messages"].append("Pushing to origin/main...")
        _run_git(["push", "origin", "main"])

        result["success"] = True
        result["messages"].append(f"✅ Successfully merged {current} to main")
        result["messages"].append("💡 Run 'pmagent repo branch-cleanup' to delete merged branch")

    except subprocess.CalledProcessError as e:
        result["error"] = e.stderr
        result["messages"].append(f"❌ Failed: {e.stderr}")

    return result


def cleanup_merged_branches(dry_run: bool = True, force: bool = False) -> Dict[str, any]:
    """
    Delete branches that have been merged to main.

    Args:
        dry_run: If True, only show what would be deleted
        force: If True, use -D instead of -d (force delete)

    Returns status dict with deleted branches.
    """
    result = {
        "success": False,
        "dry_run": dry_run,
        "deleted_local": [],
        "deleted_remote": [],
        "failed": [],
        "messages": [],
    }

    try:
        # Get current branch to avoid deleting it
        current_branch = _run_git(["branch", "--show-current"]).stdout.strip()

        # Get LOCAL merged branches
        merged_result = _run_git(["branch", "--merged", "main"])
        local_branches = [
            b.strip().replace("* ", "")
            for b in merged_result.stdout.split("\n")
            if b.strip() and b.strip() != "main" and b.strip() != current_branch and not b.strip().startswith("origin/")
        ]

        # Get REMOTE merged branches
        remote_merged_result = _run_git(["branch", "-r", "--merged", "main"])
        remote_branches = [
            b.strip().replace("origin/", "")
            for b in remote_merged_result.stdout.split("\n")
            if b.strip() and "origin/" in b and "HEAD" not in b and "main" not in b
        ]

        result["local_branches"] = local_branches
        result["remote_branches"] = remote_branches

        if not local_branches and not remote_branches:
            result["messages"].append("No merged branches to clean up")
            result["success"] = True
            return result

        if dry_run:
            if local_branches:
                result["messages"].append(f"Would delete {len(local_branches)} local merged branches:")
                for b in local_branches[:10]:  # Show first 10
                    result["messages"].append(f"  - {b}")
                if len(local_branches) > 10:
                    result["messages"].append(f"  ... and {len(local_branches) - 10} more")

            if remote_branches:
                result["messages"].append(f"\nWould delete {len(remote_branches)} remote merged branches:")
                for b in remote_branches[:10]:  # Show first 10
                    result["messages"].append(f"  - origin/{b}")
                if len(remote_branches) > 10:
                    result["messages"].append(f"  ... and {len(remote_branches) - 10} more")

            result["messages"].append("\nRun with --execute to actually delete")
        else:
            # Delete local branches
            if local_branches:
                result["messages"].append(f"Deleting {len(local_branches)} local branches...")
                delete_flag = "-D" if force else "-d"

                for b in local_branches:
                    try:
                        _run_git(["branch", delete_flag, b])
                        result["deleted_local"].append(b)
                        result["messages"].append(f"  ✓ Deleted {b}")
                    except subprocess.CalledProcessError as e:
                        result["failed"].append({"branch": b, "error": str(e.stderr)})
                        if "not fully merged" in e.stderr:
                            result["messages"].append(f"  ⚠ {b} not fully merged (use --force to delete anyway)")
                        else:
                            result["messages"].append(f"  ✗ Failed to delete {b}")

            # Delete remote branches
            if remote_branches:
                result["messages"].append(f"\nDeleting {len(remote_branches)} remote branches from origin...")

                for b in remote_branches:
                    try:
                        _run_git(["push", "origin", "--delete", b])
                        result["deleted_remote"].append(b)
                        result["messages"].append(f"  ✓ Deleted origin/{b}")
                    except subprocess.CalledProcessError as e:
                        error_msg = e.stderr.lower() if e.stderr else ""
                        if "unable to delete" in error_msg or "does not exist" in error_msg:
                            result["messages"].append(f"  ⚠ origin/{b} already deleted")
                        else:
                            result["failed"].append({"branch": f"origin/{b}", "error": str(e.stderr)})
                            result["messages"].append(f"  ✗ Failed to delete origin/{b}")

        result["success"] = True
        result["summary"] = {
            "local_deleted": len(result["deleted_local"]),
            "remote_deleted": len(result["deleted_remote"]),
            "failed": len(result["failed"]),
            "total_cleaned": len(result["deleted_local"]) + len(result["deleted_remote"]),
        }

    except subprocess.CalledProcessError as e:
        result["error"] = e.stderr
        result["messages"].append(f"❌ Failed: {e.stderr}")

    return result


def get_branch_status() -> Dict[str, any]:
    """
    Get status of current branch vs main.

    Returns:
        - Current branch name
        - Commits ahead of main
        - Commits behind main
        - Last commit date
        - Branch age in days
    """
    result = {"success": False, "messages": []}

    try:
        # Current branch
        current = _run_git(["branch", "--show-current"]).stdout.strip()
        if not current:
            result["error"] = "Not on a branch (detached HEAD)"
            return result

        result["branch"] = current

        if current == "main":
            result["messages"].append("On main branch")
            result["success"] = True
            return result

        # Commits ahead/behind
        ahead_behind = _run_git(["rev-list", "--left-right", "--count", "main...HEAD"]).stdout.strip().split()

        result["behind_main"] = int(ahead_behind[0])
        result["ahead_of_main"] = int(ahead_behind[1])

        # Last commit info
        last_commit = _run_git(["log", "-1", "--format=%H|%ci|%s"]).stdout.strip().split("|")

        result["last_commit"] = {
            "sha": last_commit[0][:8],
            "date": last_commit[1],
            "message": last_commit[2],
        }

        # Calculate age
        commit_date = datetime.fromisoformat(last_commit[1].replace(" +", "+").replace(" -", "-"))
        age_days = (datetime.now(UTC) - commit_date).days
        result["age_days"] = age_days

        # Status message
        result["messages"].append(f"Branch: {current}")
        result["messages"].append(f"Ahead of main: {result['ahead_of_main']} commits")
        result["messages"].append(f"Behind main: {result['behind_main']} commits")
        result["messages"].append(f"Age: {age_days} days")
        result["messages"].append(f"Last commit: {last_commit[2]}")

        # Warnings
        if result["behind_main"] > 10:
            result["messages"].append("⚠️  Branch is significantly behind main - consider updating")

        if age_days > 14:
            result["messages"].append("⚠️  Branch is older than 2 weeks - consider merging or closing")

        result["success"] = True

    except subprocess.CalledProcessError as e:
        result["error"] = e.stderr
        result["messages"].append(f"❌ Failed: {e.stderr}")

    return result


def run_semantic_inventory(write_share: bool = False) -> None:
    """
    Generate:
      - evidence/repo/repo_semantic_inventory.json
      - evidence/repo/semantic_inventory_filtered.json

    Optionally:
      - share/exports/repo/semantic_inventory.json
    """
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    SHARE_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    inventory = build_semantic_inventory()
    untracked = inventory.get("untracked_source_files", [])
    by_dir = _by_top_level_dir(untracked)

    filtered = {
        "summary": inventory["summary"],
        "by_top_level_dir": by_dir,
    }

    # Evidence files
    (EVIDENCE_DIR / "repo_semantic_inventory.json").write_text(
        json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8"
    )
    (EVIDENCE_DIR / "semantic_inventory_filtered.json").write_text(
        json.dumps(filtered, indent=2, sort_keys=True), encoding="utf-8"
    )

    if write_share:
        (SHARE_EXPORT_DIR / "semantic_inventory.json").write_text(
            json.dumps(filtered, indent=2, sort_keys=True), encoding="utf-8"
        )


def build_reunion_plan(
    filtered_inventory: Dict,
    integration_dirs: Set[str] | None = None,
    quarantine_dirs: Set[str] | None = None,
) -> Dict:
    """
    Build the reunion plan based on the filtered semantic inventory and
    policy-driven directory labels.
    """
    if integration_dirs is None:
        integration_dirs = {"webui", "ui", "genai-toolbox"}
    if quarantine_dirs is None:
        quarantine_dirs = {"archive", "logs"}

    summary = filtered_inventory.get("summary", {})
    # For file-level labeling we need untracked_source_files from the full inventory.
    # Reload from evidence if needed.
    full_inventory_path = EVIDENCE_DIR / "repo_semantic_inventory.json"
    if not full_inventory_path.exists():
        raise RuntimeError("repo_semantic_inventory.json missing; run semantic-inventory first.")
    full_inventory = json.loads(full_inventory_path.read_text(encoding="utf-8"))
    untracked_files: List[str] = full_inventory.get("untracked_source_files", [])

    dir_labels: Dict[str, Dict[str, object]] = {}
    files_bucket: Dict[str, List[str]] = {
        "integration_candidates": [],
        "quarantine_candidates": [],
        "external": [],
        "investigate": [],
    }

    for path in untracked_files:
        top = path.split("/", 1)[0]
        if top in integration_dirs:
            label = "integration_candidate"
            bucket = "integration_candidates"
        elif top in quarantine_dirs:
            label = "quarantine_candidate"
            bucket = "quarantine_candidates"
        else:
            # For now, treat everything else as "investigate" to avoid
            # accidentally discarding important code.
            label = "investigate"
            bucket = "investigate"

        files_bucket[bucket].append(path)
        if top not in dir_labels:
            dir_labels[top] = {
                "label": label,
                "untracked_source_count": 0,
            }
        dir_labels[top]["untracked_source_count"] = dir_labels[top]["untracked_source_count"] + 1

    plan = {
        "summary": summary,
        "dir_labels": dir_labels,
        "files": files_bucket,
        "notes": [
            "integration_dirs: " + ", ".join(sorted(integration_dirs)),
            "quarantine_dirs: " + ", ".join(sorted(quarantine_dirs)),
        ],
    }
    return plan


def run_reunion_plan(write_share: bool = False) -> None:
    """
    Generate:
      - evidence/repo/repo_reunion_plan.json
    Optionally:
      - share/exports/repo/reunion_plan.json
    """
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    SHARE_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    filtered_path = EVIDENCE_DIR / "semantic_inventory_filtered.json"
    if not filtered_path.exists():
        # compute semantic inventory first if missing
        run_semantic_inventory(write_share=False)
        filtered_path = EVIDENCE_DIR / "semantic_inventory_filtered.json"

    filtered = json.loads(filtered_path.read_text(encoding="utf-8"))
    plan = build_reunion_plan(filtered_inventory=filtered)

    (EVIDENCE_DIR / "repo_reunion_plan.json").write_text(json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8")

    if write_share:
        (SHARE_EXPORT_DIR / "reunion_plan.json").write_text(
            json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8"
        )


def run_quarantine_candidates(write_share: bool = False) -> None:
    """
    Generate:
      - evidence/repo/repo_quarantine_candidates.json
    Optionally:
      - share/exports/repo/quarantine_candidates.json
    """
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    SHARE_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    plan_path = EVIDENCE_DIR / "repo_reunion_plan.json"
    if not plan_path.exists():
        # compute reunion plan first if missing
        run_reunion_plan(write_share=False)
        plan_path = EVIDENCE_DIR / "repo_reunion_plan.json"

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    quarantine_files: List[str] = plan.get("files", {}).get("quarantine_candidates", [])

    payload = {"quarantine_candidates": quarantine_files}

    (EVIDENCE_DIR / "repo_quarantine_candidates.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
    )

    if write_share:
        (SHARE_EXPORT_DIR / "quarantine_candidates.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
        )


def check_branch_protection(protected_branches: List[str] | None = None, allow_release: bool = False) -> Dict[str, any]:
    """
    Check if the current branch is protected (e.g. main) and should be blocked
    from direct commits/work.

    Args:
        protected_branches: List of branch names to protect. Default: ["main"]
        allow_release: If True, allow work on protected branches (e.g. for release tags)

    Returns:
        Status dict. If success=False, the action should be blocked.
    """
    if protected_branches is None:
        protected_branches = ["main"]

    result = {"success": False, "messages": []}

    try:
        # Get current branch
        current = _run_git(["branch", "--show-current"]).stdout.strip()
        if not current:
            result["error"] = "Not on a branch (detached HEAD)"
            return result

        result["branch"] = current

        if current in protected_branches:
            if allow_release:
                result["success"] = True
                result["messages"].append(f"⚠️  Running on protected branch '{current}' (allow_release=True)")
            else:
                result["success"] = False
                result["error"] = f"BLOCKED: Direct work on protected branch '{current}' is forbidden."
                result["messages"].append(f"❌ You are on '{current}'.")
                result["messages"].append("💡 Please create a feature branch: pmagent repo branch-create <name>")
        else:
            result["success"] = True
            result["messages"].append(f"✅ Branch '{current}' is safe for work")

    except subprocess.CalledProcessError as e:
        result["error"] = e.stderr
        result["messages"].append(f"❌ Failed: {e.stderr}")

    return result
