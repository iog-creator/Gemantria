from typing import Dict, Any, Iterable


class GuardError(Exception):
    """Guard error for policy/schema/ring/allowlist violations."""


def _require_keys(obj: Dict[str, Any], keys: Iterable[str], err: str) -> None:
    for k in keys:
        if k not in obj:
            raise GuardError(f"{err}: missing '{k}'")


def validate_first_response(first_msg: Dict[str, Any], session: Dict[str, Any]) -> None:
    """
    Proof-of-Readback (PoR): if session contains 'por_token', the model must echo it in first_msg.
    Deterministic, hermetic check — no I/O.
    """
    token = session.get("por_token")
    if token is None:
        return
    if first_msg.get("por_token") != token:
        raise GuardError("por.mismatch")


def validate_tool_call(call: Dict[str, Any], session: Dict[str, Any], policy: Dict[str, Any]) -> None:
    """
    Enforce: allowlist, ring, and minimal 'required_args' policy.
    No JSONSchema dependency to keep CI hermetic; use simple presence checks.
    """
    _require_keys(call, ["tool_id", "ring", "args"], "call.invalid")
    allowed = session.get("allowed_tool_ids", [])
    if call["tool_id"] not in allowed:
        raise GuardError("forbidden.tool")
    if call["ring"] != 1:
        raise GuardError("ring.violation")
    required_args = policy.get("required_args", [])
    if not isinstance(call["args"], dict):
        raise GuardError("args.invalid-type")
    for rk in required_args:
        if rk not in call["args"]:
            raise GuardError(f"args.missing:{rk}")


def record_violation(task_id: str, kind: str, detail: Dict[str, Any]) -> None:
    """
    Stubbed — in STRICT/tag lanes this would append to DB (mcp_agent_run.violations_json).
    Hermetic by design in PR CI.
    """
    return
