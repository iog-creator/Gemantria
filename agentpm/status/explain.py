#!/usr/bin/env python3
"""
Status Explanation Module

Phase-8A: Human-readable explanations of system status (DB + LM health).
Uses rule-based logic with optional LM enhancement for better wording.
"""

from __future__ import annotations

import json
from typing import Any

from agentpm.status.system import get_system_status


def summarize_system_status(status: dict[str, Any]) -> dict[str, Any]:
    """Summarize system status into a human-readable explanation.

    Args:
        status: System status dict from get_system_status()

    Returns:
        Dictionary with:
        {
            "level": "OK" | "WARN" | "ERROR",
            "headline": str,
            "details": str,
        }
    """
    db = status.get("db", {})
    lm = status.get("lm", {})

    db_mode = db.get("mode", "db_off")
    db_reachable = db.get("reachable", False)
    db_notes = db.get("notes", "")

    lm_slots = lm.get("slots", [])

    # Count LM slot states
    slot_states = [slot.get("service", "UNKNOWN") for slot in lm_slots]
    ok_slots = sum(1 for s in slot_states if s == "OK")
    down_slots = sum(1 for s in slot_states if s == "DOWN")
    unknown_slots = sum(1 for s in slot_states if s in ("UNKNOWN", "DISABLED", "SKIPPED"))
    total_slots = len(slot_states)

    # Determine overall level and headline
    level = "OK"
    headline = "All systems nominal"
    details_parts = []

    # DB status assessment
    if db_mode == "db_off":
        level = "ERROR"
        headline = "Database is offline"
        details_parts.append("Database is not reachable. This prevents data operations.")
        if db_notes:
            details_parts.append(f"Details: {db_notes}")
    elif db_mode == "partial":
        level = "WARN"
        headline = "Database is partially configured"
        details_parts.append("Database is connected, but some tables or features are missing.")
        if db_notes:
            details_parts.append(f"Details: {db_notes}")
    elif db_mode == "ready" and db_reachable:
        details_parts.append("Database is ready and all checks passed.")
    else:
        level = "WARN"
        headline = "Database status is unclear"
        details_parts.append(f"Database mode: {db_mode}")

    # LM status assessment
    if total_slots == 0:
        details_parts.append("No LM slots configured.")
    elif down_slots > 0:
        if level == "OK":
            level = "WARN"
            headline = "Some LM services are down"
        elif level == "WARN":
            level = "ERROR"
            headline = "Database and LM issues detected"
        down_slot_names = [slot.get("name", "unknown") for slot in lm_slots if slot.get("service") == "DOWN"]
        details_parts.append(f"{down_slots} of {total_slots} LM slot(s) are down: {', '.join(down_slot_names)}.")
    elif unknown_slots > 0:
        if level == "OK":
            level = "WARN"
            headline = "Some LM services have unknown status"
        unknown_slot_names = [
            slot.get("name", "unknown")
            for slot in lm_slots
            if slot.get("service") in ("UNKNOWN", "DISABLED", "SKIPPED")
        ]
        details_parts.append(
            f"{unknown_slots} of {total_slots} LM slot(s) have unknown/disabled status: {', '.join(unknown_slot_names)}."
        )
    elif ok_slots == total_slots and total_slots > 0:
        details_parts.append(f"All {total_slots} LM slot(s) are operational.")

    # Combine details
    details = " ".join(details_parts)

    return {
        "level": level,
        "headline": headline,
        "details": details,
    }


def _enhance_with_lm(rule_based: dict[str, Any], status: dict[str, Any]) -> dict[str, Any]:
    """Optionally enhance explanation with LM-generated text.

    Args:
        rule_based: Rule-based explanation dict
        status: Raw system status dict

    Returns:
        Enhanced explanation dict (or original if LM unavailable)
    """
    # Check if LM is available by looking at local_agent slot
    lm_slots = status.get("lm", {}).get("slots", [])
    local_agent_slot = next((s for s in lm_slots if s.get("name") == "local_agent"), None)

    if not local_agent_slot or local_agent_slot.get("service") != "OK":
        # LM not available, return rule-based explanation
        return rule_based

    # Try to call LM for better wording
    try:
        # Import here to avoid circular dependencies
        from agentpm.adapters.lm_studio import chat

        # Build prompt
        status_json = json.dumps(status, indent=2)
        prompt = f"""Given this system status snapshot:

{status_json}

Provide a concise, non-technical explanation (2-4 sentences) of the current system health.
Focus on what the user needs to know, not technical details.
Do not include stack traces or error codes.

Current assessment: {rule_based["level"]} - {rule_based["headline"]}
Current details: {rule_based["details"]}

Provide an improved, user-friendly explanation:"""

        system_prompt = "You are a helpful system administrator assistant. Provide clear, concise explanations of system status in plain language."

        # Call LM (guarded - will raise if unavailable)
        enhanced_text = chat(prompt, model_slot="local_agent", system=system_prompt)

        # Use LM text as details, but keep original level and headline
        return {
            "level": rule_based["level"],
            "headline": rule_based["headline"],
            "details": enhanced_text.strip(),
        }
    except Exception:
        # LM call failed, return rule-based explanation
        return rule_based


def explain_system_status(use_lm: bool = True) -> dict[str, Any]:
    """Explain current system status in plain language.

    Args:
        use_lm: Whether to attempt LM enhancement (default: True)

    Returns:
        Dictionary with:
        {
            "level": "OK" | "WARN" | "ERROR",
            "headline": str,
            "details": str,
        }
    """
    try:
        # Get current system status
        status = get_system_status()
    except Exception:
        # If status check fails, return a safe fallback explanation
        return {
            "level": "ERROR",
            "headline": "Unable to check system status",
            "details": "Failed to retrieve system status. Please check logs for details.",
        }

    # Generate rule-based explanation
    explanation = summarize_system_status(status)

    # Optionally enhance with LM
    if use_lm:
        explanation = _enhance_with_lm(explanation, status)

    return explanation
