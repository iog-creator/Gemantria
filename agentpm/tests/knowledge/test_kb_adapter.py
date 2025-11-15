"""Tests for knowledge base adapter (Phase-6 6D)."""

from __future__ import annotations

import json

from agentpm.knowledge.adapter import (
    load_kb_docs_widget_props,
    OFFLINE_SAFE_DEFAULT,
)


def test_load_kb_docs_widget_props_happy_path(tmp_path, monkeypatch):
    """Test loading KB docs with valid JSON file."""
    # Create a fake kb_docs.head.json
    fake_kb_file = tmp_path / "kb_docs.head.json"
    fake_data = {
        "schema": "knowledge",
        "generated_at": "2025-11-15T12:00:00Z",
        "ok": True,
        "connection_ok": True,
        "docs": [
            {
                "id": "doc-1",
                "title": "Test Document 1",
                "section": "general",
                "slug": "test-document-1",
                "tags": ["test", "example"],
                "preview": "This is a test document preview...",
                "created_at": "2025-11-15T10:00:00Z",
            },
            {
                "id": "doc-2",
                "title": "Test Document 2",
                "section": "bible",
                "slug": "test-document-2",
                "tags": [],
                "preview": "Another test document...",
                "created_at": "2025-11-15T11:00:00Z",
            },
        ],
        "db_off": False,
        "error": None,
    }
    fake_kb_file.write_text(json.dumps(fake_data), encoding="utf-8")

    # Mock the path
    monkeypatch.setattr(
        "agentpm.knowledge.adapter.KB_DOCS_PATH",
        fake_kb_file,
    )

    # Load widget props
    props = load_kb_docs_widget_props()

    # Verify structure
    assert isinstance(props, dict)
    assert "docs" in props
    assert "db_off" in props
    assert "ok" in props
    assert "error" in props
    assert "generated_at" in props
    assert "source" in props

    # Verify docs
    assert len(props["docs"]) == 2
    assert props["docs"][0]["id"] == "doc-1"
    assert props["docs"][0]["title"] == "Test Document 1"
    assert props["docs"][0]["section"] == "general"
    assert props["docs"][0]["slug"] == "test-document-1"
    assert props["docs"][0]["tags"] == ["test", "example"]
    assert props["docs"][0]["preview"] == "This is a test document preview..."
    assert props["docs"][1]["id"] == "doc-2"
    assert props["docs"][1]["section"] == "bible"

    # Verify metadata
    assert props["db_off"] is False
    assert props["ok"] is True
    assert props["error"] is None
    assert props["generated_at"] == "2025-11-15T12:00:00Z"
    assert props["source"]["path"] == str(fake_kb_file)


def test_load_kb_docs_widget_props_missing_file(tmp_path, monkeypatch):
    """Test loading KB docs when file is missing (db_off scenario)."""
    # Mock the path to a non-existent file
    fake_kb_file = tmp_path / "nonexistent.json"
    monkeypatch.setattr(
        "agentpm.knowledge.adapter.KB_DOCS_PATH",
        fake_kb_file,
    )

    # Load widget props
    props = load_kb_docs_widget_props()

    # Should return offline-safe default
    assert props == OFFLINE_SAFE_DEFAULT
    assert props["docs"] == []
    assert props["db_off"] is True
    assert props["ok"] is False
    assert props["error"] is not None
    assert "unavailable" in props["error"].lower() or "offline" in props["error"].lower()


def test_load_kb_docs_widget_props_malformed_json(tmp_path, monkeypatch):
    """Test loading KB docs with malformed JSON (safe fallback)."""
    # Create a file with invalid JSON
    fake_kb_file = tmp_path / "kb_docs.head.json"
    fake_kb_file.write_text("{ invalid json }", encoding="utf-8")

    # Mock the path
    monkeypatch.setattr(
        "agentpm.knowledge.adapter.KB_DOCS_PATH",
        fake_kb_file,
    )

    # Load widget props
    props = load_kb_docs_widget_props()

    # Should return offline-safe default with error
    assert isinstance(props, dict)
    assert props["docs"] == []
    assert props["db_off"] is True
    assert props["ok"] is False
    assert props["error"] is not None
    assert "Failed to load KB export" in props["error"]


def test_load_kb_docs_widget_props_empty_docs(tmp_path, monkeypatch):
    """Test loading KB docs with empty docs list (db_off scenario)."""
    # Create a file with empty docs
    fake_kb_file = tmp_path / "kb_docs.head.json"
    fake_data = {
        "schema": "knowledge",
        "generated_at": "2025-11-15T12:00:00Z",
        "ok": False,
        "connection_ok": False,
        "docs": [],
        "db_off": True,
        "error": "GEMATRIA_DSN not set",
    }
    fake_kb_file.write_text(json.dumps(fake_data), encoding="utf-8")

    # Mock the path
    monkeypatch.setattr(
        "agentpm.knowledge.adapter.KB_DOCS_PATH",
        fake_kb_file,
    )

    # Load widget props
    props = load_kb_docs_widget_props()

    # Should return props with empty docs and db_off=True
    assert isinstance(props, dict)
    assert props["docs"] == []
    assert props["db_off"] is True
    assert props["ok"] is False
    assert props["error"] == "GEMATRIA_DSN not set"


def test_load_kb_docs_widget_props_invalid_doc_structure(tmp_path, monkeypatch):
    """Test loading KB docs with invalid doc structure (safe parsing)."""
    # Create a file with invalid doc structure
    fake_kb_file = tmp_path / "kb_docs.head.json"
    fake_data = {
        "schema": "knowledge",
        "generated_at": "2025-11-15T12:00:00Z",
        "ok": True,
        "connection_ok": True,
        "docs": [
            {"id": "doc-1", "title": "Valid Doc"},  # Missing some fields
            "invalid-doc-type",  # Not a dict
            {"id": "doc-3", "title": "Another Valid Doc", "section": "test"},  # Partial
        ],
        "db_off": False,
        "error": None,
    }
    fake_kb_file.write_text(json.dumps(fake_data), encoding="utf-8")

    # Mock the path
    monkeypatch.setattr(
        "agentpm.knowledge.adapter.KB_DOCS_PATH",
        fake_kb_file,
    )

    # Load widget props
    props = load_kb_docs_widget_props()

    # Should parse valid docs and skip invalid ones
    assert isinstance(props, dict)
    assert len(props["docs"]) == 2  # Only valid dicts
    assert props["docs"][0]["id"] == "doc-1"
    assert props["docs"][0]["title"] == "Valid Doc"
    assert props["docs"][1]["id"] == "doc-3"
    assert props["docs"][1]["title"] == "Another Valid Doc"
    assert props["docs"][1]["section"] == "test"
