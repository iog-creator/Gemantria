"""Hint Registry - DMS-backed hint loading and embedding for envelopes."""

from __future__ import annotations

import json
from typing import Any

from pmagent.db.loader import DbUnavailableError, TableMissingError, get_control_engine
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

    except Exception as exc:  # noqa: BLE001
        if mode == "STRICT":
            raise RuntimeError(f"Failed to configure DSPy LM for LM Studio: {exc}") from exc  # noqa: E501
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


def list_all_hints(
    scope: str | None = None,
    kind: str | None = None,
    flow: str | None = None,
) -> list[dict[str, Any]]:
    """
    List hints from the registry with optional filtering.

    Args:
        scope: Filter by scope
        kind: Filter by kind
        flow: Filter by flow (within applies_to)

    Returns:
        List of hint dicts
    """
    try:
        engine = get_control_engine()
    except (DbUnavailableError, TableMissingError):
        # Graceful degradation for listing
        return []

    try:
        with engine.connect() as conn:
            # Base query
            query_str = """
                SELECT logical_name, scope, applies_to, kind, injection_mode, payload, priority, enabled
                FROM control.hint_registry
                WHERE enabled = TRUE
            """
            params = {}

            if scope:
                query_str += " AND scope = :scope"
                params["scope"] = scope

            if kind:
                query_str += " AND kind = :kind"
                params["kind"] = kind

            if flow:
                query_str += " AND applies_to->>'flow' = :flow"
                params["flow"] = flow

            query_str += " ORDER BY scope, kind, priority ASC"

            result = conn.execute(text(query_str), params)

            hints = []
            for row in result:
                hints.append(
                    {
                        "logical_name": row.logical_name,
                        "scope": row.scope,
                        "applies_to": row.applies_to,
                        "kind": row.kind,
                        "injection_mode": row.injection_mode,
                        "payload": row.payload,
                        "priority": row.priority,
                        "enabled": row.enabled,
                    }
                )
            return hints

    except Exception as exc:
        print(f"Warning: Failed to list hints: {exc}")
        return []
