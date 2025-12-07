"""Tests for reality sessions summary (read-only capability_session summary)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from pmagent.reality.sessions_summary import summarize_tracked_sessions


def test_summarize_tracked_sessions_empty_dir(tmp_path: Path, monkeypatch) -> None:
    """Test that empty directory returns zero counts and None agent_run_cli fields."""
    evidence_dir = tmp_path / "evidence" / "pmagent"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Monkeypatch REPO_ROOT to use tmp_path
    monkeypatch.setattr("pmagent.reality.sessions_summary.REPO_ROOT", tmp_path)

    with patch("pmagent.reality.sessions_summary.get_rw_dsn", return_value=None):
        summary = summarize_tracked_sessions(limit=10, evidence_dir=evidence_dir)

    assert summary["envelopes"]["count"] == 0
    assert summary["envelopes"]["latest"] == []
    assert summary["tracking"]["db_mode"] == "db_off"
    assert summary["tracking"]["agent_run_cli"] is None


def test_summarize_tracked_sessions_with_envelopes(tmp_path: Path, monkeypatch) -> None:
    """Test that non-empty directory returns correct counts and latest entries."""
    evidence_dir = tmp_path / "evidence" / "pmagent"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Create 3 fake capability_session JSON files
    envelope1 = {
        "type": "capability_session",
        "version": "1.0",
        "id": "NEXT_STEPS:1",
        "title": "Test task 1",
        "source": "NEXT_STEPS",
        "plan": {
            "current_focus": "Phase 1",
            "next_milestone": "M1",
            "raw_line": "- Task 1",
            "dry_run_command": "make book.go",
        },
        "posture": {"mode": "live"},
        "timestamp": "2024-01-01T00:00:00Z",
    }

    envelope2 = {
        "type": "capability_session",
        "version": "1.0",
        "id": "NEXT_STEPS:2",
        "title": "Test task 2",
        "source": "NEXT_STEPS",
        "plan": {
            "current_focus": "Phase 2",
            "next_milestone": "M2",
            "raw_line": "- Task 2",
        },
        "posture": {"mode": "hermetic"},
        "timestamp": "2024-01-02T00:00:00Z",
    }

    envelope3 = {
        "type": "capability_session",
        "version": "1.0",
        "id": "NEXT_STEPS:3",
        "title": "Test task 3",
        "source": "MASTER_PLAN",
        "plan": {
            "current_focus": "Phase 3",
            "next_milestone": "M3",
            "raw_line": "- Task 3",
            "dry_run_command": "make eval.graph.calibrate.adv",
        },
        "posture": {"mode": "live"},
        "timestamp": "2024-01-03T00:00:00Z",
    }

    # Write files with different timestamps (newest first)
    file1 = evidence_dir / "capability_session-2024-01-01T00:00:00Z.json"
    file2 = evidence_dir / "capability_session-2024-01-02T00:00:00Z.json"
    file3 = evidence_dir / "capability_session-2024-01-03T00:00:00Z.json"

    file1.write_text(json.dumps(envelope1, indent=2), encoding="utf-8")
    file2.write_text(json.dumps(envelope2, indent=2), encoding="utf-8")
    file3.write_text(json.dumps(envelope3, indent=2), encoding="utf-8")

    # Touch files to set mtime (newest first: file3 > file2 > file1)
    import time

    file1.touch()
    time.sleep(0.01)
    file2.touch()
    time.sleep(0.01)
    file3.touch()

    with patch("pmagent.reality.sessions_summary.get_rw_dsn", return_value=None):
        summary = summarize_tracked_sessions(limit=10, evidence_dir=evidence_dir)

    assert summary["envelopes"]["count"] == 3
    latest = summary["envelopes"]["latest"]
    assert len(latest) == 3

    # Check that latest is ordered newest-first (file3 should be first)
    assert latest[0]["id"] == "NEXT_STEPS:3"
    assert latest[0]["title"] == "Test task 3"
    assert latest[0]["posture_mode"] == "live"
    assert latest[0]["dry_run_command"] == "make eval.graph.calibrate.adv"
    assert latest[0]["source"] == "MASTER_PLAN"

    assert latest[1]["id"] == "NEXT_STEPS:2"
    assert latest[1]["posture_mode"] == "hermetic"
    assert latest[1]["dry_run_command"] is None

    assert latest[2]["id"] == "NEXT_STEPS:1"
    assert latest[2]["dry_run_command"] == "make book.go"

    assert summary["tracking"]["db_mode"] == "db_off"
    assert summary["tracking"]["agent_run_cli"] is None


def test_summarize_tracked_sessions_respects_limit(tmp_path: Path, monkeypatch) -> None:
    """Test that limit parameter restricts the number of latest entries."""
    evidence_dir = tmp_path / "evidence" / "pmagent"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Create 5 fake files
    for i in range(5):
        envelope = {
            "type": "capability_session",
            "version": "1.0",
            "id": f"NEXT_STEPS:{i}",
            "title": f"Test task {i}",
            "source": "NEXT_STEPS",
            "plan": {
                "current_focus": f"Phase {i}",
                "next_milestone": f"M{i}",
                "raw_line": f"- Task {i}",
            },
            "posture": {"mode": "live"},
            "timestamp": f"2024-01-0{i + 1}T00:00:00Z",
        }
        file_path = evidence_dir / f"capability_session-2024-01-0{i + 1}T00:00:00Z.json"
        file_path.write_text(json.dumps(envelope, indent=2), encoding="utf-8")
        import time

        time.sleep(0.01)  # Ensure different mtimes
        file_path.touch()

    with patch("pmagent.reality.sessions_summary.get_rw_dsn", return_value=None):
        summary = summarize_tracked_sessions(limit=3, evidence_dir=evidence_dir)

    assert summary["envelopes"]["count"] == 5  # Total count is all files
    assert len(summary["envelopes"]["latest"]) == 3  # But latest is limited to 3


def test_summarize_tracked_sessions_handles_invalid_json_gracefully(tmp_path: Path, monkeypatch) -> None:
    """Test that invalid JSON files are skipped gracefully."""
    evidence_dir = tmp_path / "evidence" / "pmagent"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Create one valid and one invalid file
    valid_envelope = {
        "type": "capability_session",
        "version": "1.0",
        "id": "NEXT_STEPS:1",
        "title": "Valid task",
        "source": "NEXT_STEPS",
        "plan": {"current_focus": "Phase 1", "next_milestone": "M1", "raw_line": "- Task"},
        "posture": {"mode": "live"},
        "timestamp": "2024-01-01T00:00:00Z",
    }

    valid_file = evidence_dir / "capability_session-2024-01-01T00:00:00Z.json"
    valid_file.write_text(json.dumps(valid_envelope, indent=2), encoding="utf-8")

    invalid_file = evidence_dir / "capability_session-invalid.json"
    invalid_file.write_text("invalid json content", encoding="utf-8")

    with patch("pmagent.reality.sessions_summary.get_rw_dsn", return_value=None):
        summary = summarize_tracked_sessions(limit=10, evidence_dir=evidence_dir)

    # Should only count the valid file
    assert summary["envelopes"]["count"] == 2  # Both files exist
    assert len(summary["envelopes"]["latest"]) == 1  # But only one is valid
    assert summary["envelopes"]["latest"][0]["id"] == "NEXT_STEPS:1"
