"""Capability Session Envelope Writer

Gated writer path for persisting capability_session envelopes to control.agent_run_cli.
All writes are behind an explicit opt-in flag and gracefully handle DB-off scenarios.

See docs/SSOT/CAPABILITY_SESSION_AI_TRACKING_MAPPING.md for the mapping contract.
"""

from __future__ import annotations

from typing import Any

from pmagent.control_plane import create_agent_run
from scripts.config.env import get_rw_dsn


def maybe_persist_capability_session(
    envelope: dict[str, Any],
    *,
    tracking_enabled: bool,
) -> dict[str, Any]:
    """Optionally persist a capability_session envelope to control.agent_run_cli.

    Hermetic: Returns structured results; no exceptions raised.
    DB-off behavior: Returns {"written": False, "mode": "db_off"} when DB unavailable.

    Args:
        envelope: Capability session envelope dict (from JSON file)
        tracking_enabled: If False, returns immediately with mode="disabled" (no DB calls)

    Returns:
        Result dict with:
        - written: bool (True if row was inserted)
        - mode: str ("disabled" | "db_off" | "db_on" | "error")
        - agent_run_cli_id: str | None (UUID string if written, None otherwise)
        - error: str | None (error message if mode="error")
    """
    # Fast path: tracking disabled
    if not tracking_enabled:
        return {
            "written": False,
            "mode": "disabled",
            "agent_run_cli_id": None,
            "error": None,
        }

    # Check DB availability
    dsn = get_rw_dsn()
    if not dsn:
        return {
            "written": False,
            "mode": "db_off",
            "agent_run_cli_id": None,
            "error": None,
        }

    # Extract command from envelope
    plan = envelope.get("plan", {})
    dry_run_command = plan.get("dry_run_command")
    command = (
        dry_run_command
        if (dry_run_command and isinstance(dry_run_command, str) and dry_run_command.strip())
        else "plan.reality-loop"
    )

    # Prepare request_json (full envelope)
    request_json = envelope

    # Attempt to write to DB
    try:
        agent_run = create_agent_run(command=command, request=request_json)
        if agent_run:
            return {
                "written": True,
                "mode": "db_on",
                "agent_run_cli_id": str(agent_run.id),
                "error": None,
            }
        else:
            # create_agent_run returned None (DB unavailable or error)
            return {
                "written": False,
                "mode": "db_off",
                "agent_run_cli_id": None,
                "error": None,
            }
    except Exception as e:
        # Catch any unexpected exceptions
        return {
            "written": False,
            "mode": "error",
            "agent_run_cli_id": None,
            "error": str(e),
        }
