import jsonschema
from typing import Dict, Any, Iterable


class GuardError(Exception):
    """Guard error for policy/schema/ring/allowlist violations."""


def _require_keys(obj: Dict[str, Any], keys: Iterable[str], err: str) -> None:
    for k in keys:
        if k not in obj:
            raise GuardError(f"{err}: missing '{k}'")


def load_tool_schema(tool_id: str) -> Dict[str, Any] | None:
    """
    Load JSON schema for a tool from schemas/tools/ directory.
    Hermetic - loads local files only.
    """
    import pathlib
    import json

    schema_path = pathlib.Path("schemas") / "tools" / f"{tool_id}.input.v1.json"
    if not schema_path.exists():
        return None
    with open(schema_path) as f:
        schema = json.load(f)
    # Validate the schema itself
    jsonschema.Draft7Validator.check_schema(schema)
    return schema


def validate_jsonschema(call: Dict[str, Any], tool_schema: Dict[str, Any]) -> None:
    """
    Validate tool call args against JSON schema.
    PLAN-091: jsonschema validation for P0 tool I/O.
    """
    try:
        jsonschema.validate(call["args"], tool_schema)
    except jsonschema.ValidationError as e:
        raise GuardError(f"args.schema:{e.message}") from e


def validate_por(call: Dict[str, Any], session: Dict[str, Any]) -> None:
    """
    Proof-of-Readback (PoR): caller must echo back constraints/tokens.
    PLAN-091: PoR enforcement before tool execution.
    """
    expected_token = session.get("por_token")
    if expected_token is None:
        return  # PoR not required for this session

    actual_token = call.get("por_token")
    if actual_token != expected_token:
        raise GuardError("MISSING_POR")


def validate_tool_call_p0(call: Dict[str, Any], session: Dict[str, Any], policy: Dict[str, Any]) -> None:
    """
    PLAN-091 P0 validation: jsonschema + PoR + legacy checks.
    Enforce allowlist, ring, PoR, and schema validation for P0 tools.
    """
    _require_keys(call, ["tool_id", "ring", "args"], "call.invalid")

    # PoR check (PLAN-091 requirement)
    validate_por(call, session)

    # Allowlist check
    allowed = session.get("allowed_tool_ids", [])
    if call["tool_id"] not in allowed:
        raise GuardError("forbidden.tool")

    # Ring check
    if call["ring"] != 1:
        raise GuardError("ring.violation")

    # Schema validation (PLAN-091 requirement - jsonschema for P0)
    tool_schema = load_tool_schema(call["tool_id"])
    if tool_schema:
        validate_jsonschema(call, tool_schema)

    # Legacy required args check (for compatibility)
    required_args = policy.get("required_args", [])
    if not isinstance(call["args"], dict):
        raise GuardError("args.invalid-type")
    for rk in required_args:
        if rk not in call["args"]:
            raise GuardError(f"args.missing:{rk}")


def guarded_call_p0(tool_id: str, args: Dict[str, Any], session: Dict[str, Any]) -> Dict[str, Any]:
    """
    PLAN-091 P0 guarded call entry point.
    Returns structured result with por_ok, schema_ok, provenance_ok, violations.
    """
    # Include PoR token in call if session has one
    call = {"tool_id": tool_id, "ring": 1, "args": args}
    if "por_token" in session:
        call["por_token"] = session["por_token"]

    violations = []

    # Apply all validations
    try:
        validate_tool_call_p0(call, session, {})  # Empty policy for now
        por_ok = True
        schema_ok = True
        provenance_ok = True
    except GuardError as e:
        violations.append(str(e))
        por_ok = "MISSING_POR" not in str(e)
        schema_ok = "args.schema" not in str(e)
        provenance_ok = True  # Placeholder for future provenance checks

    return {
        "por_ok": por_ok,
        "schema_ok": schema_ok,
        "provenance_ok": provenance_ok,
        "violations": violations,
        "call": call,
    }


# Legacy compatibility - keep existing functions
validate_first_response = validate_por  # Alias for backward compatibility
validate_tool_call = validate_tool_call_p0  # Update to use P0 validation


def record_violation(task_id: str, kind: str, detail: Dict[str, Any]) -> None:
    """
    Stubbed — in STRICT/tag lanes this would append to DB (mcp_agent_run.violations_json).
    Hermetic by design in PR CI.
    """
    return
