#!/usr/bin/env python3
"""
LM Studio Insights Export for Atlas

Phase-4A: Exports aggregated LM Studio insights derived from usage and health metrics
to share/atlas/control_plane/ for Atlas visualization.

Tolerates db_off and LM-off (no DB or LM Studio required; best-effort empty exports).
Reads from existing lm_usage_7d.json and lm_health_7d.json files.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "share" / "atlas" / "control_plane"
USAGE_PATH = OUT_DIR / "lm_usage_7d.json"
HEALTH_PATH = OUT_DIR / "lm_health_7d.json"
OUT_INSIGHTS_PATH = OUT_DIR / "lm_insights_7d.json"


@dataclass
class LMInsights7dExport:
    schema: str
    generated_at: str
    window_days: int
    since: str
    ok: bool
    connection_ok: bool
    db_off: bool
    total_calls: int
    successful_calls: int
    failed_calls: int
    success_rate: float
    error_rate: float
    lm_studio_calls: int | None = None
    remote_calls: int | None = None
    lm_studio_usage_ratio: float | None = None
    top_error_reason: str | None = None
    error: str | None = None


def now_utc() -> datetime:
    return datetime.now(UTC)


def now_iso() -> str:
    return now_utc().isoformat()


def db_off_insights_payload(message: str, window_days: int = 7) -> LMInsights7dExport:
    """Generate db_off insights payload."""
    since_dt = now_utc() - timedelta(days=window_days)
    return LMInsights7dExport(
        schema="control",
        generated_at=now_iso(),
        window_days=window_days,
        since=since_dt.isoformat(),
        ok=False,
        connection_ok=False,
        db_off=True,
        total_calls=0,
        successful_calls=0,
        failed_calls=0,
        success_rate=0.0,
        error_rate=0.0,
        lm_studio_calls=None,
        remote_calls=None,
        lm_studio_usage_ratio=None,
        top_error_reason="db_off",
        error=message,
    )


def load_json_file(path: Path) -> dict[str, Any] | None:
    """Load JSON file, return None if missing or invalid."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def compute_insights(window_days: int = 7) -> LMInsights7dExport:
    """Compute LM insights from existing usage and health JSON files."""
    # Load usage and health data
    usage_data = load_json_file(USAGE_PATH)
    health_data = load_json_file(HEALTH_PATH)

    # If either file is missing or invalid, treat as db_off
    if not usage_data or not health_data:
        return db_off_insights_payload(
            "lm_usage_7d.json or lm_health_7d.json missing or invalid",
            window_days=window_days,
        )

    # Check if connection is OK
    connection_ok = usage_data.get("connection_ok", False) and health_data.get("connection_ok", False)
    db_off = not connection_ok

    # If db_off, return db_off payload
    if db_off:
        error_msg = usage_data.get("error") or health_data.get("error") or "database offline"
        return db_off_insights_payload(error_msg, window_days=window_days)

    # Extract metrics from usage data
    total_calls = usage_data.get("total_calls", 0)
    successful_calls = usage_data.get("successful_calls", 0)
    failed_calls = usage_data.get("failed_calls", 0)

    # Extract metrics from health data
    success_rate = health_data.get("success_rate", 0.0)
    error_rate = health_data.get("error_rate", 0.0)
    error_types = health_data.get("error_types", {})

    # Determine top error reason
    top_error_reason = None
    if error_types:
        # Find the most common error type
        top_error_type = max(error_types.items(), key=lambda x: x[1], default=None)
        if top_error_type:
            top_error_reason = top_error_type[0]
    elif failed_calls > 0:
        # If we have failures but no error types, use a generic reason
        top_error_reason = "unknown_error"
    # Note: db_off case is handled earlier in the function

    # For now, we don't have backend breakdown (lm_studio vs remote) in the current data
    # This would require querying the DB for backend field or adding it to usage export
    # For Phase-4A, we'll set these to None and they can be populated in a future enhancement
    lm_studio_calls = None
    remote_calls = None
    lm_studio_usage_ratio = None

    # If we had backend breakdown, we could compute:
    # lm_studio_usage_ratio = lm_studio_calls / total_calls if total_calls > 0 else 0.0

    since_dt = now_utc() - timedelta(days=window_days)

    return LMInsights7dExport(
        schema="control",
        generated_at=now_iso(),
        window_days=window_days,
        since=since_dt.isoformat(),
        ok=True,
        connection_ok=connection_ok,
        db_off=db_off,
        total_calls=total_calls,
        successful_calls=successful_calls,
        failed_calls=failed_calls,
        success_rate=success_rate,
        error_rate=error_rate,
        lm_studio_calls=lm_studio_calls,
        remote_calls=remote_calls,
        lm_studio_usage_ratio=lm_studio_usage_ratio,
        top_error_reason=top_error_reason,
        error=None,
    )


def main() -> None:
    """Export LM insights to JSON file."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Compute insights from existing usage and health exports
    insights_export = compute_insights(window_days=7)
    insights_payload = asdict(insights_export)

    # Write insights JSON
    OUT_INSIGHTS_PATH.write_text(
        json.dumps(insights_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
