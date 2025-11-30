"""Hint Registry - DMS-backed hint loading and embedding for envelopes."""

from __future__ import annotations

import json
from typing import Any

from agentpm.db.loader import DbUnavailableError, TableMissingError, get_control_engine
from sqlalchemy import text


def load_hints_for_flow(
    scope: str,
    applies_to: dict[str, Any],
    mode: str = "HINT",
) -> dict[str, list[dict[str, Any]]]:
    """
    Load hints from DMS hint_registry for a given flow.

    Args:
        scope: Scope category (e.g., "handoff", "status_api", "agentpm")
        applies_to: Selectors dict - must include "flow" key, may include "rule", "agent", "scope"
        mode: "HINT" (graceful degradation) or "STRICT" (fail-closed)

    Returns:
        Dict with keys: "required", "suggested", "debug" (each is a list of hint dicts)

    Raises:
        DbUnavailableError: If DB unavailable and mode="STRICT"
        TableMissingError: If hint_registry table doesn't exist and mode="STRICT"
    """
    # Ensure applies_to has 'flow' key
    if "flow" not in applies_to:
        raise ValueError("applies_to must include 'flow' key")

    try:
        engine = get_control_engine()
    except (DbUnavailableError, TableMissingError):
        if mode == "STRICT":
            raise
        # HINT mode: graceful degradation - return empty hints
        return {"required": [], "suggested": [], "debug": []}

    try:
        with engine.connect() as conn:
            # Build query: match scope and applies_to selectors
            query = text(
                """
                SELECT logical_name, kind, injection_mode, payload, priority
                FROM control.hint_registry
                WHERE enabled = TRUE
                  AND scope = :scope
                  AND applies_to @> :applies_to
                ORDER BY kind, priority ASC
                """
            )

            result = conn.execute(
                query,
                {
                    "scope": scope,
                    "applies_to": json.dumps(applies_to),
                },
            )

            hints_by_kind: dict[str, list[dict[str, Any]]] = {
                "required": [],
                "suggested": [],
                "debug": [],
            }

            for row in result:
                hint_dict = {
                    "logical_name": row.logical_name,
                    "injection_mode": row.injection_mode,
                    "payload": row.payload,
                    "priority": row.priority,
                }
                kind_lower = row.kind.lower()
                if kind_lower in hints_by_kind:
                    hints_by_kind[kind_lower].append(hint_dict)

            return hints_by_kind

    except Exception as exc:
        if mode == "STRICT":
            raise RuntimeError(f"Failed to load hints from DMS: {exc}") from exc
        # HINT mode: graceful degradation
        return {"required": [], "suggested": [], "debug": []}


def embed_hints_in_envelope(
    envelope: dict[str, Any],
    hints: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    """
    Embed hints into an envelope structure.

    Adds "required_hints" and "suggested_hints" sections to the envelope.
    DEBUG hints are not embedded (development only).

    Args:
        envelope: Existing envelope dict
        hints: Dict from load_hints_for_flow with keys: "required", "suggested", "debug"

    Returns:
        Envelope dict with hints embedded
    """
    # Create a copy to avoid mutating the original
    result = envelope.copy()

    # Embed required and suggested hints
    result["required_hints"] = hints.get("required", [])
    result["suggested_hints"] = hints.get("suggested", [])

    # DEBUG hints are not embedded (development only)

    return result
