#!/usr/bin/env python3
"""
Tests for pmagent status kb command (KB-Reg:M3b)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Add project root to path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from pmagent.kb.registry import KBDocument, KBDocumentRegistry, save_registry
from pmagent.status.snapshot import get_kb_status_view


def test_status_kb_json_shape(tmp_path: Path) -> None:
    """Test that status kb returns correct JSON shape."""
    # Create a test registry
    registry = KBDocumentRegistry()
    doc1 = KBDocument(
        id="test-1",
        title="Test Document 1",
        path="docs/test1.md",
        type="ssot",
        owning_subsystem="docs",
        tags=["test"],
    )
    doc2 = KBDocument(
        id="test-2",
        title="Test Document 2",
        path="docs/test2.md",
        type="runbook",
        owning_subsystem="docs",
        tags=["test", "governance"],
    )
    registry.add_document(doc1)
    registry.add_document(doc2)

    # Save to temp path
    registry_path = tmp_path / "kb_registry.json"
    save_registry(registry, registry_path)

    # Get status view
    status = get_kb_status_view(registry_path=registry_path)

    # Verify shape
    assert "available" in status
    assert "total" in status
    assert "by_subsystem" in status
    assert "by_type" in status
    assert "missing_files" in status
    assert "notes" in status

    # Verify values
    assert status["available"] is True
    assert status["total"] == 2
    assert status["by_subsystem"]["docs"] == 2
    assert status["by_type"]["ssot"] == 1
    assert status["by_type"]["runbook"] == 1
    assert isinstance(status["missing_files"], list)
    assert isinstance(status["notes"], list)


def test_status_kb_reflects_seeded_counts() -> None:
    """Test that status kb reflects seeded registry counts."""
    # Use the actual registry path (should exist after seeding)
    repo_root = Path(__file__).resolve().parents[3]
    registry_path = repo_root / "share" / "kb_registry.json"

    if not registry_path.exists():
        pytest.skip("Registry file not found (run seed_registry.py first)")

    status = get_kb_status_view(registry_path=registry_path)

    # Should have seeded documents
    assert status["available"] is True
    assert status["total"] > 0

    # Should have breakdowns
    assert len(status["by_subsystem"]) > 0
    assert len(status["by_type"]) > 0

    # Verify counts match
    total_from_subsystem = sum(status["by_subsystem"].values())
    total_from_type = sum(status["by_type"].values())
    assert total_from_subsystem == status["total"]
    assert total_from_type == status["total"]


def test_status_kb_handles_missing_registry(tmp_path: Path) -> None:
    """Test that status kb handles missing registry gracefully."""
    # Use a non-existent path
    registry_path = tmp_path / "nonexistent" / "kb_registry.json"

    status = get_kb_status_view(registry_path=registry_path)

    # Should return unavailable status
    assert status["available"] is False
    assert status["total"] == 0
    assert len(status["notes"]) > 0
    assert "not found" in status["notes"][0].lower() or "failed" in status["notes"][0].lower()


def test_status_kb_cli_json_only() -> None:
    """Test pmagent status kb --json-only CLI command."""
    repo_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [sys.executable, "-m", "pmagent.cli", "status", "kb", "--json-only"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    # Should succeed
    assert result.returncode == 0

    # Should output valid JSON
    output = result.stdout.strip()
    data = json.loads(output)

    # Verify shape
    assert "available" in data
    assert "total" in data
    assert "by_subsystem" in data
    assert "by_type" in data
    assert "missing_files" in data
    assert "notes" in data


def test_kb_registry_summary_cli_json_only() -> None:
    """Test pmagent kb registry summary --json-only CLI command."""
    repo_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [sys.executable, "-m", "pmagent.cli", "kb", "registry", "summary", "--json-only"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    # Should succeed
    assert result.returncode == 0

    # Should output valid JSON
    output = result.stdout.strip()
    data = json.loads(output)

    # Verify shape (same as status kb)
    assert "available" in data
    assert "total" in data
    assert "by_subsystem" in data
    assert "by_type" in data
    assert "missing_files" in data
    assert "notes" in data
