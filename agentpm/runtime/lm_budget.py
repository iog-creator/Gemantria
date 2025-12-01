#!/usr/bin/env python3
"""
LM Studio Budget Enforcement

Phase-6 6B: Budget checking for LM Studio usage.
Queries control.lm_usage_budget and recent usage from control.agent_run to enforce
per-app budgets (max_requests and max_tokens within a rolling window).

DB-off safe: Returns True (fail-open) when DB is unavailable to avoid bricking dev.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

try:
    import psycopg
except ImportError:
    psycopg = None

from scripts.config.env import get_rw_dsn

logger = logging.getLogger(__name__)


def _query_usage_for_app(app_name: str, window_days: int) -> tuple[int, int] | None:
    """
    Query recent LM Studio usage for an app from control.agent_run.

    Args:
        app_name: Application identifier
        window_days: Number of days to look back

    Returns:
        Tuple of (request_count, total_tokens) or None if DB unavailable/error
    """
    if psycopg is None:
        return None

    dsn = get_rw_dsn()
    if not dsn:
        return None

    since_dt = datetime.now(UTC) - timedelta(days=window_days)

    try:
        with psycopg.connect(dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Check if tables exist
                cur.execute(
                    """
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'control'
                      AND table_name = 'agent_run'
                    """
                )
                if not cur.fetchone():
                    return None

                # Query usage for this app_name
                # We identify app calls by call_site in result_json or args_json
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
                      )
                    """,
                    (since_dt, f"%{app_name}%", f"%{app_name}%"),
                )
                row = cur.fetchone()
                if row:
                    return (row[0], row[1] or 0)
                return (0, 0)

    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Budget check DB error for {app_name}: {exc!s}")
        return None


def check_lm_budget(app_name: str, tokens: int | None = None) -> bool:
    """
    Check if the app is allowed to make another LM call under configured budgets.

    Phase-6 6B: Returns True if the app is within budget, False if exceeded.

    Behavior:
        - If DB/control-plane is unavailable → return True (fail-open, but log)
        - If no budget row for app_name → return True (no budgets configured)
        - Otherwise:
            * Query recent usage (last N days) from control.agent_run
            * Compare against lm_usage_budget.max_requests / max_tokens
            * Return False if either limit would be exceeded

    Args:
        app_name: Application identifier (e.g., "gemantria.runtime", "storymaker")
        tokens: Estimated tokens for this call (optional, for pre-check)

    Returns:
        True if within budget (or DB unavailable), False if budget exceeded
    """
    if psycopg is None:
        logger.debug(f"Budget check skipped (psycopg unavailable) for {app_name}")
        return True

    dsn = get_rw_dsn()
    if not dsn:
        logger.debug(f"Budget check skipped (DSN unavailable) for {app_name}")
        return True

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
                    # No budget table - allow all (backward compatible)
                    logger.debug(f"Budget table not found, allowing {app_name}")
                    return True

                # Get budget for this app
                cur.execute(
                    """
                    SELECT window_days, max_requests, max_tokens
                    FROM control.lm_usage_budget
                    WHERE app_name = %s
                    """,
                    (app_name,),
                )
                budget_row = cur.fetchone()

                if not budget_row:
                    # No budget configured for this app - allow
                    logger.debug(f"No budget configured for {app_name}, allowing")
                    return True

                window_days, max_requests, max_tokens = budget_row

                # Query current usage
                usage = _query_usage_for_app(app_name, window_days)
                if usage is None:
                    # DB error - fail-open
                    logger.warning(f"Could not query usage for {app_name}, allowing (fail-open)")
                    return True

                used_requests, used_tokens = usage

                # Check request limit
                if used_requests >= max_requests:
                    logger.warning(
                        f"Budget exceeded for {app_name}: {used_requests}/{max_requests} requests"
                    )
                    return False

                # Check token limit (with estimated tokens for this call)
                estimated_tokens = tokens or 0
                if used_tokens + estimated_tokens > max_tokens:
                    logger.warning(
                        f"Budget exceeded for {app_name}: {used_tokens + estimated_tokens}/{max_tokens} tokens"
                    )
                    return False

                # Within budget
                logger.debug(
                    f"Budget OK for {app_name}: {used_requests}/{max_requests} requests, "
                    f"{used_tokens}/{max_tokens} tokens"
                )
                return True

    except Exception as exc:  # noqa: BLE001
        # DB error - fail-open to avoid bricking dev
        logger.warning(f"Budget check error for {app_name}: {exc!s}, allowing (fail-open)")
        return True
