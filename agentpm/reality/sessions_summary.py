"""Reality Lane: Sessions Summary

Read-only summary of capability_session envelopes and tracking posture.
Hermetic: file-only reads, optional DB reads (gracefully handles DB-off).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from agentpm.plan.next import REPO_ROOT
from scripts.config.env import get_rw_dsn


def _detect_db_mode() -> str:
    """Detect DB mode without side effects (read-only check).

    Returns:
        "db_on" if DSN available, "db_off" otherwise.
    """
    dsn = get_rw_dsn()
    return "db_on" if dsn else "db_off"


def _check_tracking_enabled_hint() -> bool:
    """Check if tracking is enabled (env/flag hint only, no side effects).

    Returns:
        True if PMAGENT_TRACK_SESSIONS=1 or similar env var is set, False otherwise.
    """
    return os.getenv("PMAGENT_TRACK_SESSIONS", "").strip() in ("1", "true", "True", "TRUE")


def summarize_tracked_sessions(
    *,
    limit: int = 20,
    evidence_dir: Path | None = None,
) -> dict[str, Any]:
    """Read capability_session envelopes and return summary.

    Hermetic: file-only reads, optional DB reads (gracefully handles DB-off).
    DB-off behavior: agent_run_cli fields set to None, db_mode="db_off".

    Args:
        limit: Maximum number of latest sessions to include
        evidence_dir: Directory containing capability_session files (defaults to evidence/pmagent/)

    Returns:
        Summary dict with:
        - envelopes: {count, latest: [{id, title, source, dry_run_command, posture_mode, envelope_path, ts}, ...]}
        - tracking: {enabled_hint, db_mode, agent_run_cli: {count, latest_modes} | None}
    """
    evidence_path = evidence_dir or (REPO_ROOT / "evidence" / "pmagent")

    # Enumerate capability_session files
    session_files: list[Path] = []
    if evidence_path.exists():
        session_files = sorted(
            evidence_path.glob("capability_session-*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

    # Read up to limit envelopes
    latest_envelopes: list[dict[str, Any]] = []
    for session_file in session_files[:limit]:
        try:
            envelope_data = json.loads(session_file.read_text(encoding="utf-8"))
            # Extract timestamp from filename (RFC3339 format)
            filename_ts = session_file.stem.replace("capability_session-", "")
            # Fallback to envelope timestamp if available
            envelope_ts = envelope_data.get("timestamp") or filename_ts

            plan = envelope_data.get("plan", {})
            posture = envelope_data.get("posture", {})

            latest_envelopes.append(
                {
                    "id": envelope_data.get("id", ""),
                    "title": envelope_data.get("title", ""),
                    "source": envelope_data.get("source", ""),
                    "dry_run_command": plan.get("dry_run_command"),
                    "posture_mode": posture.get("mode", "unknown"),
                    "envelope_path": str(session_file),
                    "ts": envelope_ts,
                }
            )
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            # Skip invalid files gracefully
            continue

    # Detect DB mode (cheap, read-only)
    db_mode = _detect_db_mode()
    tracking_enabled_hint = _check_tracking_enabled_hint()

    # For now, leave agent_run_cli query as TODO (no new DB queries if not present)
    # Future: could add a read-only helper in control_plane to query agent_run_cli counts
    agent_run_cli: dict[str, Any] | None = None
    if db_mode == "db_on":
        # TODO: Add read-only query helper in control_plane to get:
        # - count of agent_run_cli rows with command like 'plan.reality-loop%'
        # - histogram of modes (db_on/db_off/disabled/error)
        # For now, set to None to indicate query not implemented
        agent_run_cli = None

    return {
        "envelopes": {
            "count": len(session_files),
            "latest": latest_envelopes,
        },
        "tracking": {
            "enabled_hint": tracking_enabled_hint,
            "db_mode": db_mode,
            "agent_run_cli": agent_run_cli,
        },
    }
