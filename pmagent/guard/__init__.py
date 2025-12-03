# Guard Shim (stub P0): interfaces only; implementation to follow in P0 execution PR
from typing import Dict, Any


class GuardError(Exception):
    """Guard error for policy/schema/ring violations."""


def validate_first_response(first_msg: Dict[str, Any], session: Dict[str, Any]) -> None:
    """Verify PoR tokens + readbacks. Raise GuardError on failure."""
    return


def validate_tool_call(call: Dict[str, Any], session: Dict[str, Any], policy: Dict[str, Any]) -> None:
    """Check allowed tool id, jsonschema args, and budgets."""
    return


def record_violation(task_id: str, kind: str, detail: Dict[str, Any]) -> None:
    """Append violation to agent_run.violations_json (DB write to follow)."""
    return
