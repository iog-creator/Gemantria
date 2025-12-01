import json
import subprocess
from pathlib import Path

import pytest


def _repo_root() -> Path:
    # tests/ -> repo root is parent
    return Path(__file__).resolve().parent.parent


def _run_pmagent(args: list[str]) -> subprocess.CompletedProcess[str]:
    """
    Run the pmagent CLI with the given args, from the repo root.

    If pmagent is not on PATH (e.g. unusual dev env), skip the test
    instead of hard failing.
    """
    repo_root = _repo_root()
    try:
        result = subprocess.run(
            ["pmagent", *args],
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        pytest.skip("pmagent CLI not found on PATH")
    return result


def _evidence_dir() -> Path:
    return _repo_root() / "evidence" / "repo"


def _remove_if_exists(path: Path) -> None:
    if path.exists():
        path.unlink()


@pytest.mark.tv("TV-REPO-01")
def test_semantic_inventory_generates_expected_evidence_files() -> None:
    """
    TV-REPO-01:
    pmagent repo semantic-inventory

    - exits successfully
    - writes repo_semantic_inventory.json
    - writes semantic_inventory_filtered.json
    - produces a JSON object with basic counters
    """
    evidence_dir = _evidence_dir()
    semantic_inventory_path = evidence_dir / "repo_semantic_inventory.json"
    filtered_path = evidence_dir / "semantic_inventory_filtered.json"

    # Clean up any old artifacts for a deterministic run
    _remove_if_exists(semantic_inventory_path)
    _remove_if_exists(filtered_path)

    result = _run_pmagent(["repo", "semantic-inventory"])
    assert (
        result.returncode == 0
    ), f"semantic-inventory failed: rc={result.returncode}, stdout={result.stdout}, stderr={result.stderr}"

    assert semantic_inventory_path.exists(), "repo_semantic_inventory.json not created"
    assert filtered_path.exists(), "semantic_inventory_filtered.json not created"

    # Basic shape validation on the main inventory JSON
    raw = semantic_inventory_path.read_text(encoding="utf-8")
    data = json.loads(raw)
    assert isinstance(data, dict), "semantic inventory should be a JSON object"

    # These keys were observed in manual smoke tests and act as basic sanity checks
    summary = data.get("summary", {})
    for key in [
        "total_repo_files",
        "ignored_files_count",
        "untracked_files_count_raw",
        "untracked_source_files_count_filtered",
    ]:
        assert key in summary, f"expected key {key!r} in semantic inventory summary"


@pytest.mark.tv("TV-REPO-02")
def test_reunion_plan_generates_reunion_and_inventory() -> None:
    """
    TV-REPO-02:
    pmagent repo reunion-plan

    - exits successfully
    - writes repo_reunion_plan.json
    - also ensures repo_semantic_inventory.json exists (auto-generated if missing)
    """
    evidence_dir = _evidence_dir()
    reunion_plan_path = evidence_dir / "repo_reunion_plan.json"
    semantic_inventory_path = evidence_dir / "repo_semantic_inventory.json"

    # Only remove reunion plan to test the command, not semantic inventory
    # (reunion-plan will auto-generate it if missing, demonstrating command chaining)
    _remove_if_exists(reunion_plan_path)

    result = _run_pmagent(["repo", "reunion-plan"])
    assert (
        result.returncode == 0
    ), f"reunion-plan failed: rc={result.returncode}, stdout={result.stdout}, stderr={result.stderr}"

    assert reunion_plan_path.exists(), "repo_reunion_plan.json not created"
    assert (
        semantic_inventory_path.exists()
    ), "reunion-plan did not produce repo_semantic_inventory.json as expected"

    # Sanity-check reunion plan JSON shape (dict or list, non-empty)
    raw = reunion_plan_path.read_text(encoding="utf-8")
    data = json.loads(raw)
    assert isinstance(data, (dict, list)), "reunion plan JSON must be dict or list"
    if isinstance(data, dict):
        assert data, "reunion plan dict should not be empty"
    else:
        assert len(data) >= 1, "reunion plan list should not be empty"


@pytest.mark.tv("TV-REPO-03")
def test_quarantine_candidates_json_non_empty() -> None:
    """
    TV-REPO-03:
    pmagent repo quarantine-candidates

    - exits successfully
    - writes repo_quarantine_candidates.json
    - produced JSON is non-empty (list or dict)
    """
    evidence_dir = _evidence_dir()
    quarantine_path = evidence_dir / "repo_quarantine_candidates.json"

    # Only clean the quarantine file itself, not the reunion plan it depends on
    _remove_if_exists(quarantine_path)

    result = _run_pmagent(["repo", "quarantine-candidates"])
    assert (
        result.returncode == 0
    ), f"quarantine-candidates failed: rc={result.returncode}, stdout={result.stdout}, stderr={result.stderr}"

    assert quarantine_path.exists(), "repo_quarantine_candidates.json not created"

    raw = quarantine_path.read_text(encoding="utf-8")
    data = json.loads(raw)

    # Accept either a list or dict here; just require it to be non-empty.
    assert isinstance(data, (list, dict)), "quarantine candidates JSON must be list or dict"
    if isinstance(data, dict):
        assert data, "quarantine candidates dict should not be empty"
    else:
        assert len(data) >= 1, "quarantine candidates list should not be empty"
