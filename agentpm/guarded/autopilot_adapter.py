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
    Supports both exact matches and keyword-based matching for natural language.

    Args:
        intent: The intent text (e.g., "status", "check system health", "show plan")

    Returns:
        The corresponding pmagent command string, or None if intent is not in whitelist.

    Examples:
        >>> map_intent_to_command("status")
        'pmagent status explain'
        >>> map_intent_to_command("check system health")
        'pmagent health system'
        >>> map_intent_to_command("unknown")
        None
    """
    # Normalize intent: lowercase and strip whitespace
    normalized = intent.lower().strip()

    # Try exact match first
    if normalized in INTENT_TO_COMMAND_MAP:
        return INTENT_TO_COMMAND_MAP[normalized]

    # Keyword-based matching for natural language
    # Check if intent contains keywords that map to commands
    if "status" in normalized or "system status" in normalized:
        return INTENT_TO_COMMAND_MAP.get("status")
    if "health" in normalized or "system health" in normalized or "check health" in normalized:
        return INTENT_TO_COMMAND_MAP.get("health")
    if "plan" in normalized or "next plan" in normalized or "show plan" in normalized:
        return INTENT_TO_COMMAND_MAP.get("plan")

    # Unknown intent - not in whitelist
    return None
