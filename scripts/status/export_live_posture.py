#!/usr/bin/env python3
"""
Live System Posture Export for PM Share Package

Exports DB/LM/DSN posture as JSON including:
- DB mode (ready/db_off/partial)
- LM mode and slot availability
- DSN posture (redacted)
- Model availability (Qwen/Granite slots)

Uses centralized DSN loaders (never os.getenv directly).
Tolerates empty/nonexistent DB/LM (exits 0, writes empty export for CI tolerance).
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.config.env import get_rw_dsn, get_ro_dsn, get_bible_db_dsn, env

OUT_DIR = REPO / "share"
OUT_FILE = OUT_DIR / "live_posture.json"


def now_iso() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now(UTC).isoformat()


def redact_dsn(dsn: str | None) -> str:
    """Redact DSN to show only scheme and database name."""
    if not dsn:
        return "(unset)"
    # Keep scheme and database name only
    m = re.match(r"^([a-zA-Z0-9+.-]+)://.*?/(.*?)(?:[?].*)?$", dsn)
    if m:
        return f"{m.group(1)}://<REDACTED>/{m.group(2)}"
    return "<REDACTED-DSN>"


def export_live_posture() -> dict[str, Any]:
    """Export live system posture."""
    # Get DSNs (redacted)
    rw_dsn = get_rw_dsn()
    ro_dsn = get_ro_dsn()
    bible_dsn = get_bible_db_dsn()

    # Get DB health
    try:
        from scripts.guards.guard_db_health import check_db_health

        db_health = check_db_health()
        db_mode = db_health.get("mode", "db_off")
        db_ok = db_health.get("ok", False)
    except Exception as exc:
        db_health = {"ok": False, "mode": "error", "error": str(exc)}
        db_mode = "error"
        db_ok = False

    # Get LM status
    try:
        from pmagent.status.system import get_system_status

        system_status = get_system_status()
        lm_slots = system_status.get("lm", {}).get("slots", [])
    except Exception as exc:
        lm_slots = []
        system_status = {"lm": {"slots": [], "error": str(exc)}}

    # Check model availability
    model_availability = {}
    for slot in lm_slots:
        slot_name = slot.get("name", "unknown")
        provider = slot.get("provider", "unknown")
        model = slot.get("model", "NOT_CONFIGURED")
        service = slot.get("service", "UNKNOWN")
        model_availability[slot_name] = {
            "provider": provider,
            "model": model,
            "available": service in ["OK", "UP"],
        }

    # Check for Qwen/Granite models
    qwen_available = any(
        "qwen" in slot.get("model", "").lower() and slot.get("service") in ["OK", "UP"] for slot in lm_slots
    )
    granite_available = any(
        "granite" in slot.get("model", "").lower() and slot.get("service") in ["OK", "UP"] for slot in lm_slots
    )

    return {
        "schema": "live_posture.v1",
        "generated_at": now_iso(),
        "db": {
            "mode": db_mode,
            "ok": db_ok,
            "dsn_rw": redact_dsn(rw_dsn),
            "dsn_ro": redact_dsn(ro_dsn),
            "dsn_bible": redact_dsn(bible_dsn),
        },
        "lm": {
            "slots": lm_slots,
            "model_availability": model_availability,
            "qwen_available": qwen_available,
            "granite_available": granite_available,
        },
        "checkpointer": env("CHECKPOINTER", "memory"),
        "enforce_strict": env("ENFORCE_STRICT", ""),
        "db_off": db_mode == "db_off",
    }


def main() -> int:
    """Main entrypoint."""
    # Ensure output directory exists
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        export_data = export_live_posture()
        OUT_FILE.write_text(
            json.dumps(export_data, indent=2, default=str),
            encoding="utf-8",
        )
        print(f"✅ Exported live posture: DB={export_data['db']['mode']}, LM slots={len(export_data['lm']['slots'])}")
        return 0
    except Exception as exc:
        print(f"ERROR: Failed to export live posture: {exc}", file=sys.stderr)
        error_data = {
            "schema": "live_posture.v1",
            "generated_at": now_iso(),
            "error": f"Failed to generate posture: {exc!s}",
            "db_off": True,
        }
        OUT_FILE.write_text(
            json.dumps(error_data, indent=2, default=str),
            encoding="utf-8",
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
