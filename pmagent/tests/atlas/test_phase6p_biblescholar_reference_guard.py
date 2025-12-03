"""Tests for Phase-6P BibleScholar Reference Answer Slice Export."""

import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
BIBLESCHOLAR_REFERENCE_JSON = REPO / "share" / "atlas" / "control_plane" / "biblescholar_reference.json"
VIEWER_HTML = REPO / "docs" / "atlas" / "browser" / "biblescholar_reference.html"
GUARD_EVIDENCE = REPO / "evidence" / "guard_biblescholar_reference.json"


def test_phase6p_export_present():
    """Phase-6P: biblescholar_reference.json exists."""
    assert BIBLESCHOLAR_REFERENCE_JSON.exists(), "biblescholar_reference.json must exist"


def test_phase6p_export_structure():
    """Phase-6P: biblescholar_reference.json has correct structure."""
    assert BIBLESCHOLAR_REFERENCE_JSON.exists(), "biblescholar_reference.json must exist"

    with BIBLESCHOLAR_REFERENCE_JSON.open() as f:
        data = json.load(f)

    # Check required keys
    assert "schema" in data, "Missing 'schema' key"
    assert data["schema"] == "biblescholar_reference_v1", (
        f"Wrong schema: expected biblescholar_reference_v1, got {data['schema']}"
    )

    assert "generated_at" in data, "Missing 'generated_at' key"
    assert "ok" in data, "Missing 'ok' key"
    assert "questions" in data, "Missing 'questions' key"
    assert "summary" in data, "Missing 'summary' key"

    # Check questions structure (must be a list)
    questions = data["questions"]
    assert isinstance(questions, list), "questions must be a list"

    # Check summary structure
    summary = data["summary"]
    assert isinstance(summary, dict), "summary must be a dict"
    assert "total_questions" in summary, "Missing 'total_questions' in summary"
    assert "by_mode" in summary, "Missing 'by_mode' in summary"
    assert "by_verse_ref" in summary, "Missing 'by_verse_ref' in summary"

    # Validate question entries if present
    for i, q in enumerate(questions):
        assert isinstance(q, dict), f"Question {i} must be a dict"
        assert "run_id" in q, f"Question {i} missing 'run_id'"
        assert "question" in q, f"Question {i} missing 'question'"
        assert "created_at" in q, f"Question {i} missing 'created_at'"
        assert "metadata" in q, f"Question {i} missing 'metadata'"


def test_phase6p_viewer_present():
    """Phase-6P: biblescholar_reference.html exists."""
    assert VIEWER_HTML.exists(), "biblescholar_reference.html must exist"


def test_phase6p_viewer_backlinks():
    """Phase-6P: viewer HTML has required backlinks."""
    assert VIEWER_HTML.exists(), "biblescholar_reference.html must exist"

    content = VIEWER_HTML.read_text()

    required_backlinks = [
        "backlink-biblescholar-reference-json",
        "backlink-guard-biblescholar-reference-json",
        "backlink-compliance-summary",
        "backlink-violations-browser",
    ]

    for backlink_id in required_backlinks:
        assert f'data-testid="{backlink_id}"' in content, f"Missing backlink: {backlink_id}"


def test_phase6p_guard_evidence():
    """Phase-6P: guard evidence JSON exists and is valid."""
    # Guard evidence may not exist if guard hasn't been run yet
    # This test is non-blocking (just checks structure if present)
    if not GUARD_EVIDENCE.exists():
        return  # Skip if guard hasn't been run

    with GUARD_EVIDENCE.open() as f:
        evidence = json.load(f)

    assert "guard" in evidence, "Missing 'guard' key in evidence"
    assert evidence["guard"] == "guard_biblescholar_reference", f"Wrong guard name: {evidence['guard']}"
    assert "episode" in evidence, "Missing 'episode' key in evidence"
    assert evidence["episode"] == "Phase-6P", f"Wrong episode: expected Phase-6P, got {evidence['episode']}"
    assert "overall_ok" in evidence, "Missing 'overall_ok' key in evidence"
    assert "checks" in evidence, "Missing 'checks' key in evidence"
