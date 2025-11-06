"""
Budget Control and Breach Handling

Provides configurable budget enforcement with strict/non-strict modes.
"""

import os


def strict_mode():
    """Check if budget strict mode is enabled."""
    return os.getenv("BUDGET_STRICT", "1") == "1"


class BudgetBreach(Exception):
    """Raised when budget limits are exceeded in strict mode."""

    pass


def handle_breach(summary: dict, *, kind: str, value, limit):
    """
    Handle budget breach according to BUDGET_STRICT setting.

    In strict mode: raises BudgetBreach exception
    In non-strict mode: logs breach in summary and continues

    Args:
        summary: Evidence summary dict to update
        kind: Budget type (e.g., "ai_calls", "p95_latency_ms")
        value: Actual value that exceeded limit
        limit: Budget limit that was exceeded
    """
    summary.setdefault("budget", {})["breach"] = {"kind": kind, "value": value, "limit": limit, "strict": strict_mode()}

    # Always raise to let caller decide based on strict mode
    raise BudgetBreach(f"BUDGET_EXCEEDED[{kind}]: {value} > {limit}")
    # non-strict: continue; caller writes summary and exits 0
