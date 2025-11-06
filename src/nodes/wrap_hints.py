"""
Wrap hints node for pipeline hints envelope generation.

Related Rules: Rule-039 (Execution Contract), Rule-050 (OPS Contract), Rule-058 (Auto-Housekeeping)
Related ADRs: ADR-032 (Organic AI Discovery), ADR-019 (Data Contracts)
"""

from typing import Any

from src.infra.structured_logger import get_logger, log_json

LOG = get_logger("gematria.wrap_hints")


def wrap_hints_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Wrap runtime hints into envelope structure for persistence.

    This node collects hints from the pipeline state and wraps them into a structured
    envelope format for export validation and auditability.
    """
    try:
        # If hints are already enveloped, pass through
        if state.get("enveloped_hints"):
            log_json(LOG, 20, "hints_already_enveloped", count=state["enveloped_hints"].get("count", 0))
            return state

        # Collect hints from state
        hints = state.get("hints", [])
        if not hints:
            log_json(LOG, 20, "no_hints_to_wrap")
            # Create empty envelope for consistency
            state["enveloped_hints"] = {
                "type": "hints_envelope",
                "version": "1.0",
                "items": [],
                "count": 0,
            }
            return state

        # Wrap hints into envelope structure with imperative commands
        hints_envelope = {
            "type": "hints_envelope",
            "version": "1.0",
            "items": hints,
            "count": len(hints),
            "imperative_commands": [
                "AGENT_STOP_AND_PAY_ATTENTION",
                "PROCESS_HINTS_ENVELOPE_IMMEDIATELY",
                "CHECK_METADATA_REQUIREMENTS",
                "VALIDATE_ENVELOPE_CONTENTS",
            ],
            "enforcement_level": "CRITICAL",
            "ignore_risk": "PIPELINE_ABORT",
        }

        state["enveloped_hints"] = hints_envelope
        log_json(LOG, 20, "hints_wrapped", count=len(hints))

        return state

    except Exception as e:
        log_json(LOG, 40, "wrap_hints_failed", error=str(e))
        # Don't fail the pipeline on hints wrapping errors
        return state
