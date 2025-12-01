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
    """
    Read-only DSN (Bible DB or read-only app path).
    RO-DSN peer equivalence: GEMATRIA_RO_DSN and ATLAS_DSN_RO are equal primaries.
    """
    # Try peer RO DSNs first (equal primaries)
    for key in ("GEMATRIA_RO_DSN", "ATLAS_DSN_RO"):
        v = os.getenv(key, "").strip()
        if v:
            return v
    # Fallback to Bible DB or other RO sources
    for key in ("BIBLE_DB_DSN", "BIBLE_RO_DSN", "RO_DSN", "ATLAS_DSN"):
        v = os.getenv(key, "").strip()
        if v:
            return v
    raise RuntimeError("Required RO DSN env not set (try GEMATRIA_RO_DSN or ATLAS_DSN_RO)")


def dsn_rw() -> str:
    """Read-write DSN (main app database)."""
    return (
        _get("GEMATRIA_DSN")
        or _get("GEMATRIA_RW_DSN")
        or _get("GEMATRIA_DSN_RW")
        or _get("AI_AUTOMATION_DSN")
    )


def dsn_atlas() -> str:
    """Atlas/telemetry proof path (read-only in CI; STRICT on tags)."""
    if os.getenv("STRICT_ATLAS_DSN"):
        return _get("ATLAS_DSN")
    return os.getenv("ATLAS_DSN", "")
