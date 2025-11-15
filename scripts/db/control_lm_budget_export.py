#!/usr/bin/env python3
"""
LM Studio Budget Export for Atlas

Phase-6 6B: Exports LM Studio budget status from control.lm_usage_budget and control.agent_run
to share/atlas/control_plane/lm_budget_7d.json for Atlas visualization.

Tolerates db_off (no DB required; best-effort empty exports).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

try:
    import psycopg
except ImportError:
    psycopg = None

from scripts.config.env import get_rw_dsn


REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "share" / "atlas" / "control_plane"
OUT_BUDGET_PATH = OUT_DIR / "lm_budget_7d.json"


@dataclass
class LMBudget7dItem:
    app_name: str
    window_days: int
    max_requests: int
    max_tokens: int
    used_requests: int
    used_tokens: int
    status: str  # "ok" | "near_limit" | "over_limit"
    generated_at: str


@dataclass
class LMBudget7dExport:
    schema: str
    generated_at: str
    ok: bool
    connection_ok: bool
    budgets: list[LMBudget7dItem]
    error: str | None = None


def now_utc() -> datetime:
    return datetime.now(UTC)


def now_iso() -> str:
    return now_utc().isoformat()


def db_off_budget_payload(message: str) -> LMBudget7dExport:
    return LMBudget7dExport(
        schema="control",
        generated_at=now_iso(),
        ok=False,
        connection_ok=False,
        budgets=[],
        error=message,
    )


def _get_output_path() -> Path:
    """Get output path for budget export (for testing)."""
    return OUT_BUDGET_PATH


def fetch_budget_status(window_days: int = 7) -> LMBudget7dExport:
    """Fetch LM Studio budget status from control.lm_usage_budget and control.agent_run."""
    if psycopg is None:
        return db_off_budget_payload("psycopg not available")

    dsn = get_rw_dsn()
    if not dsn:
        return db_off_budget_payload("GEMATRIA_DSN not set")

    since_dt = now_utc() - timedelta(days=window_days)

    try:
        with psycopg.connect(dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Check if budget table exists
                cur.execute(
                    """
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'control'
                      AND table_name = 'lm_usage_budget'
                    """
                )
                if not cur.fetchone():
                    # No budget table - return empty list (backward compatible)
                    return LMBudget7dExport(
                        schema="control",
                        generated_at=now_iso(),
                        ok=True,
                        connection_ok=True,
                        budgets=[],
                        error=None,
                    )

                # Get all budgets
                cur.execute(
                    """
                    SELECT app_name, window_days, max_requests, max_tokens
                    FROM control.lm_usage_budget
                    """
                )
                budget_rows = cur.fetchall()

                if not budget_rows:
                    # No budgets configured
                    return LMBudget7dExport(
                        schema="control",
                        generated_at=now_iso(),
                        ok=True,
                        connection_ok=True,
                        budgets=[],
                        error=None,
                    )

                # Check if agent_run table exists
                cur.execute(
                    """
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'control'
                      AND table_name = 'agent_run'
                    """
                )
                agent_run_exists = cur.fetchone() is not None

                budgets: list[LMBudget7dItem] = []

                for app_name, budget_window_days, max_requests, max_tokens in budget_rows:
                    # Use budget's window_days, not the function parameter
                    app_since_dt = now_utc() - timedelta(days=budget_window_days)

                    used_requests = 0
                    used_tokens = 0

                    if agent_run_exists:
                        # Query usage for this app
                        cur.execute(
                            """
                            SELECT
                                COUNT(*)::int as request_count,
                                COALESCE(
                                    SUM(
                                        (result_json->'usage'->>'prompt_tokens')::int +
                                        (result_json->'usage'->>'completion_tokens')::int
                                    ),
                                    0
                                )::int as total_tokens
                            FROM control.agent_run
                            WHERE tool = 'lm_studio'
                              AND created_at >= %s
                              AND (
                                  result_json->>'call_site' LIKE %s
                                  OR args_json->>'call_site' LIKE %s
                                  OR args_json->>'app_name' = %s
                              )
                            """,
                            (app_since_dt, f"%{app_name}%", f"%{app_name}%", app_name),
                        )
                        usage_row = cur.fetchone()
                        if usage_row:
                            used_requests, used_tokens = usage_row[0], usage_row[1] or 0

                    # Determine status
                    requests_pct = (used_requests / max_requests * 100) if max_requests > 0 else 0
                    tokens_pct = (used_tokens / max_tokens * 100) if max_tokens > 0 else 0

                    if used_requests >= max_requests or used_tokens >= max_tokens:
                        status = "over_limit"
                    elif requests_pct >= 80 or tokens_pct >= 80:
                        status = "near_limit"
                    else:
                        status = "ok"

                    budgets.append(
                        LMBudget7dItem(
                            app_name=app_name,
                            window_days=budget_window_days,
                            max_requests=max_requests,
                            max_tokens=max_tokens,
                            used_requests=used_requests,
                            used_tokens=used_tokens,
                            status=status,
                            generated_at=now_iso(),
                        )
                    )

                return LMBudget7dExport(
                    schema="control",
                    generated_at=now_iso(),
                    ok=True,
                    connection_ok=True,
                    budgets=budgets,
                    error=None,
                )

    except Exception as exc:  # noqa: BLE001
        return db_off_budget_payload(f"database error: {exc!s}")


def main() -> None:
    """Export LM budget status to JSON file."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    budget_export = fetch_budget_status(window_days=7)

    # Convert to dict for JSON serialization
    export_dict: dict[str, Any] = {
        "schema": budget_export.schema,
        "generated_at": budget_export.generated_at,
        "ok": budget_export.ok,
        "connection_ok": budget_export.connection_ok,
        "budgets": [asdict(budget) for budget in budget_export.budgets],
    }
    if budget_export.error:
        export_dict["error"] = budget_export.error

    OUT_BUDGET_PATH.write_text(
        json.dumps(export_dict, indent=2, sort_keys=True),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
