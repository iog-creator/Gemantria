from __future__ import annotations

import json
from dataclasses import dataclass
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
    Load DMS-tracked repo paths from share/doc_registry.md, which is the
    Markdown export of control.doc_registry.

    Assumes there is a 'repo_path' column in the header row.
    If the file is missing or malformed, this will raise.
    """
    md_path = Path("share/doc_registry.md")
    if not md_path.exists():
        raise RuntimeError("share/doc_registry.md not found; run housekeeping / DMS export first.")

    lines = md_path.read_text(encoding="utf-8").splitlines()
    header: List[str] | None = None
    repo_idx: int | None = None
    tracked: Set[str] = set()

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
            # not reached header yet
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
