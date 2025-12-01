#!/usr/bin/env python3
"""
Planning Lane Status Export for PM Share Package

Exports planning provider/model/last_run metadata from:
- control.agent_run_cli (for planning commands: tools.plan, tools.gemini, tools.codex)
- control.tool_catalog (for planning tools registered in MCP)

Uses centralized DSN loader (never os.getenv directly).
Tolerates empty/nonexistent DB (exits 0, writes empty export for CI tolerance).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.config.env import get_rw_dsn

try:
    import psycopg
except ImportError:
    psycopg = None

OUT_DIR = REPO / "share"
OUT_FILE = OUT_DIR / "planning_lane_status.json"

PLANNING_COMMANDS = ["tools.plan", "tools.gemini", "tools.codex"]


def now_iso() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now(UTC).isoformat()


def db_off_export(error: str) -> dict[str, Any]:
    """Generate empty export for DB-off scenarios."""
    return {
        "schema": "planning_lane_status.v1",
        "generated_at": now_iso(),
        "providers": [],
        "tools": [],
        "last_runs": [],
        "db_off": True,
        "error": error,
    }


def export_planning_lane_status(conn: psycopg.Connection) -> dict[str, Any]:
    """Export planning lane status."""
    with conn.cursor() as cur:
        # Get planning command runs from agent_run_cli
        cur.execute(
            """
            SELECT
                command,
                request_json,
                response_json,
                status,
                created_at
            FROM control.agent_run_cli
            WHERE command = ANY(%s)
            ORDER BY created_at DESC
            """,
            (PLANNING_COMMANDS,),
        )
        planning_runs = cur.fetchall()

        # Get all tools from tool_catalog (planning tools identified by name pattern)
        cur.execute(
            """
            SELECT
                name,
                ring,
                io_schema,
                enabled,
                created_at
            FROM control.tool_catalog
            WHERE name LIKE '%planning%' OR name LIKE '%gemini%' OR name LIKE '%codex%'
            ORDER BY name
            """
        )
        planning_tools = cur.fetchall()

    # Process providers from runs
    providers: dict[str, dict[str, Any]] = {}
    last_runs: list[dict[str, Any]] = []

    for run in planning_runs:
        command, request_json, _response_json, status, created_at = run
        provider = command.replace("tools.", "")

        if provider not in providers:
            providers[provider] = {
                "provider": provider,
                "last_run": None,
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "model": None,
            }

        providers[provider]["total_runs"] += 1
        if status == "success":
            providers[provider]["successful_runs"] += 1
        elif status == "error":
            providers[provider]["failed_runs"] += 1

        last_run_str = providers[provider]["last_run"]
        if last_run_str:
            last_run_dt = datetime.fromisoformat(last_run_str.replace("Z", "+00:00"))
        else:
            last_run_dt = None
        if last_run_dt is None or (created_at and created_at > last_run_dt):
            providers[provider]["last_run"] = created_at.isoformat() if created_at else None

        # Extract model from request_json if available
        if request_json and isinstance(request_json, dict):
            model = request_json.get("model") or request_json.get("PLANNING_MODEL")
            if model and not providers[provider]["model"]:
                providers[provider]["model"] = model

        # Add to last_runs list
        last_runs.append(
            {
                "provider": provider,
                "command": command,
                "status": status,
                "created_at": created_at.isoformat() if created_at else None,
                "model": request_json.get("model") if isinstance(request_json, dict) else None,
            }
        )

    # Process tools
    tools = []
    for tool in planning_tools:
        tool_name, ring, io_schema, enabled, created_at = tool
        tools.append(
            {
                "tool": tool_name,
                "ring": ring,
                "io_schema": io_schema if isinstance(io_schema, dict) else {},
                "enabled": enabled,
                "created_at": created_at.isoformat() if created_at else None,
            }
        )

    return {
        "schema": "planning_lane_status.v1",
        "generated_at": now_iso(),
        "providers": sorted(providers.values(), key=lambda x: x["provider"]),
        "tools": tools,
        "last_runs": sorted(last_runs, key=lambda x: x["created_at"] or "", reverse=True)[
            :10
        ],  # Last 10 runs
        "db_off": False,
    }


def main() -> int:
    """Main entrypoint."""
    # Ensure output directory exists
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if psycopg is None:
        print(
            "WARN: psycopg not available; writing empty export (CI empty-DB tolerance).",
            file=sys.stderr,
        )
        export_data = db_off_export("psycopg not available")
        OUT_FILE.write_text(
            json.dumps(export_data, indent=2, default=str),
            encoding="utf-8",
        )
        return 0

    dsn = get_rw_dsn()
    if not dsn:
        print("SKIP: GEMATRIA_DSN not set (empty-DB tolerance).", file=sys.stderr)
        export_data = db_off_export("DSN not set")
        OUT_FILE.write_text(
            json.dumps(export_data, indent=2, default=str),
            encoding="utf-8",
        )
        return 0

    try:
        with psycopg.connect(dsn) as conn:
            export_data = export_planning_lane_status(conn)
            OUT_FILE.write_text(
                json.dumps(export_data, indent=2, default=str),
                encoding="utf-8",
            )
            print(
                f"✅ Exported planning lane status: {len(export_data['providers'])} providers, "
                f"{len(export_data['tools'])} tools"
            )
    except Exception as exc:
        print(f"ERROR: Failed to export planning lane status: {exc}", file=sys.stderr)
        export_data = db_off_export(f"database error: {exc!s}")
        OUT_FILE.write_text(
            json.dumps(export_data, indent=2, default=str),
            encoding="utf-8",
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
