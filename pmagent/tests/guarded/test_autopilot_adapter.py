"""Tests for Autopilot Guarded Tool Adapter."""

from __future__ import annotations

from pmagent.guarded.autopilot_adapter import map_intent_to_command


def test_map_intent_to_command_status() -> None:
    """Test mapping 'status' intent to command."""
    result = map_intent_to_command("status")
    assert result == "pmagent status explain"


def test_map_intent_to_command_health() -> None:
    """Test mapping 'health' intent to command."""
    result = map_intent_to_command("health")
    assert result == "pmagent health system"


def test_map_intent_to_command_plan() -> None:
    """Test mapping 'plan' intent to command."""
    result = map_intent_to_command("plan")
    assert result == "pmagent plan next"


def test_map_intent_to_command_case_insensitive() -> None:
    """Test that intent mapping is case-insensitive."""
    assert map_intent_to_command("STATUS") == "pmagent status explain"
    assert map_intent_to_command("Health") == "pmagent health system"
    assert map_intent_to_command("  plan  ") == "pmagent plan next"


def test_map_intent_to_command_unknown() -> None:
    """Test that unknown intents return None."""
    assert map_intent_to_command("unknown") is None
    assert map_intent_to_command("delete") is None
    assert map_intent_to_command("rm -rf") is None
    assert map_intent_to_command("") is None


def test_map_intent_to_command_whitespace_handling() -> None:
    """Test that whitespace is properly stripped."""
    assert map_intent_to_command("  status  ") == "pmagent status explain"
    assert map_intent_to_command("\tstatus\n") == "pmagent status explain"
