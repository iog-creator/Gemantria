"""Guarded Tool Adapter for Autopilot Phase C.

Maps Autopilot intents to safe pmagent commands with a whitelist approach.
Only known, safe commands are allowed; unknown intents return None.
"""

from __future__ import annotations

# Whitelist of safe intent -> command mappings
INTENT_TO_COMMAND_MAP: dict[str, str] = {
    "status": "pmagent status explain",
    "health": "pmagent health system",
    "plan": "pmagent plan next",
}


def map_intent_to_command(intent: str) -> str | None:
    """Map an Autopilot intent to a safe pmagent command.

    Uses a strict whitelist approach: only known, safe intents are mapped.
    Unknown intents return None to indicate they are not allowed.

    Args:
        intent: The intent text (e.g., "status", "health", "plan")

    Returns:
        The corresponding pmagent command string, or None if intent is not in whitelist.

    Examples:
        >>> map_intent_to_command("status")
        'pmagent status explain'
        >>> map_intent_to_command("unknown")
        None
    """
    # Normalize intent: lowercase and strip whitespace
    normalized = intent.lower().strip()

    # Return mapped command if in whitelist, None otherwise
    return INTENT_TO_COMMAND_MAP.get(normalized)
