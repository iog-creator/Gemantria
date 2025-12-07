"""Tests for knowledge base ingestion and export (Phase-6 6C)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_kb_ingest_handles_missing_db(monkeypatch, tmp_path):
    """
    If DB is unavailable, the ingestion script should fail-soft (db_off)
    and not raise unhandled exceptions.
    """
    # Create a test markdown file
    test_md = tmp_path / "test.md"
    test_md.write_text("# Test Document\n\nThis is test content.", encoding="utf-8")

    # Mock get_rw_dsn to return None (db_off)
    with patch("scripts.db.control_kb_ingest.get_rw_dsn", return_value=None):
        import scripts.db.control_kb_ingest as kb_ingest  # type: ignore[import]

        # Should exit 0 (fail-soft) when DB is unavailable
        import sys

        with patch.object(sys, "argv", ["control_kb_ingest.py", str(tmp_path)]):
            try:
                kb_ingest.main()
            except SystemExit as exc:
                # Should exit with code 0 (fail-soft)
                assert exc.code == 0
            else:
                # If no SystemExit, that's also acceptable (script may return normally)
                pass


def test_kb_export_writes_json(tmp_path, monkeypatch):
    """
    The export script should write a valid JSON file with either:
    - a list of docs, or
    - a dict with db_off marker.
    """
    output = tmp_path / "kb_docs.head.json"

    import scripts.db.control_kb_export as kb_export  # type: ignore[import]

    # Mock the output path
    monkeypatch.setattr(kb_export, "_get_output_path", lambda: output, raising=False)

    # Mock get_rw_dsn to return None (db_off scenario)
    with patch("scripts.db.control_kb_export.get_rw_dsn", return_value=None):
        kb_export.main()

        assert output.exists()
        data = json.loads(output.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        # Should have db_off marker when DB unavailable
        assert data.get("db_off") is True
        assert "docs" in data
        assert isinstance(data["docs"], list)


def test_kb_export_schema_structure(tmp_path, monkeypatch):
    """Verify export JSON has expected schema fields."""
    output = tmp_path / "kb_docs.head.json"

    import scripts.db.control_kb_export as kb_export  # type: ignore[import]

    monkeypatch.setattr(kb_export, "_get_output_path", lambda: output, raising=False)

    # Mock db_off scenario
    with patch("scripts.db.control_kb_export.get_rw_dsn", return_value=None):
        kb_export.main()

        data = json.loads(output.read_text(encoding="utf-8"))
        # Required fields
        assert "schema" in data
        assert "generated_at" in data
        assert "ok" in data
        assert "connection_ok" in data
        assert "docs" in data
        assert data["schema"] == "knowledge"


def test_slugify():
    """Test slug generation utility."""
    import scripts.db.control_kb_ingest as kb_ingest  # type: ignore[import]

    assert kb_ingest.slugify("Hello World") == "hello-world"
    assert kb_ingest.slugify("Test_Document") == "test-document"
    assert kb_ingest.slugify("Section/Subsection") == "section-subsection"
    assert kb_ingest.slugify("  Multiple   Spaces  ") == "multiple-spaces"


def test_extract_title_from_markdown():
    """Test title extraction from markdown."""
    import scripts.db.control_kb_ingest as kb_ingest  # type: ignore[import]

    # H1 present
    content1 = "# My Title\n\nContent here."
    assert kb_ingest.extract_title_from_markdown(content1, "file.md") == "My Title"

    # No H1, use filename
    content2 = "Just content, no title."
    assert kb_ingest.extract_title_from_markdown(content2, "my_document.md") == "My Document"
