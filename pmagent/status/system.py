#!/usr/bin/env python3
"""
System Status Module

Phase-7G: Shared system status helpers for DB + LM health snapshots.
Reused by CLI (pmagent) and web API endpoints.
"""

from __future__ import annotations

from typing import Any

from pmagent.lm.lm_status import compute_lm_status
from scripts.guards.guard_db_health import check_db_health


def get_db_health_snapshot() -> dict[str, Any]:
    """Get DB health snapshot for web/API consumption.

    Returns:
        Dictionary with:
        {
            "reachable": bool,
            "mode": "ready" | "db_off" | "partial",
            "notes": str
        }
    """
    health = check_db_health()
    mode = health.get("mode", "db_off")
    ok = health.get("ok", False)
    errors = health.get("details", {}).get("errors", [])

    # Build notes
    if mode == "ready" and ok:
        notes = "Database is ready and all checks passed"
    elif mode == "partial":
        notes = f"Database connected but some tables missing: {errors[0] if errors else 'unknown'}"
    elif mode == "db_off":
        notes = f"Database unavailable: {errors[0] if errors else 'connection failed'}"
    else:
        notes = f"Unknown status: {mode}"

    return {
        "reachable": ok and mode == "ready",
        "mode": mode,
        "notes": notes,
    }


def get_lm_health_snapshot() -> dict[str, Any]:
    """Get LM health snapshot for web/API consumption.

    Returns:
        Dictionary with:
        {
            "slots": [
                {
                    "name": str,
                    "provider": str,
                    "model": str,
                    "service": "OK" | "DOWN" | "UNKNOWN" | "DISABLED" | "SKIPPED"
                },
                ...
            ],
            "notes": str
        }
    """
    status = compute_lm_status()
    slots = status.get("slots", [])

    # Transform slot format for web consumption
    web_slots = []
    for slot in slots:
        web_slots.append(
            {
                "name": slot.get("slot", "unknown"),
                "provider": slot.get("provider", "unknown"),
                "model": slot.get("model", "NOT_CONFIGURED"),
                "service": slot.get("service_status", "UNKNOWN"),
            }
        )

    return {
        "slots": web_slots,
        "notes": "Local-only providers (Ollama + LM Studio on 127.0.0.1).",
    }


def get_system_status() -> dict[str, Any]:
    """Get combined system status (DB + LM) for web/API consumption.

    Returns:
        Dictionary with:
        {
            "db": {
                "reachable": bool,
                "mode": str,
                "notes": str
            },
            "lm": {
                "slots": [...],
                "notes": str
            }
        }
    """
    return {
        "db": get_db_health_snapshot(),
        "lm": get_lm_health_snapshot(),
    }
