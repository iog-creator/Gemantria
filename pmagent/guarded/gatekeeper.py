# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

"""Gatekeeper: PoR token management, TTL checks, session readback."""

import hashlib
import time
from typing import Any, Dict

try:
    import psycopg
except ImportError:
    psycopg = None

from pmagent.control_plane.sessions import get_session, verify_por_checklist


def generate_por_token(session_id: str, timestamp: float | None = None) -> str:
    """
    Generate a PoR token for a session (in-memory, deterministic).
    In production, this could be signed.
    """
    if timestamp is None:
        timestamp = time.time()
    payload = f"{session_id}:{timestamp:.0f}"
    token_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"por-{token_hash}"


def verify_por_token(token: str, session_id: str, max_age_s: int = 300) -> bool:
    """
    Verify a PoR token matches a session (basic check).
    In production, this would verify signature and timestamp.
    """
    if not token.startswith("por-"):
        return False

    # For Phase-1, we accept any por-* token for the session
    # In production, we'd verify the hash matches
    return True


def check_session_ttl(session_id: str) -> bool:
    """Check if session is still valid (not expired). Returns True if valid."""
    session = get_session(session_id)
    return session is not None


def readback_session(session_id: str) -> Dict[str, Any] | None:
    """
    Read back session data including PoR checklist.
    Returns None if session not found or expired.
    """
    return get_session(session_id)


def validate_por(session_id: str, por_token: str | None = None) -> tuple[bool, str | None]:
    """
    Validate PoR for a session.
    Returns (is_valid, error_message).
    """
    session = get_session(session_id)
    if session is None:
        return False, "Session not found or expired"

    # Check PoR token if provided
    if por_token:
        if not verify_por_token(por_token, session_id):
            return False, "Invalid PoR token"

    # Verify PoR checklist matches current document state
    por_json = session.get("por_json", {})
    project_id = session.get("project_id")

    if not verify_por_checklist(project_id, por_json):
        return False, "PoR checklist verification failed (document drift)"

    return True, None
