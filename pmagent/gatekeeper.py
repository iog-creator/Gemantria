#!/usr/bin/env python3
"""
Gatekeeper - PoR + capability session + violation taxonomy.

Reuses guard logic from existing gatekeeper implementation.
"""

from __future__ import annotations

from typing import Any

from pmagent.gatekeeper.impl import build_capability_session


def create_capability_session(project_id: int, task_id: str, intent: str) -> dict[str, Any]:
    """Create a capability session for guarded tool execution.

    Args:
        project_id: Project ID.
        task_id: Task identifier (UUID string).
        intent: Intent description.

    Returns:
        Capability session dict.
    """
    return build_capability_session(project_id, task_id, intent)


def check_violations(result: dict[str, Any]) -> list[dict[str, Any]]:
    """Check for violations in tool execution result.

    Args:
        result: Tool execution result dict.

    Returns:
        List of violation dicts (empty if no violations).
    """
    violations: list[dict[str, Any]] = []

    # Basic violation checks
    if not result.get("ok", False):
        violations.append({"code": "TOOL_ERROR", "severity": "ERROR", "message": "Tool execution failed"})

    # Add more violation checks as needed
    # (e.g., schema validation, budget limits, etc.)

    return violations
