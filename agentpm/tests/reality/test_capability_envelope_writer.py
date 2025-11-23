"""Tests for capability_session envelope writer (gated DB persistence)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from agentpm.control_plane import AgentRun
from agentpm.reality.capability_envelope_writer import maybe_persist_capability_session
from agentpm.reality.capability_envelope_validator import validate_and_optionally_persist


def test_maybe_persist_capability_session_disabled_flag() -> None:
    """Test that tracking disabled returns written=False, mode='disabled'."""
    envelope = {
        "type": "capability_session",
        "version": "1.0",
        "id": "NEXT_STEPS:1",
        "title": "Test task",
        "source": "NEXT_STEPS",
        "plan": {"current_focus": "Phase 1", "next_milestone": "M1", "raw_line": "- Task"},
        "posture": {"mode": "live"},
    }

    result = maybe_persist_capability_session(envelope, tracking_enabled=False)

    assert result["written"] is False
    assert result["mode"] == "disabled"
    assert result["agent_run_cli_id"] is None
    assert result["error"] is None


def test_maybe_persist_capability_session_db_off() -> None:
    """Test that DB-off returns written=False, mode='db_off'."""
    envelope = {
        "type": "capability_session",
        "version": "1.0",
        "id": "NEXT_STEPS:1",
        "title": "Test task",
        "source": "NEXT_STEPS",
        "plan": {"current_focus": "Phase 1", "next_milestone": "M1", "raw_line": "- Task"},
        "posture": {"mode": "live"},
    }

    with patch("agentpm.reality.capability_envelope_writer.get_rw_dsn", return_value=None):
        result = maybe_persist_capability_session(envelope, tracking_enabled=True)

    assert result["written"] is False
    assert result["mode"] == "db_off"
    assert result["agent_run_cli_id"] is None
    assert result["error"] is None


def test_maybe_persist_capability_session_db_on_happy_path() -> None:
    """Test that DB-on with valid envelope writes successfully."""
    envelope = {
        "type": "capability_session",
        "version": "1.0",
        "id": "NEXT_STEPS:1",
        "title": "Test task",
        "source": "NEXT_STEPS",
        "plan": {
            "current_focus": "Phase 1",
            "next_milestone": "M1",
            "raw_line": "- Task",
            "dry_run_command": "make book.go",
        },
        "posture": {"mode": "live"},
    }

    # Mock AgentRun instance
    mock_agent_run = MagicMock(spec=AgentRun)
    mock_agent_run.id = "test-uuid-123"

    mock_create_agent_run = MagicMock(return_value=mock_agent_run)

    with patch("agentpm.reality.capability_envelope_writer.get_rw_dsn", return_value="postgresql://test"):
        with patch("agentpm.reality.capability_envelope_writer.create_agent_run", mock_create_agent_run):
            result = maybe_persist_capability_session(envelope, tracking_enabled=True)

    assert result["written"] is True
    assert result["mode"] == "db_on"
    assert result["agent_run_cli_id"] == "test-uuid-123"
    assert result["error"] is None

    # Verify create_agent_run was called with correct command
    mock_create_agent_run.assert_called_once()
    call_args = mock_create_agent_run.call_args
    assert call_args.kwargs["command"] == "make book.go"
    assert call_args.kwargs["request"] == envelope


def test_maybe_persist_capability_session_uses_default_command_when_no_dry_run() -> None:
    """Test that default command 'plan.reality-loop' is used when dry_run_command is missing."""
    envelope = {
        "type": "capability_session",
        "version": "1.0",
        "id": "NEXT_STEPS:1",
        "title": "Test task",
        "source": "NEXT_STEPS",
        "plan": {"current_focus": "Phase 1", "next_milestone": "M1", "raw_line": "- Task"},
        "posture": {"mode": "live"},
    }

    mock_agent_run = MagicMock(spec=AgentRun)
    mock_agent_run.id = "test-uuid-456"

    mock_create_agent_run = MagicMock(return_value=mock_agent_run)

    with patch("agentpm.reality.capability_envelope_writer.get_rw_dsn", return_value="postgresql://test"):
        with patch("agentpm.reality.capability_envelope_writer.create_agent_run", mock_create_agent_run):
            result = maybe_persist_capability_session(envelope, tracking_enabled=True)

    assert result["written"] is True
    assert result["mode"] == "db_on"

    # Verify default command was used
    mock_create_agent_run.assert_called_once()
    call_args = mock_create_agent_run.call_args
    assert call_args.kwargs["command"] == "plan.reality-loop"


def test_maybe_persist_capability_session_handles_create_agent_run_none() -> None:
    """Test that create_agent_run returning None is handled gracefully."""
    envelope = {
        "type": "capability_session",
        "version": "1.0",
        "id": "NEXT_STEPS:1",
        "title": "Test task",
        "source": "NEXT_STEPS",
        "plan": {"current_focus": "Phase 1", "next_milestone": "M1", "raw_line": "- Task"},
        "posture": {"mode": "live"},
    }

    with patch("agentpm.reality.capability_envelope_writer.get_rw_dsn", return_value="postgresql://test"):
        with patch("agentpm.reality.capability_envelope_writer.create_agent_run", return_value=None):
            result = maybe_persist_capability_session(envelope, tracking_enabled=True)

    assert result["written"] is False
    assert result["mode"] == "db_off"
    assert result["agent_run_cli_id"] is None
    assert result["error"] is None


def test_maybe_persist_capability_session_handles_exceptions() -> None:
    """Test that exceptions during DB write are caught and returned as error mode."""
    envelope = {
        "type": "capability_session",
        "version": "1.0",
        "id": "NEXT_STEPS:1",
        "title": "Test task",
        "source": "NEXT_STEPS",
        "plan": {"current_focus": "Phase 1", "next_milestone": "M1", "raw_line": "- Task"},
        "posture": {"mode": "live"},
    }

    with patch("agentpm.reality.capability_envelope_writer.get_rw_dsn", return_value="postgresql://test"):
        with patch(
            "agentpm.reality.capability_envelope_writer.create_agent_run", side_effect=Exception("DB connection failed")
        ):
            result = maybe_persist_capability_session(envelope, tracking_enabled=True)

    assert result["written"] is False
    assert result["mode"] == "error"
    assert result["agent_run_cli_id"] is None
    assert result["error"] == "DB connection failed"


def test_validate_and_optionally_persist_includes_tracking_block_when_enabled_and_ok() -> None:
    """Test that validate_and_optionally_persist includes tracking result when enabled and validation passes."""
    envelope = {
        "type": "capability_session",
        "version": "1.0",
        "id": "NEXT_STEPS:1",
        "title": "Test task",
        "source": "NEXT_STEPS",
        "plan": {
            "current_focus": "Phase 1",
            "next_milestone": "M1",
            "raw_line": "- Task",
            "dry_run_command": "make book.go",
        },
        "posture": {"mode": "live"},
    }

    mock_agent_run = MagicMock(spec=AgentRun)
    mock_agent_run.id = "test-uuid-789"

    with patch("agentpm.reality.capability_envelope_writer.get_rw_dsn", return_value="postgresql://test"):
        with patch("agentpm.reality.capability_envelope_writer.create_agent_run", return_value=mock_agent_run):
            result = validate_and_optionally_persist(envelope, tracking_enabled=True)

    assert result["ok"] is True
    assert "tracking" in result
    assert result["tracking"]["written"] is True
    assert result["tracking"]["mode"] == "db_on"
    assert result["tracking"]["agent_run_cli_id"] == "test-uuid-789"


def test_validate_and_optionally_persist_no_tracking_when_disabled() -> None:
    """Test that validate_and_optionally_persist does not include tracking when disabled."""
    envelope = {
        "type": "capability_session",
        "version": "1.0",
        "id": "NEXT_STEPS:1",
        "title": "Test task",
        "source": "NEXT_STEPS",
        "plan": {"current_focus": "Phase 1", "next_milestone": "M1", "raw_line": "- Task"},
        "posture": {"mode": "live"},
    }

    result = validate_and_optionally_persist(envelope, tracking_enabled=False)

    assert result["ok"] is True
    assert "tracking" not in result


def test_validate_and_optionally_persist_no_tracking_when_validation_fails() -> None:
    """Test that validate_and_optionally_persist does not attempt persistence when validation fails."""
    invalid_envelope = {
        "type": "invalid_type",
        "version": "1.0",
        "id": "NEXT_STEPS:1",
    }

    result = validate_and_optionally_persist(invalid_envelope, tracking_enabled=True)

    assert result["ok"] is False
    assert "tracking" not in result
