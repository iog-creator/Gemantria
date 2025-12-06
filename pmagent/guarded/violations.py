"""Violation codes for guarded tool calls (Phase-1 subset)."""

# Phase-1 violation codes (subset of full taxonomy)
MISSING_POR = "MISSING_POR"
ARG_SCHEMA_INVALID = "ARG_SCHEMA_INVALID"
RING_VIOLATION = "RING_VIOLATION"
PROVENANCE_MISMATCH = "PROVENANCE_MISMATCH"
FORBIDDEN_TOOL = "FORBIDDEN_TOOL"
BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
RETRY_EXHAUSTED = "RETRY_EXHAUSTED"

# All Phase-1 codes
PHASE1_CODES = {
    MISSING_POR,
    ARG_SCHEMA_INVALID,
    RING_VIOLATION,
    PROVENANCE_MISMATCH,
    FORBIDDEN_TOOL,
    BUDGET_EXCEEDED,
    RETRY_EXHAUSTED,
}


def create_violation(code: str, detail: str, at: str | None = None) -> dict:
    """Create a violation object."""
    import datetime

    if at is None:
        at = datetime.datetime.now(datetime.UTC).isoformat()

    return {
        "code": code,
        "detail": detail,
        "at": at,
    }


def is_phase1_code(code: str) -> bool:
    """Check if code is a Phase-1 violation code."""
    return code in PHASE1_CODES
