"""
LM Indicator Widget adapter for downstream apps (StoryMaker, BibleScholar).

Transforms the canonical `lm_indicator.json` signal into widget props matching
the LM_WIDGETS.md contract. Hermetic (file-only, no DB/LM calls) and fail-closed
(offline-safe defaults when file is missing or invalid).

See `docs/SSOT/LM_WIDGETS.md` for the widget contract specification.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal, TypedDict

INDICATOR_PATH = Path("share/atlas/control_plane/lm_indicator.json")

# Type aliases
LmStatus = Literal["offline", "healthy", "degraded"]
LmReason = Literal["db_off", "no_calls", "high_error_rate", "ok"]
LmColor = Literal["grey", "green", "yellow", "red"]


class MetricsProps(TypedDict):
    """Metrics properties for widget contract."""

    successRate: float | None
    errorRate: float | None
    totalCalls: int | None
    dbOff: bool
    topErrorReason: str | None
    windowDays: int
    generatedAt: str


class LmIndicatorWidgetProps(TypedDict):
    """Widget props matching LM_WIDGETS.md contract."""

    status: LmStatus
    reason: LmReason
    label: str
    color: LmColor
    icon: str
    tooltip_lines: List[str]
    metrics: MetricsProps
    source: Dict[str, str]


@dataclass
class RawIndicator:
    """Raw indicator data parsed from JSON file."""

    status: str
    reason: str
    success_rate: float | None
    error_rate: float | None
    total_calls: int | None
    db_off: bool
    top_error_reason: str | None
    window_days: int
    generated_at: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RawIndicator:
        """Parse raw indicator from dict with safe defaults."""
        return cls(
            status=str(data.get("status", "offline")),
            reason=str(data.get("reason", "db_off")),
            success_rate=_to_optional_float(data.get("success_rate")),
            error_rate=_to_optional_float(data.get("error_rate")),
            total_calls=_to_optional_int(data.get("total_calls")),
            db_off=bool(data.get("db_off", True)),
            top_error_reason=_to_optional_str(data.get("top_error_reason")),
            window_days=int(data.get("window_days", 7)),
            generated_at=str(data.get("generated_at", "1970-01-01T00:00:00Z")),
        )


# Offline-safe default widget props
OFFLINE_SAFE_DEFAULT: LmIndicatorWidgetProps = {
    "status": "offline",
    "reason": "db_off",
    "label": "LM status unknown (offline-safe mode)",
    "color": "grey",
    "icon": "status-offline",
    "tooltip_lines": [
        "LM status unavailable",
        "Operating in offline-safe mode",
    ],
    "metrics": {
        "successRate": None,
        "errorRate": None,
        "totalCalls": None,
        "dbOff": True,
        "topErrorReason": None,
        "windowDays": 7,
        "generatedAt": "1970-01-01T00:00:00Z",
    },
    "source": {"path": str(INDICATOR_PATH)},
}


def _to_optional_float(value: Any) -> float | None:
    """Convert value to float or None."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _to_optional_int(value: Any) -> int | None:
    """Convert value to int or None."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _to_optional_str(value: Any) -> str | None:
    """Convert value to str or None."""
    if value is None:
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    return str(value)


def _normalize_status(status: str) -> LmStatus:
    """Normalize status string to valid LmStatus."""
    status_lower = status.lower().strip()
    if status_lower in ("offline", "healthy", "degraded"):
        return status_lower  # type: ignore[return-value]
    return "offline"  # Default to offline for unknown status


def _normalize_reason(reason: str) -> LmReason:
    """Normalize reason string to valid LmReason."""
    reason_lower = reason.lower().strip()
    if reason_lower in ("db_off", "no_calls", "high_error_rate", "ok"):
        return reason_lower  # type: ignore[return-value]
    return "db_off"  # Default to db_off for unknown reason


def _generate_label(status: LmStatus, reason: LmReason) -> str:
    """Generate human-readable label from status and reason."""
    if status == "offline" and reason == "db_off":
        return "LM Studio offline (database unavailable)"
    if status == "offline" and reason == "no_calls":
        return "LM Studio offline (no recent activity)"
    if status == "degraded" and reason == "high_error_rate":
        return "LM Studio degraded (high error rate)"
    if status == "healthy" and reason == "ok":
        return "LM Studio healthy"
    # Fallback
    return f"LM Studio {status} ({reason})"


def _generate_color(status: LmStatus, error_rate: float | None) -> LmColor:
    """Generate color from status and error rate."""
    if status == "offline":
        return "grey"
    if status == "healthy":
        return "green"
    if status == "degraded":
        # Red if error rate >= 0.5, yellow otherwise
        if error_rate is not None and error_rate >= 0.5:
            return "red"
        return "yellow"
    return "grey"  # Fallback


def _generate_icon(status: LmStatus) -> str:
    """Generate icon name from status."""
    if status == "offline":
        return "status-offline"
    if status == "healthy":
        return "status-healthy"
    if status == "degraded":
        return "status-degraded"
    return "status-offline"  # Fallback


def _generate_tooltip_lines(indicator: RawIndicator) -> List[str]:
    """Generate tooltip lines from indicator data."""
    lines: List[str] = []

    # Status summary line
    status_label = _generate_label(
        _normalize_status(indicator.status),
        _normalize_reason(indicator.reason),
    )
    lines.append(status_label)

    # Key metrics
    if indicator.total_calls is not None and indicator.total_calls > 0:
        lines.append(f"Total calls: {indicator.total_calls:,}")

    if indicator.success_rate is not None:
        success_pct = indicator.success_rate * 100
        lines.append(f"Success rate: {success_pct:.1f}%")

    if indicator.error_rate is not None and indicator.error_rate > 0:
        error_pct = indicator.error_rate * 100
        lines.append(f"Error rate: {error_pct:.1f}%")

    # Reason explanation
    if indicator.reason == "db_off":
        lines.append("Database unavailable")
    elif indicator.reason == "no_calls":
        lines.append("No recent LM Studio activity")
    elif indicator.reason == "high_error_rate":
        if indicator.top_error_reason:
            lines.append(f"Top error: {indicator.top_error_reason}")

    # Window info
    lines.append(f"Window: {indicator.window_days} days")

    return lines


def load_lm_indicator_widget_props() -> LmIndicatorWidgetProps:
    """
    Load LM indicator widget props from canonical JSON file.

    Returns widget props matching LM_WIDGETS.md contract. Hermetic (file-only,
    no DB/LM calls) and fail-closed (offline-safe defaults when file is missing
    or invalid).

    Returns:
        LmIndicatorWidgetProps: Widget props with status, reason, label, color,
            icon, tooltip_lines, metrics, and source fields.

    Example:
        >>> props = load_lm_indicator_widget_props()
        >>> print(props["status"])
        "healthy"
        >>> print(props["label"])
        "LM Studio healthy"
    """
    # Read indicator file
    try:
        if not INDICATOR_PATH.exists():
            return OFFLINE_SAFE_DEFAULT

        raw_json = json.loads(INDICATOR_PATH.read_text(encoding="utf-8"))
        raw_indicator = RawIndicator.from_dict(raw_json)

    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return OFFLINE_SAFE_DEFAULT

    # Normalize status and reason
    status = _normalize_status(raw_indicator.status)
    reason = _normalize_reason(raw_indicator.reason)

    # Generate widget props
    props: LmIndicatorWidgetProps = {
        "status": status,
        "reason": reason,
        "label": _generate_label(status, reason),
        "color": _generate_color(status, raw_indicator.error_rate),
        "icon": _generate_icon(status),
        "tooltip_lines": _generate_tooltip_lines(raw_indicator),
        "metrics": {
            "successRate": raw_indicator.success_rate,
            "errorRate": raw_indicator.error_rate,
            "totalCalls": raw_indicator.total_calls,
            "dbOff": raw_indicator.db_off,
            "topErrorReason": raw_indicator.top_error_reason,
            "windowDays": raw_indicator.window_days,
            "generatedAt": raw_indicator.generated_at,
        },
        "source": {"path": str(INDICATOR_PATH)},
    }

    return props
