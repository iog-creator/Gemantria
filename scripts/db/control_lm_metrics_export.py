#!/usr/bin/env python3
"""
LM Studio Metrics Export for Atlas

Phase-3D D1: Exports LM Studio usage and health metrics from control.agent_run
to share/atlas/control_plane/ for Atlas visualization.

Tolerates db_off and LM-off (no DB or LM Studio required; best-effort empty exports).
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
OUT_USAGE_PATH = OUT_DIR / "lm_usage_7d.json"
OUT_HEALTH_PATH = OUT_DIR / "lm_health_7d.json"


@dataclass
class LMUsage7dExport:
    schema: str
    generated_at: str
    window_days: int
    since: str
    ok: bool
    connection_ok: bool
    total_calls: int
    successful_calls: int
    failed_calls: int
    total_tokens_prompt: int
    total_tokens_completion: int
    total_latency_ms: int
    avg_latency_ms: float
    calls_by_day: list[dict[str, Any]]
    error: str | None = None


@dataclass
class LMHealth7dExport:
    schema: str
    generated_at: str
    window_days: int
    since: str
    ok: bool
    connection_ok: bool
    health_score: float
    success_rate: float
    avg_latency_ms: float
    error_rate: float
    error_types: dict[str, int]
    recent_errors: list[dict[str, Any]]
    error: str | None = None


def now_utc() -> datetime:
    return datetime.now(UTC)


def now_iso() -> str:
    return now_utc().isoformat()


def db_off_usage_payload(message: str, window_days: int = 7) -> LMUsage7dExport:
    since_dt = now_utc() - timedelta(days=window_days)
    return LMUsage7dExport(
        schema="control",
        generated_at=now_iso(),
        window_days=window_days,
        since=since_dt.isoformat(),
        ok=False,
        connection_ok=False,
        total_calls=0,
        successful_calls=0,
        failed_calls=0,
        total_tokens_prompt=0,
        total_tokens_completion=0,
        total_latency_ms=0,
        avg_latency_ms=0.0,
        calls_by_day=[],
        error=message,
    )


def db_off_health_payload(message: str, window_days: int = 7) -> LMHealth7dExport:
    since_dt = now_utc() - timedelta(days=window_days)
    return LMHealth7dExport(
        schema="control",
        generated_at=now_iso(),
        window_days=window_days,
        since=since_dt.isoformat(),
        ok=False,
        connection_ok=False,
        health_score=0.0,
        success_rate=0.0,
        avg_latency_ms=0.0,
        error_rate=1.0,
        error_types={},
        recent_errors=[],
        error=message,
    )


def fetch_lm_usage(window_days: int = 7) -> LMUsage7dExport:
    """Fetch LM Studio usage metrics from control.agent_run for the last N days."""
    if psycopg is None:
        return db_off_usage_payload("psycopg not available", window_days=window_days)

    dsn = get_rw_dsn()
    if not dsn:
        return db_off_usage_payload("GEMATRIA_DSN not set", window_days=window_days)

    since_dt = now_utc() - timedelta(days=window_days)

    try:
        with psycopg.connect(dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Check if control.agent_run table exists
                cur.execute(
                    """
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'control'
                      AND table_name = 'agent_run'
                    """
                )
                if not cur.fetchone():
                    return db_off_usage_payload(
                        "control.agent_run table not found",
                        window_days=window_days,
                    )

                # Fetch LM Studio calls (tool='lm_studio')
                cur.execute(
                    """
                    SELECT
                        created_at,
                        result_json->>'ok' as ok,
                        result_json->>'latency_ms' as latency_ms,
                        result_json->'usage'->>'prompt_tokens' as prompt_tokens,
                        result_json->'usage'->>'completion_tokens' as completion_tokens
                    FROM control.agent_run
                    WHERE tool = 'lm_studio'
                      AND created_at >= %s
                    ORDER BY created_at ASC
                    """,
                    (since_dt,),
                )
                rows = cur.fetchall()

    except Exception as exc:  # noqa: BLE001
        return db_off_usage_payload(f"database error: {exc!s}", window_days=window_days)

    # Process rows
    total_calls = len(rows)
    successful_calls = 0
    failed_calls = 0
    total_tokens_prompt = 0
    total_tokens_completion = 0
    total_latency_ms = 0

    # Group by day
    calls_by_day_map: dict[str, dict[str, Any]] = {}
    for row in rows:
        created_at, ok_str, latency_ms_str, prompt_tokens_str, completion_tokens_str = row
        day_key = created_at.date().isoformat()

        if day_key not in calls_by_day_map:
            calls_by_day_map[day_key] = {
                "date": day_key,
                "calls": 0,
                "successful": 0,
                "failed": 0,
                "tokens_prompt": 0,
                "tokens_completion": 0,
                "latency_ms": 0,
            }

        day_data = calls_by_day_map[day_key]
        day_data["calls"] += 1

        is_ok = ok_str == "true" if ok_str else False
        if is_ok:
            successful_calls += 1
            day_data["successful"] += 1
        else:
            failed_calls += 1
            day_data["failed"] += 1

        if latency_ms_str:
            try:
                latency = int(latency_ms_str)
                total_latency_ms += latency
                day_data["latency_ms"] += latency
            except (ValueError, TypeError):
                pass

        if prompt_tokens_str:
            try:
                tokens = int(prompt_tokens_str)
                total_tokens_prompt += tokens
                day_data["tokens_prompt"] += tokens
            except (ValueError, TypeError):
                pass

        if completion_tokens_str:
            try:
                tokens = int(completion_tokens_str)
                total_tokens_completion += tokens
                day_data["tokens_completion"] += tokens
            except (ValueError, TypeError):
                pass

    calls_by_day = sorted(calls_by_day_map.values(), key=lambda x: x["date"])

    avg_latency_ms = total_latency_ms / total_calls if total_calls > 0 else 0.0

    return LMUsage7dExport(
        schema="control",
        generated_at=now_iso(),
        window_days=window_days,
        since=since_dt.isoformat(),
        ok=True,
        connection_ok=True,
        total_calls=total_calls,
        successful_calls=successful_calls,
        failed_calls=failed_calls,
        total_tokens_prompt=total_tokens_prompt,
        total_tokens_completion=total_tokens_completion,
        total_latency_ms=total_latency_ms,
        avg_latency_ms=avg_latency_ms,
        calls_by_day=calls_by_day,
        error=None,
    )


def fetch_lm_health(window_days: int = 7) -> LMHealth7dExport:
    """Fetch LM Studio health metrics from control.agent_run for the last N days."""
    if psycopg is None:
        return db_off_health_payload("psycopg not available", window_days=window_days)

    dsn = get_rw_dsn()
    if not dsn:
        return db_off_health_payload("GEMATRIA_DSN not set", window_days=window_days)

    since_dt = now_utc() - timedelta(days=window_days)

    try:
        with psycopg.connect(dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Check if control.agent_run table exists
                cur.execute(
                    """
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'control'
                      AND table_name = 'agent_run'
                    """
                )
                if not cur.fetchone():
                    return db_off_health_payload(
                        "control.agent_run table not found",
                        window_days=window_days,
                    )

                # Fetch LM Studio calls with error details
                cur.execute(
                    """
                    SELECT
                        created_at,
                        result_json->>'ok' as ok,
                        result_json->>'latency_ms' as latency_ms,
                        violations_json
                    FROM control.agent_run
                    WHERE tool = 'lm_studio'
                      AND created_at >= %s
                    ORDER BY created_at DESC
                    """,
                    (since_dt,),
                )
                rows = cur.fetchall()

    except Exception as exc:  # noqa: BLE001
        return db_off_health_payload(f"database error: {exc!s}", window_days=window_days)

    # Process rows
    total_calls = len(rows)
    successful_calls = 0
    failed_calls = 0
    total_latency_ms = 0
    error_types: dict[str, int] = {}
    recent_errors: list[dict[str, Any]] = []

    for row in rows:
        created_at, ok_str, latency_ms_str, violations_json = row

        is_ok = ok_str == "true" if ok_str else False
        if is_ok:
            successful_calls += 1
        else:
            failed_calls += 1

            # Extract error type from violations_json
            if violations_json and isinstance(violations_json, list):
                for violation in violations_json:
                    if isinstance(violation, dict):
                        error_type = violation.get("type", "unknown_error")
                        error_types[error_type] = error_types.get(error_type, 0) + 1

                        # Collect recent errors (last 10)
                        if len(recent_errors) < 10:
                            recent_errors.append(
                                {
                                    "created_at": created_at.isoformat() if created_at else None,
                                    "type": error_type,
                                    "reason": violation.get("reason", "unknown"),
                                }
                            )

        if latency_ms_str:
            try:
                total_latency_ms += int(latency_ms_str)
            except (ValueError, TypeError):
                pass

    success_rate = successful_calls / total_calls if total_calls > 0 else 0.0
    error_rate = failed_calls / total_calls if total_calls > 0 else 0.0
    avg_latency_ms = total_latency_ms / total_calls if total_calls > 0 else 0.0

    # Health score: weighted combination of success rate and latency
    # Higher is better (0.0 = unhealthy, 1.0 = healthy)
    # Penalize high latency (>5000ms = 0.5x, >10000ms = 0.25x)
    latency_penalty = 1.0
    if avg_latency_ms > 10000:
        latency_penalty = 0.25
    elif avg_latency_ms > 5000:
        latency_penalty = 0.5
    elif avg_latency_ms > 2000:
        latency_penalty = 0.75

    health_score = success_rate * latency_penalty

    return LMHealth7dExport(
        schema="control",
        generated_at=now_iso(),
        window_days=window_days,
        since=since_dt.isoformat(),
        ok=True,
        connection_ok=True,
        health_score=health_score,
        success_rate=success_rate,
        avg_latency_ms=avg_latency_ms,
        error_rate=error_rate,
        error_types=error_types,
        recent_errors=recent_errors,
        error=None,
    )


def main() -> None:
    """Export LM usage and health metrics to JSON files."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Export usage metrics
    usage_export = fetch_lm_usage(window_days=7)
    usage_payload = asdict(usage_export)
    OUT_USAGE_PATH.write_text(
        json.dumps(usage_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    # Export health metrics
    health_export = fetch_lm_health(window_days=7)
    health_payload = asdict(health_export)
    OUT_HEALTH_PATH.write_text(
        json.dumps(health_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
