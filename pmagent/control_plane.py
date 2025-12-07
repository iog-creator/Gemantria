#!/usr/bin/env python3
"""
Control Plane - Agent Run CLI Tracking

Tracks pmagent CLI command executions in control.agent_run_cli table.
"""

from __future__ import annotations

import json
from datetime import datetime, UTC
from typing import Any
from uuid import UUID, uuid4

import psycopg
from psycopg.types.json import Json

from scripts.config.env import get_rw_dsn


class AgentRun:
    """Represents a CLI command execution record."""

    def __init__(
        self,
        id: UUID,
        created_at: datetime,
        updated_at: datetime,
        command: str,
        status: str,
        request_json: dict[str, Any] | None = None,
        response_json: dict[str, Any] | None = None,
        error_text: str | None = None,
    ):
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.command = command
        self.status = status
        self.request_json = request_json
        self.response_json = response_json
        self.error_text = error_text


def create_agent_run(command: str, request: dict[str, Any] | None = None) -> AgentRun | None:
    """Create a new agent_run_cli record.

    Args:
        command: Command name (e.g., "system.health", "bible.retrieve").
        request: Optional request parameters as dict.

    Returns:
        AgentRun instance if successful, None if DB unavailable (hermetic behavior).
    """
    dsn = get_rw_dsn()
    if not dsn:
        return None

    try:
        run_id = uuid4()
        now = datetime.now(UTC)

        with psycopg.connect(dsn) as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO control.agent_run_cli
                (id, created_at, updated_at, command, status, request_json)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, created_at, updated_at, command, status, request_json, response_json, error_text
                """,
                (run_id, now, now, command, "started", Json(request) if request else None),
            )
            row = cur.fetchone()
            conn.commit()

            return AgentRun(
                id=row[0],
                created_at=row[1],
                updated_at=row[2],
                command=row[3],
                status=row[4],
                request_json=json.loads(row[5]) if row[5] else None,
                response_json=json.loads(row[6]) if row[6] else None,
                error_text=row[7],
            )
    except Exception:
        # Graceful no-op when DB unavailable (hermetic DB-off behavior)
        return None


def mark_agent_run_success(run: AgentRun | None, response: dict[str, Any] | None = None) -> None:
    """Mark an agent_run_cli record as successful.

    Args:
        run: AgentRun instance (from create_agent_run).
        response: Optional response data as dict.
    """
    if not run:
        return

    dsn = get_rw_dsn()
    if not dsn:
        return

    try:
        now = datetime.now(UTC)
        with psycopg.connect(dsn) as conn, conn.cursor() as cur:
            cur.execute(
                """
                UPDATE control.agent_run_cli
                SET updated_at = %s, status = 'success', response_json = %s
                WHERE id = %s
                """,
                (now, Json(response) if response else None, run.id),
            )
            conn.commit()
    except Exception:
        # Graceful no-op when DB unavailable
        pass


def mark_agent_run_error(run: AgentRun | None, error: Exception | str) -> None:
    """Mark an agent_run_cli record as failed.

    Args:
        run: AgentRun instance (from create_agent_run).
        error: Exception or error message string.
    """
    if not run:
        return

    dsn = get_rw_dsn()
    if not dsn:
        return

    try:
        error_text = str(error) if isinstance(error, str) else f"{type(error).__name__}: {error}"
        now = datetime.now(UTC)
        with psycopg.connect(dsn) as conn, conn.cursor() as cur:
            cur.execute(
                """
                UPDATE control.agent_run_cli
                SET updated_at = %s, status = 'error', error_text = %s
                WHERE id = %s
                """,
                (now, error_text, run.id),
            )
            conn.commit()
    except Exception:
        # Graceful no-op when DB unavailable
        pass
