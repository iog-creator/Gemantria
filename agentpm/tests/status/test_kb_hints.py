#!/usr/bin/env python3
"""
Tests for KB hints generation (KB-Reg:M4)
"""

from __future__ import annotations

import sys
from pathlib import Path


# Add project root to path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from agentpm.kb.registry import KBDocument, KBDocumentRegistry, save_registry
from agentpm.status.snapshot import get_kb_hints, get_kb_status_view


def test_kb_hints_no_issues(tmp_path: Path) -> None:
    """Test that KB hints returns empty list when no issues."""
    # Create a registry with valid docs
    registry = KBDocumentRegistry()
    # Create actual files so they exist
    test_file1 = tmp_path / "docs" / "test1.md"
    test_file1.parent.mkdir(parents=True, exist_ok=True)
    test_file1.write_text("# Test 1")
    test_file2 = tmp_path / "docs" / "test2.md"
    test_file2.write_text("# Test 2")

    doc1 = KBDocument(
        id="test-1",
        title="Test Document 1",
        path=str(test_file1.relative_to(tmp_path)),
        type="ssot",
        owning_subsystem="docs",
        tags=["test"],
    )
    doc2 = KBDocument(
        id="test-2",
        title="Test Document 2",
        path=str(test_file2.relative_to(tmp_path)),
        type="ssot",
        owning_subsystem="docs",
        tags=["test"],
    )
    registry.add_document(doc1)
    registry.add_document(doc2)

    # Save to temp path
    registry_path = tmp_path / "kb_registry.json"
    save_registry(registry, registry_path)

    # Get hints - use absolute paths in registry
    doc1_abs = KBDocument(
        id="test-1",
        title="Test Document 1",
        path=str(test_file1),  # Absolute path
        type="ssot",
        owning_subsystem="docs",
        tags=["test"],
    )
    doc2_abs = KBDocument(
        id="test-2",
        title="Test Document 2",
        path=str(test_file2),  # Absolute path
        type="ssot",
        owning_subsystem="docs",
        tags=["test"],
    )
    registry_abs = KBDocumentRegistry()
    registry_abs.add_document(doc1_abs)
    registry_abs.add_document(doc2_abs)
    save_registry(registry_abs, registry_path)

    # Get hints
    kb_status_view = get_kb_status_view(registry_path=registry_path)
    hints = get_kb_hints(kb_status_view)

    # Should have no missing file hints (files exist)
    missing_hints = [h for h in hints if h.get("code") == "KB_MISSING_DOCS"]
    assert len(missing_hints) == 0


def test_kb_hints_missing_docs(tmp_path: Path) -> None:
    """Test that KB hints detects missing files."""
    # Create a registry with a missing file
    registry = KBDocumentRegistry()
    doc1 = KBDocument(
        id="test-1",
        title="Test Document 1",
        path="docs/nonexistent.md",  # File doesn't exist
        type="ssot",
        owning_subsystem="docs",
        tags=["test"],
    )
    registry.add_document(doc1)

    # Save to temp path
    registry_path = tmp_path / "kb_registry.json"
    save_registry(registry, registry_path)

    # Get hints
    kb_status_view = get_kb_status_view(registry_path=registry_path)
    hints = get_kb_hints(kb_status_view)

    # Should have a missing docs hint
    assert len(hints) > 0
    missing_hint = next((h for h in hints if h.get("code") == "KB_MISSING_DOCS"), None)
    assert missing_hint is not None
    assert missing_hint["level"] == "WARN"
    assert "missing_count" in missing_hint


def test_kb_hints_low_coverage(tmp_path: Path) -> None:
    """Test that KB hints detects low coverage subsystems."""
    # Create a registry with low coverage subsystem
    registry = KBDocumentRegistry()
    doc1 = KBDocument(
        id="test-1",
        title="Test Document 1",
        path="docs/test1.md",
        type="ssot",
        owning_subsystem="webui",  # Only 1 doc
        tags=["test"],
    )
    registry.add_document(doc1)

    # Save to temp path
    registry_path = tmp_path / "kb_registry.json"
    save_registry(registry, registry_path)

    # Get hints
    kb_status_view = get_kb_status_view(registry_path=registry_path)
    hints = get_kb_hints(kb_status_view)

    # Should have a low coverage hint
    assert len(hints) > 0
    coverage_hint = next((h for h in hints if h.get("code") == "KB_LOW_COVERAGE_SUBSYSTEM"), None)
    assert coverage_hint is not None
    assert coverage_hint["level"] == "INFO"
    assert coverage_hint["subsystem"] == "webui"
    assert coverage_hint["have"] == 1


def test_kb_hints_unavailable_registry() -> None:
    """Test that KB hints handles unavailable registry gracefully."""
    # Use a non-existent path
    from pathlib import Path

    registry_path = Path("/nonexistent/kb_registry.json")
    kb_status_view = get_kb_status_view(registry_path=registry_path)
    hints = get_kb_hints(kb_status_view)

    # Should have registry unavailable hint
    assert len(hints) > 0
    unavailable_hint = next((h for h in hints if h.get("code") == "KB_REGISTRY_UNAVAILABLE"), None)
    assert unavailable_hint is not None
    assert unavailable_hint["level"] == "INFO"


def test_kb_hints_empty_registry(tmp_path: Path) -> None:
    """Test that KB hints detects empty registry."""
    # Create an empty registry
    registry = KBDocumentRegistry()

    # Save to temp path
    registry_path = tmp_path / "kb_registry.json"
    save_registry(registry, registry_path)

    # Get hints
    kb_status_view = get_kb_status_view(registry_path=registry_path)
    hints = get_kb_hints(kb_status_view)

    # Should have empty registry hint
    assert len(hints) > 0
    empty_hint = next((h for h in hints if h.get("code") == "KB_EMPTY_REGISTRY"), None)
    assert empty_hint is not None
    assert empty_hint["level"] == "INFO"


def test_kb_hints_stale_docs(tmp_path: Path) -> None:
    """Test that KB hints detects stale documents (KB-Reg:M6)."""
    from datetime import datetime, timedelta, UTC

    # Create a registry with a stale document
    registry = KBDocumentRegistry()
    test_file = tmp_path / "docs" / "stale.md"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("# Stale Document")

    # Create document with old last_refreshed_at (beyond refresh interval)
    old_date = (datetime.now(UTC) - timedelta(days=60)).isoformat()
    doc = KBDocument(
        id="stale-doc",
        title="Stale Document",
        path=str(test_file.relative_to(tmp_path)),
        type="ssot",  # 30 day refresh interval
        owning_subsystem="docs",
        last_refreshed_at=old_date,
    )
    registry.add_document(doc)

    # Save to temp path
    registry_path = tmp_path / "kb_registry.json"
    save_registry(registry, registry_path)

    # Get hints
    kb_status_view = get_kb_status_view(registry_path=registry_path)
    hints = get_kb_hints(kb_status_view)

    # Should have a stale docs hint
    stale_hint = next((h for h in hints if h.get("code") == "KB_DOC_STALE"), None)
    assert stale_hint is not None
    assert stale_hint["level"] == "WARN"
    assert stale_hint["stale_count"] == 1
    assert "stale_docs" in stale_hint
    assert len(stale_hint["stale_docs"]) == 1
    assert stale_hint["stale_docs"][0]["id"] == "stale-doc"


def test_kb_hints_out_of_sync_docs(tmp_path: Path) -> None:
    """Test that KB hints detects out-of-sync documents (KB-Reg:M6)."""
    import time

    # Create a file
    test_file = tmp_path / "docs" / "out_of_sync.md"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("# Original")
    initial_mtime = test_file.stat().st_mtime

    # Wait and modify the file
    time.sleep(1.1)
    test_file.write_text("# Updated")

    # Create a registry with an out-of-sync document
    registry = KBDocumentRegistry()
    doc = KBDocument(
        id="out-of-sync-doc",
        title="Out of Sync Document",
        path=str(test_file.relative_to(tmp_path)),
        type="ssot",
        owning_subsystem="docs",
        last_seen_mtime=initial_mtime,  # Older than current file mtime
    )
    registry.add_document(doc)

    # Save to temp path
    registry_path = tmp_path / "kb_registry.json"
    save_registry(registry, registry_path)

    # Get hints
    kb_status_view = get_kb_status_view(registry_path=registry_path)
    hints = get_kb_hints(kb_status_view)

    # Should have an out-of-sync hint
    out_of_sync_hint = next((h for h in hints if h.get("code") == "KB_DOC_OUT_OF_SYNC"), None)
    assert out_of_sync_hint is not None
    assert out_of_sync_hint["level"] == "WARN"
    assert out_of_sync_hint["out_of_sync_count"] == 1
    assert "out_of_sync_docs" in out_of_sync_hint
    assert len(out_of_sync_hint["out_of_sync_docs"]) == 1
    assert out_of_sync_hint["out_of_sync_docs"][0]["id"] == "out-of-sync-doc"
