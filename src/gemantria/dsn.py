"""Central DSN resolver — the ONLY allowed DSN env touchpoint.

All other modules must import and call dsn_ro()/dsn_rw()/dsn_atlas().
"""

from __future__ import annotations
import os


def _get(name: str) -> str:
    v = os.getenv(name, "").strip()
    if not v:
        # Keep messages generic; secrets never printed.
        raise RuntimeError(f"Required DSN env not set: {name}")
    return v


def dsn_ro() -> str:
    """Read-only DSN (Bible DB or read-only app path)."""
    return _get("BIBLE_DB_DSN") or _get("GEMATRIA_RO_DSN") or _get("GEMATRIA_DSN_RO")


def dsn_rw() -> str:
    """Read-write DSN (main app database)."""
    return _get("GEMATRIA_DSN") or _get("GEMATRIA_RW_DSN") or _get("GEMATRIA_DSN_RW") or _get("AI_AUTOMATION_DSN")


def dsn_atlas() -> str:
    """Atlas/telemetry proof path (read-only in CI; STRICT on tags)."""
    if os.getenv("STRICT_ATLAS_DSN"):
        return _get("ATLAS_DSN")
    return os.getenv("ATLAS_DSN", "")
