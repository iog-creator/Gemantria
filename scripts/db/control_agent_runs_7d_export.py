from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import psycopg

from scripts.config.env import get_rw_dsn


REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "share" / "atlas" / "control_plane"
OUT_PATH = OUT_DIR / "agent_runs_7d.json"


@dataclass
class AgentRuns7dExport:
    schema: str
    generated_at: str
    window_days: int
    since: str
    ok: bool
    connection_ok: bool
    runs: list[dict[str, Any]]
    sessions: list[dict[str, Any]]
    error: str | None = None


def now_utc() -> datetime:
    return datetime.now(UTC)


def now_iso() -> str:
    return now_utc().isoformat()


def db_off_payload(message: str, window_days: int = 7) -> AgentRuns7dExport:
    since_dt = now_utc() - timedelta(days=window_days)
    return AgentRuns7dExport(
        schema="control",
        generated_at=now_iso(),
        window_days=window_days,
        since=since_dt.isoformat(),
        ok=False,
        connection_ok=False,
        runs=[],
        sessions=[],
        error=message,
    )


def fetch_window(window_days: int = 7) -> AgentRuns7dExport:
    dsn = get_rw_dsn()
    since_dt = now_utc() - timedelta(days=window_days)

    try:
        with psycopg.connect(dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Ensure control schema and tables exist; fail-soft if missing.
                cur.execute(
                    """
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'control'
                      AND table_name IN ('agent_run', 'capability_session')
                    """
                )
                rows = cur.fetchall()
                if not rows:
                    return db_off_payload(
                        "control.agent_run / control.capability_session tables not found",
                        window_days=window_days,
                    )

                # Agent runs in the last N days
                cur.execute(
                    """
                    SELECT row_to_json(ar)
                    FROM control.agent_run AS ar
                    WHERE ar.created_at >= %s
                    """,
                    (since_dt,),
                )
                run_rows = cur.fetchall()

                # Capability sessions in the last N days
                cur.execute(
                    """
                    SELECT row_to_json(cs)
                    FROM control.capability_session AS cs
                    WHERE cs.created_at >= %s
                    """,
                    (since_dt,),
                )
                session_rows = cur.fetchall()
    except Exception as exc:  # noqa: BLE001
        return db_off_payload(f"database error: {exc!s}", window_days=window_days)

    runs: list[dict[str, Any]] = []
    for row in run_rows:
        obj = row[0]
        if isinstance(obj, dict):
            runs.append(obj)

    sessions: list[dict[str, Any]] = []
    for row in session_rows:
        obj = row[0]
        if isinstance(obj, dict):
            sessions.append(obj)

    return AgentRuns7dExport(
        schema="control",
        generated_at=now_iso(),
        window_days=window_days,
        since=since_dt.isoformat(),
        ok=True,
        connection_ok=True,
        runs=runs,
        sessions=sessions,
        error=None,
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    export = fetch_window(window_days=7)
    payload = asdict(export)
    OUT_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
