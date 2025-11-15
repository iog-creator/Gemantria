#!/usr/bin/env python3
"""
LM Studio Indicator Export for Downstream Apps

Phase-4C: Exports a compact LM status indicator derived from lm_insights_7d.json
to share/atlas/control_plane/ for consumption by StoryMaker, BibleScholar, and
other downstream applications.

Tolerates db_off and LM-off (no DB or LM Studio required; best-effort offline indicator).
Reads from existing lm_insights_7d.json file.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "share" / "atlas" / "control_plane"
INSIGHTS_PATH = OUT_DIR / "lm_insights_7d.json"
OUT_INDICATOR_PATH = OUT_DIR / "lm_indicator.json"


@dataclass
class LMIndicatorExport:
    status: str  # "offline" | "healthy" | "degraded"
    reason: str  # "db_off" | "no_calls" | "high_error_rate" | "ok"
    success_rate: float
    error_rate: float
    total_calls: int
    db_off: bool
    top_error_reason: str | None
    window_days: int
    generated_at: str


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def load_json_file(path: Path) -> dict[str, Any] | None:
    """Load JSON file, return None if missing or invalid."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def compute_indicator() -> LMIndicatorExport:
    """Compute LM indicator from existing insights JSON file."""
    # Load insights data
    insights_data = load_json_file(INSIGHTS_PATH)

    # If insights file is missing or invalid, emit conservative offline indicator
    if not insights_data:
        return LMIndicatorExport(
            status="offline",
            reason="db_off",
            success_rate=0.0,
            error_rate=0.0,
            total_calls=0,
            db_off=True,
            top_error_reason="db_off",
            window_days=7,
            generated_at=now_iso(),
        )

    # Extract fields from insights
    db_off = insights_data.get("db_off", False)
    connection_ok = insights_data.get("connection_ok", False)
    total_calls = insights_data.get("total_calls", 0)
    success_rate = insights_data.get("success_rate", 0.0)
    error_rate = insights_data.get("error_rate", 0.0)
    top_error_reason = insights_data.get("top_error_reason")
    window_days = insights_data.get("window_days", 7)
    generated_at = insights_data.get("generated_at", now_iso())

    # Determine status and reason using heuristic
    if db_off or not connection_ok:
        status = "offline"
        reason = "db_off"
    elif total_calls == 0:
        status = "offline"
        reason = "no_calls"
    elif error_rate >= 0.2:
        status = "degraded"
        reason = "high_error_rate"
    else:
        status = "healthy"
        reason = "ok"

    return LMIndicatorExport(
        status=status,
        reason=reason,
        success_rate=success_rate,
        error_rate=error_rate,
        total_calls=total_calls,
        db_off=db_off,
        top_error_reason=top_error_reason,
        window_days=window_days,
        generated_at=generated_at,
    )


def main() -> None:
    """Export LM indicator to JSON file."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Compute indicator from existing insights export
    indicator_export = compute_indicator()
    indicator_payload = asdict(indicator_export)

    # Write indicator JSON
    OUT_INDICATOR_PATH.write_text(
        json.dumps(indicator_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
