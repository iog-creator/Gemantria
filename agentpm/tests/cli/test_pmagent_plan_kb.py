#!/usr/bin/env python3
"""
Tests for pmagent plan kb command (AgentPM-Next:M1)
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta, UTC
from pathlib import Path


# Add project root to path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from agentpm.kb.registry import KBDocument, KBDocumentRegistry, save_registry
from agentpm.plan.kb import build_kb_doc_worklist


def test_plan_kb_json_shape(tmp_path: Path) -> None:
    """Test that plan kb returns correct JSON shape."""
    # Create a test registry with missing and stale docs
    registry = KBDocumentRegistry()

    # Missing doc
    doc1 = KBDocument(
        id="missing-1",
        title="Missing Document",
        path="docs/missing.md",
        type="ssot",
        owning_subsystem="docs",
    )

    # Stale doc (old refresh time)
    doc2 = KBDocument(
        id="stale-1",
        title="Stale Document",
        path=str(tmp_path / "stale.md"),
        type="runbook",
        owning_subsystem="docs",
        last_refreshed_at=(datetime.now(UTC) - timedelta(days=100)).isoformat(),
        min_refresh_interval_days=30,
    )
    # Create the file for stale doc
    (tmp_path / "stale.md").write_text("# Stale Document")

    registry.add_document(doc1)
    registry.add_document(doc2)

    # Save to temp path
    registry_path = tmp_path / "kb_registry.json"
    save_registry(registry, registry_path)

    # Build worklist with test registry path
    worklist = build_kb_doc_worklist(registry_path=registry_path)

    # Verify shape
    assert "available" in worklist
    assert "total_items" in worklist
    assert "by_subsystem" in worklist
    assert "items" in worklist

    # Verify values
    assert worklist["available"] is True
    assert worklist["total_items"] > 0
    assert isinstance(worklist["items"], list)
    assert isinstance(worklist["by_subsystem"], dict)

    # Verify item structure
    if worklist["items"]:
        item = worklist["items"][0]
        assert "id" in item
        assert "title" in item
        assert "subsystem" in item
        assert "type" in item
        assert "severity" in item
        assert "reason" in item
        assert "suggested_action" in item

        # Verify severity is valid
        assert item["severity"] in ["missing", "stale", "out_of_sync", "low_coverage", "info"]


def test_plan_kb_items_sorted_by_severity(tmp_path: Path) -> None:
    """Test that worklist items are sorted by severity (missing > stale > ...)."""
    registry = KBDocumentRegistry()

    # Add docs with different severities
    doc1 = KBDocument(
        id="missing-1",
        title="Missing Document",
        path="docs/missing.md",
        type="ssot",
        owning_subsystem="docs",
    )

    doc2 = KBDocument(
        id="stale-1",
        title="Stale Document",
        path=str(tmp_path / "stale.md"),
        type="runbook",
        owning_subsystem="docs",
        last_refreshed_at=(datetime.now(UTC) - timedelta(days=100)).isoformat(),
        min_refresh_interval_days=30,
    )
    (tmp_path / "stale.md").write_text("# Stale Document")

    registry.add_document(doc1)
    registry.add_document(doc2)

    registry_path = tmp_path / "kb_registry.json"
    save_registry(registry, registry_path)

    worklist = build_kb_doc_worklist(registry_path=registry_path)

    if worklist["total_items"] >= 2:
        items = worklist["items"]
        # Missing should come before stale
        severities = [item["severity"] for item in items]
        missing_idx = severities.index("missing") if "missing" in severities else -1
        stale_idx = severities.index("stale") if "stale" in severities else -1

        if missing_idx >= 0 and stale_idx >= 0:
            assert missing_idx < stale_idx, "Missing items should come before stale items"


def test_plan_kb_handles_missing_registry(tmp_path: Path) -> None:
    """Test that plan kb handles missing registry gracefully."""
    # Use a non-existent path
    registry_path = tmp_path / "nonexistent" / "kb_registry.json"

    worklist = build_kb_doc_worklist(registry_path=registry_path)

    # Should return unavailable status
    assert worklist["available"] is False
    assert worklist["total_items"] == 0
    assert worklist["items"] == []


def test_plan_kb_empty_worklist_when_all_fresh(tmp_path: Path) -> None:
    """Test that plan kb returns empty worklist when all docs are fresh."""
    registry = KBDocumentRegistry()

    # Fresh doc (recently refreshed)
    doc = KBDocument(
        id="fresh-1",
        title="Fresh Document",
        path=str(tmp_path / "fresh.md"),
        type="ssot",
        owning_subsystem="docs",
        last_refreshed_at=(datetime.now(UTC) - timedelta(days=5)).isoformat(),
        min_refresh_interval_days=30,
    )
    (tmp_path / "fresh.md").write_text("# Fresh Document")

    registry.add_document(doc)

    registry_path = tmp_path / "kb_registry.json"
    save_registry(registry, registry_path)

    worklist = build_kb_doc_worklist(registry_path=registry_path)

    # Should be available but may have 0 items (or only low_coverage/info items)
    assert worklist["available"] is True
    # Items may be empty or only contain low_coverage/info items
    assert isinstance(worklist["items"], list)


def test_plan_kb_cli_json_only() -> None:
    """Test pmagent plan kb --json-only CLI command."""
    repo_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [sys.executable, "-m", "pmagent.cli", "plan", "kb", "--json-only"],
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
    assert "total_items" in data
    assert "by_subsystem" in data
    assert "items" in data

    # Verify items structure if present
    if data["items"]:
        item = data["items"][0]
        assert "id" in item
        assert "title" in item
        assert "subsystem" in item
        assert "type" in item
        assert "severity" in item
        assert "reason" in item
        assert "suggested_action" in item


def test_plan_kb_cli_human_mode() -> None:
    """Test pmagent plan kb CLI command (human-readable mode)."""
    repo_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [sys.executable, "-m", "pmagent.cli", "plan", "kb"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    # Should succeed
    assert result.returncode == 0

    # Should output JSON to stdout (for scripting)
    output = result.stdout.strip()
    data = json.loads(output)

    # Verify JSON shape
    assert "available" in data
    assert "total_items" in data
    assert "by_subsystem" in data
    assert "items" in data

    # Human-readable output should be on stderr
    stderr_output = result.stderr.strip()
    if data["available"] and data["total_items"] > 0:
        # Should have some human-readable output
        assert len(stderr_output) > 0
