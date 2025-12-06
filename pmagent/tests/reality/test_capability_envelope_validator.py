"""Tests for capability_session envelope validator."""

from __future__ import annotations

import json
from pathlib import Path

from pmagent.reality.capability_envelope_validator import (
    scan_capability_envelopes,
    validate_capability_envelope,
    validate_capability_envelope_file,
)


def test_validate_capability_envelope_minimal_ok() -> None:
    """validate_capability_envelope should pass for a minimal valid envelope."""
    envelope = {
        "type": "capability_session",
        "version": "1.0",
        "id": "NEXT_STEPS:1",
        "title": "Test task",
        "source": "NEXT_STEPS",
        "plan": {
            "current_focus": "Phase X",
            "next_milestone": "Phase Y",
            "raw_line": "- Test task",
        },
        "posture": {
            "mode": "live",
            "reality": {"overall_ok": True},
            "status": {"level": "OK", "headline": "All systems nominal"},
        },
        "available": True,
    }

    result = validate_capability_envelope(envelope)

    assert result["ok"] is True
    assert len(result["errors"]) == 0
    assert "derived_tracking" in result
    assert result["derived_tracking"]["command"] == "plan.reality-loop"
    assert result["derived_tracking"]["request_json"] == envelope


def test_validate_capability_envelope_with_dry_run_command() -> None:
    """validate_capability_envelope should use dry_run_command when present."""
    envelope = {
        "type": "capability_session",
        "version": "1.0",
        "id": "NEXT_STEPS:1",
        "title": "Test task",
        "source": "NEXT_STEPS",
        "plan": {
            "current_focus": "Phase X",
            "next_milestone": "Phase Y",
            "raw_line": "- Test task",
            "dry_run_command": "make book.go",
        },
        "posture": {
            "mode": "hermetic",
        },
        "available": True,
    }

    result = validate_capability_envelope(envelope)

    assert result["ok"] is True
    assert result["derived_tracking"]["command"] == "make book.go"


def test_validate_capability_envelope_missing_required_fields() -> None:
    """validate_capability_envelope should fail for missing required fields."""
    envelope = {
        "type": "capability_session",
        "version": "1.0",
        # Missing id, title, source, plan, posture
    }

    result = validate_capability_envelope(envelope)

    assert result["ok"] is False
    assert len(result["errors"]) > 0
    assert any("id" in error.lower() for error in result["errors"])
    assert any("title" in error.lower() for error in result["errors"])
    assert any("plan" in error.lower() for error in result["errors"])


def test_validate_capability_envelope_invalid_type() -> None:
    """validate_capability_envelope should fail for wrong type."""
    envelope = {
        "type": "wrong_type",
        "version": "1.0",
        "id": "NEXT_STEPS:1",
        "title": "Test",
        "source": "NEXT_STEPS",
        "plan": {},
        "posture": {"mode": "hermetic"},
    }

    result = validate_capability_envelope(envelope)

    assert result["ok"] is False
    assert any("type" in error.lower() for error in result["errors"])


def test_validate_capability_envelope_invalid_dry_run_command() -> None:
    """validate_capability_envelope should fail for invalid dry_run_command."""
    envelope = {
        "type": "capability_session",
        "version": "1.0",
        "id": "NEXT_STEPS:1",
        "title": "Test task",
        "source": "NEXT_STEPS",
        "plan": {
            "dry_run_command": "",  # Empty string is invalid
        },
        "posture": {
            "mode": "hermetic",
        },
        "available": True,
    }

    result = validate_capability_envelope(envelope)

    assert result["ok"] is False
    assert any("dry_run_command" in error.lower() for error in result["errors"])


def test_validate_capability_envelope_file(tmp_path: Path) -> None:
    """validate_capability_envelope_file should read and validate a file."""
    envelope = {
        "type": "capability_session",
        "version": "1.0",
        "id": "NEXT_STEPS:1",
        "title": "Test task",
        "source": "NEXT_STEPS",
        "plan": {
            "current_focus": "Phase X",
            "next_milestone": "Phase Y",
            "raw_line": "- Test task",
        },
        "posture": {
            "mode": "live",
            "reality": {"overall_ok": True},
            "status": {"level": "OK", "headline": "All systems nominal"},
        },
        "available": True,
    }

    file_path = tmp_path / "capability_session-test.json"
    file_path.write_text(json.dumps(envelope), encoding="utf-8")

    result = validate_capability_envelope_file(file_path)

    assert result["ok"] is True
    assert result["file_path"] == str(file_path)
    assert result["file_error"] is None
    assert "derived_tracking" in result


def test_validate_capability_envelope_file_missing() -> None:
    """validate_capability_envelope_file should handle missing file."""
    file_path = Path("/nonexistent/file.json")

    result = validate_capability_envelope_file(file_path)

    assert result["ok"] is False
    assert result["file_error"] is not None
    assert "does not exist" in result["file_error"]


def test_validate_capability_envelope_file_invalid_json(tmp_path: Path) -> None:
    """validate_capability_envelope_file should handle invalid JSON."""
    file_path = tmp_path / "invalid.json"
    file_path.write_text("not json", encoding="utf-8")

    result = validate_capability_envelope_file(file_path)

    assert result["ok"] is False
    assert result["file_error"] is not None
    assert "Invalid JSON" in result["file_error"]


def test_scan_capability_envelopes_reports_errors_and_warnings(tmp_path: Path) -> None:
    """scan_capability_envelopes should aggregate validation results."""
    evidence_dir = tmp_path / "evidence" / "pmagent"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Create one valid envelope
    valid_envelope = {
        "type": "capability_session",
        "version": "1.0",
        "id": "NEXT_STEPS:1",
        "title": "Valid task",
        "source": "NEXT_STEPS",
        "plan": {
            "current_focus": "Phase X",
            "next_milestone": "Phase Y",
            "raw_line": "- Valid task",
        },
        "posture": {
            "mode": "live",
            "reality": {"overall_ok": True},
            "status": {"level": "OK", "headline": "All systems nominal"},
        },
        "available": True,
    }
    valid_file = evidence_dir / "capability_session-2025-11-22T01-00-00+00-00.json"
    valid_file.write_text(json.dumps(valid_envelope), encoding="utf-8")

    # Create one invalid envelope (missing required fields)
    invalid_envelope = {
        "type": "capability_session",
        "version": "1.0",
        # Missing id, title, source, plan, posture
    }
    invalid_file = evidence_dir / "capability_session-2025-11-22T02-00-00+00-00.json"
    invalid_file.write_text(json.dumps(invalid_envelope), encoding="utf-8")

    # Create one envelope with warnings (missing optional fields in live mode)
    warning_envelope = {
        "type": "capability_session",
        "version": "1.0",
        "id": "NEXT_STEPS:2",
        "title": "Warning task",
        "source": "NEXT_STEPS",
        "plan": {
            "current_focus": "Phase X",
            "next_milestone": "Phase Y",
            "raw_line": "- Warning task",
        },
        "posture": {
            "mode": "live",
            # Missing reality and status (warnings)
        },
        "available": True,
    }
    warning_file = evidence_dir / "capability_session-2025-11-22T03-00-00+00-00.json"
    warning_file.write_text(json.dumps(warning_envelope), encoding="utf-8")

    report = scan_capability_envelopes(evidence_dir=evidence_dir)

    assert report["total_files"] == 3
    assert report["ok_count"] == 2  # valid + warning (warnings don't fail validation)
    assert report["error_count"] == 1
    assert report["warning_count"] == 1
    assert len(report["files_with_errors"]) == 1
    assert len(report["files_with_warnings"]) == 1
    assert str(invalid_file) in report["files_with_errors"][0]["file_path"]
    assert str(warning_file) in report["files_with_warnings"][0]["file_path"]


def test_scan_capability_envelopes_empty_directory(tmp_path: Path) -> None:
    """scan_capability_envelopes should handle empty directory."""
    evidence_dir = tmp_path / "evidence" / "pmagent"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    report = scan_capability_envelopes(evidence_dir=evidence_dir)

    assert report["total_files"] == 0
    assert report["ok_count"] == 0
    assert report["error_count"] == 0
    assert report["warning_count"] == 0


def test_scan_capability_envelopes_nonexistent_directory() -> None:
    """scan_capability_envelopes should handle nonexistent directory."""
    evidence_dir = Path("/nonexistent/evidence/pmagent")

    report = scan_capability_envelopes(evidence_dir=evidence_dir)

    assert report["total_files"] == 0
    assert report["ok_count"] == 0
    assert report["error_count"] == 0
    assert report["warning_count"] == 0
