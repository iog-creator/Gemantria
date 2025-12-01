import json
from pathlib import Path

import pytest

from pmagent.repo.logic import (
    run_semantic_inventory,
    run_reunion_plan,
    run_quarantine_candidates,
)

DOC_REGISTRY_MD = Path("share/doc_registry.md")
EVIDENCE_DIR = Path("evidence/repo")


@pytest.mark.skipif(
    not DOC_REGISTRY_MD.exists(),
    reason="share/doc_registry.md missing; run housekeeping/DMS export first.",
)
def test_tv_repo_01_semantic_inventory_generates_evidence(tmp_path=None) -> None:
    """
    TV-REPO-01: Semantic inventory on current repo.

    Expectation:
    - repo_semantic_inventory.json exists
    - semantic_inventory_filtered.json exists
    - summary + untracked_source_files keys present
    """
    # Run semantic inventory (idempotent)
    run_semantic_inventory(write_share=False)

    inventory_path = EVIDENCE_DIR / "repo_semantic_inventory.json"
    filtered_path = EVIDENCE_DIR / "semantic_inventory_filtered.json"

    assert inventory_path.exists()
    assert filtered_path.exists()

    data = json.loads(inventory_path.read_text(encoding="utf-8"))
    assert "summary" in data
    assert "untracked_source_files" in data


@pytest.mark.skipif(
    not DOC_REGISTRY_MD.exists(),
    reason="share/doc_registry.md missing; run housekeeping/DMS export first.",
)
def test_tv_repo_02_reunion_plan_generates_plan() -> None:
    """
    TV-REPO-02: Reunion plan builds on semantic inventory.

    Expectation:
    - repo_reunion_plan.json exists
    - dir_labels and files keys present
    """
    # Ensure semantic inventory exists
    run_semantic_inventory(write_share=False)

    # Run reunion plan
    run_reunion_plan(write_share=False)

    plan_path = EVIDENCE_DIR / "repo_reunion_plan.json"
    assert plan_path.exists()

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    assert "summary" in plan
    assert "dir_labels" in plan
    assert "files" in plan
    assert set(plan["files"].keys()) >= {
        "integration_candidates",
        "quarantine_candidates",
        "investigate",
    }


@pytest.mark.skipif(
    not DOC_REGISTRY_MD.exists(),
    reason="share/doc_registry.md missing; run housekeeping/DMS export first.",
)
def test_tv_repo_03_quarantine_candidates_generates_list() -> None:
    """
    TV-REPO-03: Quarantine candidates extracted from reunion plan.

    Expectation:
    - repo_quarantine_candidates.json exists
    - 'quarantine_candidates' is a list
    """
    # Ensure reunion plan exists (and thus semantic inventory)
    run_reunion_plan(write_share=False)

    # Run quarantine-candidates
    run_quarantine_candidates(write_share=False)

    qc_path = EVIDENCE_DIR / "repo_quarantine_candidates.json"
    assert qc_path.exists()

    payload = json.loads(qc_path.read_text(encoding="utf-8"))
    assert "quarantine_candidates" in payload
    assert isinstance(payload["quarantine_candidates"], list)
