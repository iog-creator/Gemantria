"""Tests for pmagent plan next command."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from pmagent.plan.next import (
    build_capability_session,
    build_next_plan,
    list_capability_sessions,
    run_reality_loop,
)


def test_build_next_plan_with_sample_files(tmp_path: Path) -> None:
    """build_next_plan should parse Current Focus, Next Milestone, and bullets."""
    master = tmp_path / "MASTER_PLAN.md"
    master.write_text("**Current Focus**: Phase X test\n**Next Milestone**: Phase Y test\n")
    next_steps = tmp_path / "NEXT_STEPS.md"
    next_steps.write_text("# Next Gate / Next Steps\n- First task\n- Second task\n")

    result = build_next_plan(
        limit=2,
        master_plan_path=master,
        next_steps_path=next_steps,
    )

    assert result["available"] is True
    assert result["current_focus"] == "Phase X test"
    assert result["next_milestone"] == "Phase Y test"
    assert len(result["candidates"]) == 2
    assert result["candidates"][0]["title"] == "First task"
    assert result["candidates"][0]["id"] == "NEXT_STEPS:1"


def test_build_next_plan_handles_missing_files(tmp_path: Path) -> None:
    """Missing files should return available=False and empty candidates."""
    master = tmp_path / "missing_MASTER_PLAN.md"
    next_steps = tmp_path / "missing_NEXT_STEPS.md"

    result = build_next_plan(
        master_plan_path=master,
        next_steps_path=next_steps,
    )

    assert result["available"] is False
    assert result["candidates"] == []


def test_plan_next_cli_json_only() -> None:
    """pmagent plan next --json-only returns valid JSON with candidates field."""
    repo_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [sys.executable, "-m", "pmagent.cli", "plan", "next", "--json-only"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout.strip())
    assert "available" in data
    assert "candidates" in data


def test_plan_next_with_status_hints_when_commands_missing(tmp_path: Path) -> None:
    """Test that --with-status sets posture to hermetic when commands unavailable."""
    master = tmp_path / "MASTER_PLAN.md"
    master.write_text("**Current Focus**: Phase X test\n**Next Milestone**: Phase Y test\n")
    next_steps = tmp_path / "NEXT_STEPS.md"
    next_steps.write_text("# Next Gate / Next Steps\n- First task\n- Second task\n")

    # Mock subprocess.run to simulate missing commands
    with patch("pmagent.plan.next.subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError("pmagent command not found")

        result = build_next_plan(
            limit=2,
            master_plan_path=master,
            next_steps_path=next_steps,
            with_status=True,
        )

    assert result["available"] is True
    assert "posture" in result
    posture = result["posture"]
    assert posture["mode"] == "hermetic"
    assert posture.get("reality") is None
    assert posture.get("status") is None
    assert "error" in posture


def test_plan_next_with_status_merges_posture_json(tmp_path: Path) -> None:
    """Test that --with-status merges posture JSON when commands succeed."""
    master = tmp_path / "MASTER_PLAN.md"
    master.write_text("**Current Focus**: Phase X test\n**Next Milestone**: Phase Y test\n")
    next_steps = tmp_path / "NEXT_STEPS.md"
    next_steps.write_text("# Next Gate / Next Steps\n- First task\n- Second task\n")

    # Mock subprocess.run to return successful JSON responses
    mock_reality = {
        "overall_ok": True,
        "components": {"env": {"ok": True}, "db": {"ok": True}},
    }
    mock_status = {
        "level": "OK",
        "headline": "All systems nominal",
        "details": "DB ready, LM slots OK",
    }

    def mock_run(cmd, **kwargs):
        mock_result = MagicMock()
        mock_result.returncode = 0
        cmd_str = " ".join(cmd)
        if "reality-check" in cmd_str:
            mock_result.stdout = json.dumps(mock_reality)
        elif "status" in cmd_str and "explain" in cmd_str:
            mock_result.stdout = json.dumps(mock_status)
        else:
            mock_result.stdout = "{}"
        return mock_result

    with patch("pmagent.plan.next.subprocess.run", side_effect=mock_run):
        result = build_next_plan(
            limit=2,
            master_plan_path=master,
            next_steps_path=next_steps,
            with_status=True,
        )

    assert result["available"] is True
    assert "posture" in result
    posture = result["posture"]
    assert posture["mode"] == "live"
    assert posture["reality"] == mock_reality
    assert posture["status"] == mock_status
    assert "error" not in posture


def test_plan_open_builds_capability_session_envelope(tmp_path: Path) -> None:
    """build_capability_session should build a capability_session envelope with plan and posture."""
    master = tmp_path / "MASTER_PLAN.md"
    master.write_text("**Current Focus**: Phase X test\n**Next Milestone**: Phase Y test\n")
    next_steps = tmp_path / "NEXT_STEPS.md"
    next_steps.write_text("# Next Gate / Next Steps\n- First task\n- Second task\n")

    # Mock subprocess.run to return successful JSON responses
    mock_reality = {
        "overall_ok": True,
        "components": {"env": {"ok": True}, "db": {"ok": True}},
    }
    mock_status = {
        "level": "OK",
        "headline": "All systems nominal",
        "details": "DB ready, LM slots OK",
    }

    def mock_run(cmd, **kwargs):
        mock_result = MagicMock()
        mock_result.returncode = 0
        cmd_str = " ".join(cmd)
        if "reality-check" in cmd_str:
            mock_result.stdout = json.dumps(mock_reality)
        elif "status" in cmd_str and "explain" in cmd_str:
            mock_result.stdout = json.dumps(mock_status)
        else:
            mock_result.stdout = "{}"
        return mock_result

    with patch("pmagent.plan.next.subprocess.run", side_effect=mock_run):
        session = build_capability_session(
            "NEXT_STEPS:1",
            master_plan_path=master,
            next_steps_path=next_steps,
            with_status=True,
        )

    assert session["type"] == "capability_session"
    assert session["version"] == "1.0"
    assert session["id"] == "NEXT_STEPS:1"
    assert session["title"] == "First task"
    assert session["source"] == "NEXT_STEPS"
    assert session["available"] is True
    assert "plan" in session
    assert session["plan"]["current_focus"] == "Phase X test"
    assert session["plan"]["next_milestone"] == "Phase Y test"
    assert "posture" in session
    assert session["posture"]["mode"] == "live"
    assert session["posture"]["reality"] == mock_reality
    assert session["posture"]["status"] == mock_status


def test_plan_open_candidate_not_found_graceful(tmp_path: Path) -> None:
    """build_capability_session should return available=False when candidate not found."""
    master = tmp_path / "MASTER_PLAN.md"
    master.write_text("**Current Focus**: Phase X test\n**Next Milestone**: Phase Y test\n")
    next_steps = tmp_path / "NEXT_STEPS.md"
    next_steps.write_text("# Next Gate / Next Steps\n- First task\n")

    session = build_capability_session(
        "NEXT_STEPS:999",
        master_plan_path=master,
        next_steps_path=next_steps,
        with_status=False,
    )

    assert session["type"] == "capability_session"
    assert session["version"] == "1.0"
    assert session["id"] == "NEXT_STEPS:999"
    assert session["available"] is False
    assert "reason" in session
    assert "candidate_not_found" in session["reason"]


def test_pmagent_cli_plan_open_json_only() -> None:
    """pmagent plan open --json-only returns valid capability_session JSON envelope."""
    repo_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [sys.executable, "-m", "pmagent.cli", "plan", "open", "NEXT_STEPS:1", "--json-only"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    # Exit code 0 is expected even if candidate not found (graceful handling)
    assert result.returncode == 0
    data = json.loads(result.stdout.strip())
    assert data["type"] == "capability_session"
    assert data["version"] == "1.0"
    assert "id" in data
    assert "available" in data


def test_reality_loop_writes_capability_session_file(tmp_path: Path, monkeypatch) -> None:
    """run_reality_loop should write a capability_session envelope to evidence/pmagent/."""
    # Use tmp_path directly as evidence_dir
    evidence_dir = tmp_path / "evidence" / "pmagent"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Create test files
    master = tmp_path / "docs" / "SSOT" / "MASTER_PLAN.md"
    master.parent.mkdir(parents=True, exist_ok=True)
    master.write_text("**Current Focus**: Phase X test\n**Next Milestone**: Phase Y test\n")
    next_steps = tmp_path / "NEXT_STEPS.md"
    next_steps.write_text("# Next Gate / Next Steps\n- First test task\n- Second test task\n")

    # Mock subprocess.run to return successful JSON responses
    mock_reality = {
        "overall_ok": True,
        "components": {"env": {"ok": True}, "db": {"ok": True}},
    }
    mock_status = {
        "level": "OK",
        "headline": "All systems nominal",
        "details": "DB ready, LM slots OK",
    }

    def mock_run(cmd, **kwargs):
        mock_result = MagicMock()
        mock_result.returncode = 0
        cmd_str = " ".join(cmd)
        if "reality-check" in cmd_str:
            mock_result.stdout = json.dumps(mock_reality)
        elif "status" in cmd_str and "explain" in cmd_str:
            mock_result.stdout = json.dumps(mock_status)
        else:
            mock_result.stdout = "{}"
        return mock_result

    with patch("pmagent.plan.next.subprocess.run", side_effect=mock_run):
        result = run_reality_loop(
            limit=3,
            master_plan_path=master,
            next_steps_path=next_steps,
            evidence_dir=evidence_dir,
        )

    assert result["available"] is True
    assert result["candidate"] is not None
    assert result["candidate"]["id"] == "NEXT_STEPS:1"
    assert result["candidate"]["title"] == "First test task"
    assert result["envelope_path"] is not None

    # Verify the envelope file was created
    envelope_path = Path(result["envelope_path"])
    assert envelope_path.exists()
    assert envelope_path.name.startswith("capability_session-")
    assert envelope_path.name.endswith(".json")

    # Verify the envelope content
    envelope_data = json.loads(envelope_path.read_text())
    assert envelope_data["type"] == "capability_session"
    assert envelope_data["version"] == "1.0"
    assert envelope_data["id"] == "NEXT_STEPS:1"
    assert envelope_data["title"] == "First test task"
    assert "plan" in envelope_data
    assert "posture" in envelope_data
    assert envelope_data["posture"]["mode"] == "live"


def test_pmagent_cli_plan_reality_loop_json_only() -> None:
    """pmagent plan reality-loop --json-only returns valid JSON summary structure."""
    # Test the CLI command structure (may return available=False if no candidates, which is OK)
    repo_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [sys.executable, "-m", "pmagent.cli", "plan", "reality-loop", "--json-only"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    # Exit code 0 is expected even if no candidates (graceful handling)
    assert result.returncode == 0
    data = json.loads(result.stdout.strip())
    assert "available" in data
    # candidate and envelope_path may be None if no candidates available
    assert "candidate" in data or "error" in data
    assert "envelope_path" in data


def test_pmagent_cli_plan_reality_loop_no_candidates() -> None:
    """pmagent plan reality-loop handles no candidates gracefully (exit 0, advisory stderr)."""
    # Test that the CLI handles no candidates gracefully
    # This test may pass even if candidates exist (just validates graceful handling)
    repo_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [sys.executable, "-m", "pmagent.cli", "plan", "reality-loop"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    # Should exit 0 (advisory, not an error)
    assert result.returncode == 0
    data = json.loads(result.stdout.strip())
    assert "available" in data
    # If no candidates, should have error message
    if not data.get("available", False):
        assert "error" in data or "candidate" not in data or data.get("candidate") is None


def test_reality_loop_includes_dry_run_command_in_envelope(tmp_path: Path, monkeypatch) -> None:
    """run_reality_loop should include dry_run_command in the envelope when provided."""
    evidence_dir = tmp_path / "evidence" / "pmagent"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Create test files
    master = tmp_path / "docs" / "SSOT" / "MASTER_PLAN.md"
    master.parent.mkdir(parents=True, exist_ok=True)
    master.write_text("**Current Focus**: Phase X test\n**Next Milestone**: Phase Y test\n")
    next_steps = tmp_path / "NEXT_STEPS.md"
    next_steps.write_text("# Next Gate / Next Steps\n- Test task for dry-run\n")

    # Mock subprocess.run to return successful JSON responses
    mock_reality = {
        "overall_ok": True,
        "components": {"env": {"ok": True}, "db": {"ok": True}},
    }
    mock_status = {
        "level": "OK",
        "headline": "All systems nominal",
        "details": "DB ready, LM slots OK",
    }

    def mock_run(cmd, **kwargs):
        mock_result = MagicMock()
        mock_result.returncode = 0
        cmd_str = " ".join(cmd)
        if "reality-check" in cmd_str:
            mock_result.stdout = json.dumps(mock_reality)
        elif "status" in cmd_str and "explain" in cmd_str:
            mock_result.stdout = json.dumps(mock_status)
        else:
            mock_result.stdout = "{}"
        return mock_result

    with patch("pmagent.plan.next.subprocess.run", side_effect=mock_run):
        result = run_reality_loop(
            limit=1,
            master_plan_path=master,
            next_steps_path=next_steps,
            evidence_dir=evidence_dir,
            dry_run_command="make book.go",
        )

    assert result["available"] is True
    assert result["dry_run_command"] == "make book.go"

    # Verify the envelope file includes dry_run_command
    envelope_path = Path(result["envelope_path"])
    assert envelope_path.exists()
    envelope_data = json.loads(envelope_path.read_text())
    assert envelope_data["plan"]["dry_run_command"] == "make book.go"


def test_pmagent_cli_plan_reality_loop_with_dry_run_command() -> None:
    """pmagent plan reality-loop --dry-run-command includes the command in JSON output."""
    repo_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pmagent.cli",
            "plan",
            "reality-loop",
            "--limit",
            "1",
            "--dry-run-command",
            "make book.go",
            "--json-only",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    # Exit code 0 expected (even if no candidates, it's advisory)
    assert result.returncode == 0
    data = json.loads(result.stdout.strip())
    assert "available" in data
    # If available is True, should have dry_run_command
    if data.get("available", False):
        assert "dry_run_command" in data
        assert data["dry_run_command"] == "make book.go"
    # Even if not available, dry_run_command key should be present (may be None)
    assert "dry_run_command" in data


def test_pmagent_cli_reality_validate_capability_envelope_json_only(tmp_path: Path) -> None:
    """pmagent reality validate-capability-envelope --json-only returns valid JSON."""
    # Create a valid envelope file
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
    file_path = tmp_path / "test_envelope.json"
    file_path.write_text(json.dumps(envelope), encoding="utf-8")

    repo_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pmagent.cli",
            "reality",
            "validate-capability-envelope",
            str(file_path),
            "--json-only",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout.strip())
    assert "ok" in data
    assert "errors" in data
    assert "warnings" in data
    assert "derived_tracking" in data


def test_pmagent_cli_reality_validate_capability_history_json_only() -> None:
    """pmagent reality validate-capability-history --json-only returns valid JSON summary."""
    repo_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pmagent.cli",
            "reality",
            "validate-capability-history",
            "--json-only",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    # Exit code may be 0 or 1 depending on whether there are errors, but JSON should be valid
    assert result.returncode in (0, 1)
    data = json.loads(result.stdout.strip())
    assert "total_files" in data
    assert "ok_count" in data
    assert "error_count" in data
    assert "warning_count" in data
    assert "files_with_errors" in data
    assert "files_with_warnings" in data


def test_list_capability_sessions_empty_directory(tmp_path: Path) -> None:
    """list_capability_sessions should return empty list when directory doesn't exist."""
    evidence_dir = tmp_path / "evidence" / "pmagent"
    # Don't create the directory

    sessions = list_capability_sessions(limit=10, evidence_dir=evidence_dir)
    assert sessions == []


def test_list_capability_sessions_with_envelopes(tmp_path: Path) -> None:
    """list_capability_sessions should return sorted list of session summaries."""
    evidence_dir = tmp_path / "evidence" / "pmagent"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Create two test envelope files
    envelope1 = {
        "type": "capability_session",
        "version": "1.0",
        "id": "NEXT_STEPS:1",
        "title": "First task",
        "source": "NEXT_STEPS",
        "plan": {
            "current_focus": "Phase X",
            "dry_run_command": "make book.go",
        },
        "posture": {
            "mode": "live",
            "reality": {"overall_ok": True},
            "status": {"level": "OK"},
        },
    }
    envelope2 = {
        "type": "capability_session",
        "version": "1.0",
        "id": "NEXT_STEPS:2",
        "title": "Second task",
        "source": "NEXT_STEPS",
        "plan": {
            "current_focus": "Phase Y",
        },
        "posture": {
            "mode": "hermetic",
        },
    }

    file1 = evidence_dir / "capability_session-2025-11-22T01-00-00+00-00.json"
    file2 = evidence_dir / "capability_session-2025-11-22T02-00-00+00-00.json"
    file1.write_text(json.dumps(envelope1), encoding="utf-8")
    file2.write_text(json.dumps(envelope2), encoding="utf-8")

    sessions = list_capability_sessions(limit=10, evidence_dir=evidence_dir)

    assert len(sessions) == 2
    # Should be sorted newest first (file2 is newer)
    assert sessions[0]["id"] == "NEXT_STEPS:2"
    assert sessions[1]["id"] == "NEXT_STEPS:1"

    # Check first session (newest)
    session1 = sessions[0]
    assert session1["id"] == "NEXT_STEPS:2"
    assert session1["title"] == "Second task"
    assert session1["source"] == "NEXT_STEPS"
    assert session1["posture_mode"] == "hermetic"
    assert session1["dry_run_command"] is None

    # Check second session (older)
    session2 = sessions[1]
    assert session2["id"] == "NEXT_STEPS:1"
    assert session2["title"] == "First task"
    assert session2["dry_run_command"] == "make book.go"
    assert session2["posture_mode"] == "live"
    assert session2["reality_overall_ok"] is True
    assert session2["status_level"] == "OK"


def test_pmagent_cli_plan_history_json_only() -> None:
    """pmagent plan history --json-only returns valid JSON summary."""
    repo_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [sys.executable, "-m", "pmagent.cli", "plan", "history", "--limit", "3", "--json-only"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout.strip())
    assert "count" in data
    assert "sessions" in data
    assert isinstance(data["sessions"], list)


def test_pmagent_cli_plan_reality_loop_track_session_disabled() -> None:
    """pmagent plan reality-loop without --track-session should not include tracking block in JSON."""
    repo_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pmagent.cli",
            "plan",
            "reality-loop",
            "--limit",
            "1",
            "--json-only",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    # Exit code 0 expected (even if no candidates, it's advisory)
    assert result.returncode == 0
    data = json.loads(result.stdout.strip())
    assert "available" in data
    # When --track-session is NOT set, tracking block should NOT be present
    # (or if present, it should indicate disabled mode)
    if data.get("available", False) and "tracking" in data:
        # If tracking block exists, it should indicate disabled mode
        tracking = data["tracking"]
        if "tracking" in tracking:
            tracking_info = tracking["tracking"]
            # When disabled, mode should be "disabled" or tracking block should not exist
            assert tracking_info.get("mode") == "disabled" or not tracking_info.get("written", True)


def test_pmagent_cli_plan_reality_loop_track_session_enabled() -> None:
    """pmagent plan reality-loop --track-session should include tracking block in JSON output."""
    repo_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pmagent.cli",
            "plan",
            "reality-loop",
            "--limit",
            "1",
            "--track-session",
            "--json-only",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    # Exit code 0 expected (even if DB-off, it's advisory)
    assert result.returncode == 0
    data = json.loads(result.stdout.strip())
    assert "available" in data
    # If envelope was created, should have tracking block
    if data.get("available", False):
        assert "tracking" in data
        tracking = data["tracking"]
        assert "ok" in tracking
        # Tracking block should have mode (db_on, db_off, disabled, or error)
        if "tracking" in tracking:
            tracking_info = tracking["tracking"]
            assert "mode" in tracking_info
            assert tracking_info["mode"] in ("db_on", "db_off", "disabled", "error")


def test_pmagent_cli_plan_reality_loop_track_session_db_off() -> None:
    """pmagent plan reality-loop --track-session should handle db_off mode gracefully (exit 0)."""
    repo_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pmagent.cli",
            "plan",
            "reality-loop",
            "--limit",
            "1",
            "--track-session",
            "--json-only",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    # Should exit 0 even if DB is off (hermetic behavior)
    assert result.returncode == 0
    data = json.loads(result.stdout.strip())
    # If tracking block exists and mode is db_off, that's valid
    if data.get("available", False) and "tracking" in data:
        tracking = data["tracking"]
        if "tracking" in tracking:
            tracking_info = tracking["tracking"]
            if tracking_info.get("mode") == "db_off":
                # This is expected when DB is unavailable
                assert tracking_info.get("written") is False


def test_pmagent_cli_plan_history_empty() -> None:
    """pmagent plan history handles empty directory gracefully."""
    repo_root = Path(__file__).resolve().parents[3]
    # Use a non-existent directory via env var or just test with existing (may be empty)
    result = subprocess.run(
        [sys.executable, "-m", "pmagent.cli", "plan", "history", "--limit", "3", "--json-only"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout.strip())
    assert "count" in data
    assert "sessions" in data
    assert isinstance(data["sessions"], list)
    # May be empty if no sessions exist, which is fine


def test_pmagent_cli_reality_sessions_json_only() -> None:
    """pmagent reality sessions --json-only should output JSON only."""
    repo_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [sys.executable, "-m", "pmagent.cli", "reality", "sessions", "--limit", "3", "--json-only"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout.strip())
    assert "envelopes" in data
    assert "tracking" in data
    assert "count" in data["envelopes"]
    assert "latest" in data["envelopes"]
    assert "db_mode" in data["tracking"]
    assert "enabled_hint" in data["tracking"]
    # Should not have human-readable output on stderr when --json-only
    assert not result.stderr.strip() or "ERROR" not in result.stderr


def test_pmagent_cli_reality_sessions_human_summary() -> None:
    """pmagent reality sessions should output JSON to stdout and human summary to stderr."""
    repo_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [sys.executable, "-m", "pmagent.cli", "reality", "sessions", "--limit", "3"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # Should have JSON on stdout
    data = json.loads(result.stdout.strip())
    assert "envelopes" in data
    assert "tracking" in data
    # Should have human-readable summary on stderr
    assert result.stderr.strip()
    assert "Sessions:" in result.stderr or "Tracking:" in result.stderr
