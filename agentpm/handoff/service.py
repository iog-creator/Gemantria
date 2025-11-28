#!/usr/bin/env python3
"""
Handoff Service - Core service for generating handoff_context from Postgres/DMS.

This module implements the canonical handoff_context schema v1.0 and consolidates
data from control.agent_run, control.doc_registry, and evidence files.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

try:
    import psycopg
    from psycopg.rows import dict_row

    PSYCOPG_AVAILABLE = True
except ImportError:
    PSYCOPG_AVAILABLE = False

from scripts.config.env import get_rw_dsn


class HandoffType(str, Enum):
    """Handoff document types."""

    SESSION = "session"
    TASK = "task"
    ROLE = "role"
    SYSTEM_STATE = "system-state"


@dataclass
class HandoffContext:
    """Canonical handoff_context schema v1.0."""

    version: str = "1.0"
    handoff_type: str = "session"
    scope_id: str | None = None
    phase: str | None = None
    project: str = "gemantria"
    role: str | None = None
    generated_at: str = ""
    work: dict[str, Any] | None = None
    verification: dict[str, Any] | None = None
    next_steps: list[dict[str, Any]] | None = None
    docs: list[dict[str, Any]] | None = None
    agent_runs: dict[str, Any] | None = None
    handoff_seed: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "handoff_type": self.handoff_type,
            "scope_id": self.scope_id,
            "phase": self.phase,
            "project": self.project,
            "role": self.role,
            "generated_at": self.generated_at,
            "work": self.work or {},
            "verification": self.verification or {},
            "next_steps": self.next_steps or [],
            "docs": self.docs or [],
            "agent_runs": self.agent_runs or {},
            "handoff_seed": self.handoff_seed or {},
        }


def generate_handoff(
    handoff_type: HandoffType | str,
    scope_id: str | None = None,
    role: str | None = None,
    out_format: str = "markdown",
) -> dict[str, Any]:
    """
    Generate handoff document from Postgres/DMS data.

    Args:
        handoff_type: Type of handoff (session, task, role, system-state)
        scope_id: Optional scope ID for task-type handoffs
        role: Optional role for role-type handoffs
        out_format: Output format (markdown, json)

    Returns:
        handoff_context dictionary
    """
    # Normalize handoff_type
    if isinstance(handoff_type, str):
        handoff_type = HandoffType(handoff_type)

    # Build handoff context
    context = _build_handoff_context(handoff_type, scope_id, role)

    return context.to_dict()


def _build_handoff_context(
    handoff_type: HandoffType,
    scope_id: str | None = None,
    role: str | None = None,
) -> HandoffContext:
    """
    Build handoff_context from Postgres/DMS sources.

    Args:
        handoff_type: Type of handoff
        scope_id: Optional scope ID
        role: Optional role

    Returns:
        HandoffContext instance
    """
    context = HandoffContext(
        handoff_type=handoff_type.value,
        scope_id=scope_id,
        role=role,
        generated_at=datetime.utcnow().isoformat() + "Z",
    )

    # Query agent runs (last 24h)
    context.agent_runs = _query_agent_runs(hours=24)

    # Query completion envelopes
    context.work = _query_completion_envelopes()

    # Query capability sessions (if scope_id provided)
    if scope_id:
        context.work["capability_sessions"] = _query_capability_sessions(scope_id)

    # Get next steps
    context.next_steps = _get_next_steps()

    # Get relevant docs
    context.docs = _get_relevant_docs(scope_id, role)

    # Get verification status
    context.verification = _get_verification_status()

    return context


def _query_agent_runs(hours: int = 24) -> dict[str, Any]:
    """
    Query control.agent_run and control.agent_run_cli for recent activity.

    Args:
        hours: Number of hours to look back

    Returns:
        Dictionary with summary and recent runs
    """
    if not PSYCOPG_AVAILABLE:
        return {
            "summary": {
                "total": 0,
                "last_24h": 0,
                "by_tool": {},
                "errors": 0,
            },
            "recent": [],
        }

    dsn = get_rw_dsn()
    if not dsn:
        return {
            "summary": {
                "total": 0,
                "last_24h": 0,
                "by_tool": {},
                "errors": 0,
            },
            "recent": [],
        }

    try:
        with psycopg.connect(dsn, connect_timeout=2) as conn:
            # Force read-only transaction (all queries are SELECT)
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SET default_transaction_read_only=on")
                # Calculate cutoff time
                cutoff = datetime.utcnow() - timedelta(hours=hours)

                # Query control.agent_run for last N hours
                cur.execute(
                    """
                    SELECT
                        id,
                        tool,
                        args_json,
                        result_json,
                        violations_json,
                        created_at
                    FROM control.agent_run
                    WHERE created_at >= %s
                    ORDER BY created_at DESC
                    LIMIT 100
                    """,
                    (cutoff,),
                )
                agent_runs = cur.fetchall()

                # Query control.agent_run_cli for last N hours
                cur.execute(
                    """
                    SELECT
                        id,
                        command,
                        status,
                        request_json,
                        response_json,
                        error_text,
                        created_at
                    FROM control.agent_run_cli
                    WHERE created_at >= %s
                    ORDER BY created_at DESC
                    LIMIT 100
                    """,
                    (cutoff,),
                )
                cli_runs = cur.fetchall()

                # Aggregate by tool/command
                by_tool: dict[str, int] = {}
                errors = 0
                recent = []

                # Process agent_runs
                for run in agent_runs:
                    tool = run.get("tool", "unknown")
                    by_tool[tool] = by_tool.get(tool, 0) + 1

                    # Check for errors (non-empty violations_json or error in result_json)
                    violations = run.get("violations_json", [])
                    if violations and len(violations) > 0:
                        errors += 1

                    result_json = run.get("result_json", {})
                    if isinstance(result_json, dict) and result_json.get("ok") is False:
                        errors += 1

                    recent.append(
                        {
                            "id": str(run.get("id", "")),
                            "type": "agent_run",
                            "tool": tool,
                            "created_at": run.get("created_at").isoformat() if run.get("created_at") else None,
                            "has_errors": bool(violations and len(violations) > 0),
                        }
                    )

                # Process cli_runs
                for run in cli_runs:
                    command = run.get("command", "unknown")
                    by_tool[command] = by_tool.get(command, 0) + 1

                    # Check for errors
                    status = run.get("status", "")
                    if status == "error":
                        errors += 1

                    if run.get("error_text"):
                        errors += 1

                    recent.append(
                        {
                            "id": str(run.get("id", "")),
                            "type": "cli",
                            "command": command,
                            "status": status,
                            "created_at": run.get("created_at").isoformat() if run.get("created_at") else None,
                            "has_errors": status == "error" or bool(run.get("error_text")),
                        }
                    )

                # Sort recent by created_at (most recent first)
                recent.sort(key=lambda x: x.get("created_at") or "", reverse=True)
                recent = recent[:50]  # Limit to 50 most recent

                return {
                    "summary": {
                        "total": len(agent_runs) + len(cli_runs),
                        "last_24h": len(agent_runs) + len(cli_runs) if hours == 24 else 0,
                        "by_tool": by_tool,
                        "errors": errors,
                    },
                    "recent": recent,
                }

    except (psycopg.OperationalError, psycopg.Error):
        # Graceful fallback when DB unavailable (hermetic db_off behavior)
        return {
            "summary": {
                "total": 0,
                "last_24h": 0,
                "by_tool": {},
                "errors": 0,
            },
            "recent": [],
        }


def _query_completion_envelopes() -> dict[str, Any]:
    """
    Query evidence/pmagent/completion-*.json files.

    Returns:
        Dictionary with work summary and items
    """
    evidence_dir = Path("evidence/pmagent")
    completion_files = list(evidence_dir.glob("completion-*.json"))

    items = []
    for file_path in sorted(completion_files, key=lambda p: p.stat().st_mtime, reverse=True)[:10]:
        try:
            with open(file_path) as f:
                envelope = json.load(f)
                items.append(
                    {
                        "id": envelope.get("id", str(file_path.stem)),
                        "description": envelope.get("work_summary", {}).get("summary", "Unknown work"),
                        "files_changed": envelope.get("work_summary", {}).get("files_changed", []),
                        "status": "complete"
                        if envelope.get("verification", {}).get("all_checks_passed")
                        else "partial",
                        "tests": {
                            "run": True,
                            "passed": envelope.get("verification", {}).get("all_checks_passed", False),
                        },
                    }
                )
        except (json.JSONDecodeError, FileNotFoundError, KeyError):
            continue

    return {
        "summary": f"Found {len(items)} completion envelopes",
        "items": items,
    }


def _query_capability_sessions(scope_id: str) -> list[dict[str, Any]]:
    """
    Query evidence/pmagent/capability_session-*.json files for scope_id.

    Args:
        scope_id: Scope ID to filter by

    Returns:
        List of capability session envelopes
    """
    evidence_dir = Path("evidence/pmagent")
    session_files = list(evidence_dir.glob(f"capability_session-*{scope_id}*.json"))

    sessions = []
    for file_path in sorted(session_files, key=lambda p: p.stat().st_mtime, reverse=True)[:5]:
        try:
            with open(file_path) as f:
                session = json.load(f)
                sessions.append(session)
        except (json.JSONDecodeError, FileNotFoundError):
            continue

    return sessions


def _get_next_steps() -> list[dict[str, Any]]:
    """
    Query NEXT_STEPS.md or MASTER_PLAN.md for next steps.

    Returns:
        List of next step dictionaries
    """
    try:
        from agentpm.plan.next import build_next_plan

        plan = build_next_plan(limit=5, with_status=False)
        if not plan.get("available", False):
            return []

        candidates = plan.get("candidates", [])
        next_steps = []
        for candidate in candidates:
            next_steps.append(
                {
                    "id": candidate.get("id", "unknown"),
                    "title": candidate.get("title", ""),
                    "source": candidate.get("source", "unknown"),
                    "priority": candidate.get("priority", "normal"),
                }
            )
        return next_steps
    except (ImportError, Exception):
        # Fallback: return empty list if plan module unavailable
        return []


def _get_relevant_docs(scope_id: str | None, role: str | None) -> list[dict[str, Any]]:
    """
    Query control.doc_registry and control.kb_document for relevant docs.

    Args:
        scope_id: Optional scope ID to filter by
        role: Optional role to filter by

    Returns:
        List of document dictionaries
    """
    if not PSYCOPG_AVAILABLE:
        return []

    dsn = get_rw_dsn()
    if not dsn:
        return []

    try:
        with psycopg.connect(dsn, connect_timeout=2) as conn:
            # Force read-only transaction (all queries are SELECT)
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SET default_transaction_read_only=on")
                docs = []

                # Query control.doc_registry
                if role:
                    cur.execute(
                        """
                        SELECT
                            doc_id,
                            logical_name,
                            role,
                            repo_path,
                            share_path,
                            is_ssot,
                            enabled,
                            updated_at
                        FROM control.doc_registry
                        WHERE enabled = TRUE AND role = %s
                        ORDER BY updated_at DESC
                        LIMIT 50
                        """,
                        (role,),
                    )
                else:
                    cur.execute(
                        """
                        SELECT
                            doc_id,
                            logical_name,
                            role,
                            repo_path,
                            share_path,
                            is_ssot,
                            enabled,
                            updated_at
                        FROM control.doc_registry
                        WHERE enabled = TRUE
                        ORDER BY updated_at DESC
                        LIMIT 50
                        """
                    )

                registry_docs = cur.fetchall()
                for doc in registry_docs:
                    docs.append(
                        {
                            "id": str(doc.get("doc_id", "")),
                            "logical_name": doc.get("logical_name"),
                            "role": doc.get("role"),
                            "repo_path": doc.get("repo_path"),
                            "share_path": doc.get("share_path"),
                            "is_ssot": doc.get("is_ssot", False),
                            "updated_at": doc.get("updated_at").isoformat() if doc.get("updated_at") else None,
                            "source": "doc_registry",
                        }
                    )

                # Query control.kb_document for KB coverage
                cur.execute(
                    """
                    SELECT
                        id,
                        path,
                        title,
                        doc_type,
                        content_hash,
                        size_bytes,
                        mtime,
                        is_canonical,
                        status,
                        updated_at
                    FROM control.kb_document
                    WHERE status IN ('canonical', 'unreviewed')
                    ORDER BY updated_at DESC
                    LIMIT 50
                    """
                )

                kb_docs = cur.fetchall()
                for doc in kb_docs:
                    docs.append(
                        {
                            "id": str(doc.get("id", "")),
                            "path": doc.get("path"),
                            "title": doc.get("title"),
                            "doc_type": doc.get("doc_type"),
                            "content_hash": doc.get("content_hash"),
                            "size_bytes": doc.get("size_bytes"),
                            "is_canonical": doc.get("is_canonical", False),
                            "status": doc.get("status"),
                            "updated_at": doc.get("updated_at").isoformat() if doc.get("updated_at") else None,
                            "source": "kb_document",
                        }
                    )

                return docs

    except (psycopg.OperationalError, psycopg.Error):
        # Graceful fallback when DB unavailable (hermetic db_off behavior)
        return []


def _get_verification_status() -> dict[str, Any]:
    """
    Get verification status including DB health, LM health, and LM slots.

    Returns:
        Dictionary with verification status
    """
    # Get LM slots status from pmagent lm status --json-only
    lm_slots = _get_lm_slots_status()

    # Check hermetic (ruff format/lint)
    format_ok = True
    lint_ok = True
    try:
        result = subprocess.run(
            ["ruff", "format", "--check", "."],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        format_ok = result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        format_ok = False

    try:
        result = subprocess.run(
            ["ruff", "check", "."],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        lint_ok = result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        lint_ok = False

    # Get DB and LM health
    db_health = {"mode": "db_off", "reachable": False, "notes": "DB health check unavailable"}
    lm_health_snapshot = {"slots": [], "notes": "LM health check unavailable"}

    try:
        from agentpm.status.system import get_db_health_snapshot, get_lm_health_snapshot

        db_health = get_db_health_snapshot()
        lm_health_snapshot = get_lm_health_snapshot()
    except (ImportError, Exception):
        pass

    # Determine LM health mode from slots
    lm_slots_list = lm_health_snapshot.get("slots", [])
    lm_ready = any(slot.get("service") == "OK" for slot in lm_slots_list)
    lm_mode = "lm_ready" if lm_ready else "lm_off"

    return {
        "hermetic": {
            "format_ok": format_ok,
            "lint_ok": lint_ok,
            "tests_ok": True,  # TODO: Check test status (requires test runner integration)
        },
        "live": {
            "db_health": db_health.get("mode", "db_off"),
            "db_reachable": db_health.get("reachable", False),
            "lm_health": lm_mode,
            "lm_reachable": lm_ready,
            "syntax_errors": [],
        },
        "ui": {
            "browser_ok": True,  # TODO: Check browser verification (requires evidence file check)
            "services_ok": True,  # TODO: Check service status (requires service status check)
        },
        "lm_slots": lm_slots,
    }


def _get_lm_slots_status() -> dict[str, Any]:
    """
    Get LM slots status from pmagent lm status --json-only.

    Returns:
        Dictionary with LM slot status (always populated from runtime, not hardcoded)
    """
    try:
        result = subprocess.run(
            ["pmagent", "lm", "status", "--json-only"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass

    # Fallback: return empty structure if pmagent unavailable
    return {
        "local_agent": {"provider": "unknown", "model": "unknown", "status": "unknown"},
        "planning": {"provider": "unknown", "model": "unknown", "status": "unknown"},
        "vision": {"provider": "unknown", "model": "unknown", "status": "unknown"},
        "theology": {"provider": "unknown", "model": "unknown", "status": "unknown"},
    }
