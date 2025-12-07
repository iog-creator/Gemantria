#!/usr/bin/env python3
# ruff: noqa: E402  # sys.path test pattern is intentional
"""
Tests for pmagent plan kb fix command (AgentPM-Next:M2)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from pmagent.kb.registry import KBDocument, KBDocumentRegistry, save_registry
from pmagent.plan.fix import build_fix_actions, apply_actions, FixAction, _is_approved_path
from pmagent.plan.kb import build_kb_doc_worklist


def test_build_fix_actions_missing_doc(tmp_path: Path) -> None:
    """Test that build_fix_actions creates create_stub_doc action for missing docs."""
    # Create a test registry with a missing doc
    registry = KBDocumentRegistry()

    doc = KBDocument(
        id="missing-1",
        title="Missing Document",
        path="docs/test_missing.md",
        type="ssot",
        owning_subsystem="docs",
    )

    registry.add_document(doc)

    # Save to temp path
    registry_path = tmp_path / "kb_registry.json"
    save_registry(registry, registry_path)

    # Build worklist
    worklist = build_kb_doc_worklist(registry_path=registry_path)

    # Build fix actions
    actions = build_fix_actions(worklist, registry_path=registry_path)

    # Verify action structure
    assert len(actions) > 0
    missing_actions = [a for a in actions if a.severity == "missing"]
    assert len(missing_actions) > 0

    action = missing_actions[0]
    assert action.action_type == "create_stub_doc"
    assert action.severity == "missing"
    assert action.doc_path == "docs/test_missing.md"
    assert action.subsystem == "docs"


def test_build_fix_actions_filters(tmp_path: Path) -> None:
    """Test that filters work correctly."""
    registry = KBDocumentRegistry()

    # Add docs from different subsystems
    doc1 = KBDocument(
        id="missing-1",
        title="Missing Doc 1",
        path="docs/test1.md",
        type="ssot",
        owning_subsystem="docs",
    )
    doc2 = KBDocument(
        id="missing-2",
        title="Missing Doc 2",
        path="pmagent/test2.md",
        type="agents_md",
        owning_subsystem="pmagent",
    )

    registry.add_document(doc1)
    registry.add_document(doc2)

    registry_path = tmp_path / "kb_registry.json"
    save_registry(registry, registry_path)

    worklist = build_kb_doc_worklist(registry_path=registry_path)

    # Filter by subsystem
    actions = build_fix_actions(worklist, filters={"subsystem": "docs"}, registry_path=registry_path)
    assert all(a.subsystem == "docs" for a in actions)

    # Filter by min_severity
    actions = build_fix_actions(worklist, filters={"min_severity": "missing"}, registry_path=registry_path)
    assert all(a.severity == "missing" for a in actions)

    # Filter by limit
    actions = build_fix_actions(worklist, filters={"limit": 1}, registry_path=registry_path)
    assert len(actions) <= 1


def test_apply_actions_dry_run(tmp_path: Path) -> None:
    """Test that dry-run mode doesn't create files."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    action = FixAction(
        id="test-1",
        subsystem="docs",
        severity="missing",
        action_type="create_stub_doc",
        description="Create test stub",
        doc_path="docs/test.md",
    )

    result = apply_actions([action], dry_run=True, repo_root=repo_root)

    # Should simulate but not create
    assert result["mode"] == "dry-run"
    assert result["actions_applied"] == 1
    assert "docs/test.md" in result["files_created"]

    # File should not exist
    assert not (repo_root / "docs" / "test.md").exists()


def test_apply_actions_create_stub(tmp_path: Path) -> None:
    """Test that apply mode creates stub files."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    action = FixAction(
        id="test-1",
        subsystem="docs",
        severity="missing",
        action_type="create_stub_doc",
        description="Create test stub",
        doc_path="docs/test.md",
    )

    result = apply_actions([action], dry_run=False, repo_root=repo_root)

    # Should create file
    assert result["mode"] == "apply"
    assert result["actions_applied"] == 1
    assert action.applied is True

    # File should exist
    doc_path = repo_root / "docs" / "test.md"
    assert doc_path.exists()

    # Content should be stub
    content = doc_path.read_text()
    assert "Stub" in content
    assert "TODO" in content


def test_apply_actions_mark_stale(tmp_path: Path) -> None:
    """Test that mark_stale_and_suggest_update appends note."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    # Create existing doc
    doc_path = repo_root / "docs" / "stale.md"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text("# Stale Document\n\nSome content here.\n")

    action = FixAction(
        id="stale-1",
        subsystem="docs",
        severity="stale",
        action_type="mark_stale_and_suggest_update",
        description="Mark stale",
        doc_path="docs/stale.md",
    )

    result = apply_actions([action], dry_run=False, repo_root=repo_root)

    # Should modify file
    assert result["mode"] == "apply"
    assert result["actions_applied"] == 1
    assert action.applied is True

    # File should have staleness note
    content = doc_path.read_text()
    assert "STALENESS NOTE" in content
    assert "Some content here" in content  # Original content preserved


def test_apply_actions_idempotent_stale(tmp_path: Path) -> None:
    """Test that marking stale twice doesn't double-append."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    doc_path = repo_root / "docs" / "stale.md"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text("# Stale Document\n\nSome content.\n")

    action = FixAction(
        id="stale-1",
        subsystem="docs",
        severity="stale",
        action_type="mark_stale_and_suggest_update",
        description="Mark stale",
        doc_path="docs/stale.md",
    )

    # Apply twice
    apply_actions([action], dry_run=False, repo_root=repo_root)
    content1 = doc_path.read_text()

    apply_actions([action], dry_run=False, repo_root=repo_root)
    content2 = doc_path.read_text()

    # Should have same number of staleness notes (one section = one opening comment)
    # Count opening comments only (not closing comments)
    count1 = content1.count("<!-- STALENESS NOTE")
    count2 = content2.count("<!-- STALENESS NOTE")
    assert count1 == count2
    assert count1 == 1


def test_apply_actions_approved_paths(tmp_path: Path) -> None:
    """Test that only approved paths are written."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    # Approved path
    action1 = FixAction(
        id="test-1",
        subsystem="docs",
        severity="missing",
        action_type="create_stub_doc",
        description="Create approved stub",
        doc_path="docs/test.md",
    )

    # Unapproved path
    action2 = FixAction(
        id="test-2",
        subsystem="scripts",
        severity="missing",
        action_type="create_stub_doc",
        description="Create unapproved stub",
        doc_path="scripts/test.py",
    )

    result = apply_actions([action1, action2], dry_run=False, repo_root=repo_root)

    # Approved should work
    assert result["actions_applied"] >= 1
    assert (repo_root / "docs" / "test.md").exists()

    # Unapproved should be skipped
    assert "scripts/test.py" not in result["files_created"]
    assert not (repo_root / "scripts" / "test.py").exists()
    # Check that action2 was skipped with appropriate note
    assert action2.notes
    assert any("not approved" in note.lower() or "approved" in note.lower() for note in action2.notes)


def test_is_approved_path() -> None:
    """Test approved path checking."""
    assert _is_approved_path("docs/test.md") is True
    assert _is_approved_path("AGENTS.md") is True
    assert _is_approved_path("pmagent/AGENTS.md") is True
    assert _is_approved_path("rules/docs/test.md") is True
    assert _is_approved_path("scripts/test.py") is False
    assert _is_approved_path("src/test.py") is False


def test_plan_kb_fix_cli_dry_run(tmp_path: Path) -> None:
    """Test CLI command in dry-run mode."""
    registry = KBDocumentRegistry()

    doc = KBDocument(
        id="missing-1",
        title="Missing Document",
        path="docs/test.md",
        type="ssot",
        owning_subsystem="docs",
    )

    registry.add_document(doc)
    registry_path = tmp_path / "kb_registry.json"
    save_registry(registry, registry_path)

    # Change to repo root for CLI
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    # Run CLI command (dry-run by default)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pmagent.cli",
            "plan",
            "kb",
            "fix",
            "--json-only",
        ],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env={**dict(os.environ), "KB_REGISTRY_PATH": str(registry_path)},
    )

    # Should succeed
    assert result.returncode == 0

    # Should output valid JSON
    output = result.stdout.strip()
    data = json.loads(output)

    # Verify shape
    assert "mode" in data
    assert data["mode"] == "dry-run"
    assert "actions" in data
    assert "summary" in data


def test_plan_kb_fix_cli_apply(tmp_path: Path) -> None:
    """Test CLI command in apply mode."""
    registry = KBDocumentRegistry()

    doc = KBDocument(
        id="missing-1",
        title="Missing Document",
        path="docs/test.md",
        type="ssot",
        owning_subsystem="docs",
    )

    registry.add_document(doc)
    registry_path = tmp_path / "kb_registry.json"
    save_registry(registry, registry_path)

    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    # Run CLI command with --apply
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pmagent.cli",
            "plan",
            "kb",
            "fix",
            "--apply",
            "--json-only",
        ],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        env={**dict(os.environ), "KB_REGISTRY_PATH": str(registry_path)},
    )

    # Should succeed
    assert result.returncode == 0

    # Should output valid JSON
    output = result.stdout.strip()
    data = json.loads(output)

    # Verify mode
    assert data["mode"] == "apply"

    # Verify manifest was created if files were created
    if data["summary"].get("files_created"):
        manifest_dir = repo_root / "evidence" / "plan_kb_fix"
        assert manifest_dir.exists()
        manifests = list(manifest_dir.glob("run-*.json"))
        assert len(manifests) > 0
