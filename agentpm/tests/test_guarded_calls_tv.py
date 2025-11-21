import pytest
import json
from agentpm.guard.impl import GuardError, validate_por, validate_tool_call_p0, guarded_call_p0
from agentpm.gatekeeper.impl import execute_guarded_tool_call_p0


def test_tv_01_missing_por_block():
    """TV-01: MISSING_POR - PoR token mismatch blocks execution"""
    session = {"por_token": "por-abcdef12", "allowed_tool_ids": [1]}
    call = {"tool_id": 1, "ring": 1, "args": {}, "por_token": "por-xxxxxxx"}  # mismatch
    with pytest.raises(GuardError, match="MISSING_POR"):
        validate_por(call, session)


def test_tv_01_missing_por_success():
    """TV-01: PoR validation passes when tokens match"""
    session = {"por_token": "por-abcdef12", "allowed_tool_ids": [1]}
    call = {"tool_id": 1, "ring": 1, "args": {}, "por_token": "por-abcdef12"}  # match
    # Should not raise
    validate_por(call, session)


def test_tv_02_forbidden_tool_block():
    """TV-02: FORBIDDEN_TOOL - tool not in allowlist blocks execution"""
    session = {"allowed_tool_ids": [1, 2]}
    call = {"tool_id": 7, "ring": 1, "args": {}}  # tool 7 not allowed
    with pytest.raises(GuardError, match=r"forbidden\.tool"):
        validate_tool_call_p0(call, session, {"required_args": []})


def test_tv_03_bad_args_block():
    """TV-03: BAD_ARGS - missing required args blocks execution"""
    session = {"allowed_tool_ids": [1]}
    call = {"tool_id": 1, "ring": 1, "args": {"foo": "bar"}}  # missing required "query"
    with pytest.raises(GuardError, match=r"args\.missing:query"):
        validate_tool_call_p0(call, session, {"required_args": ["query"]})


def test_tv_04_ring_violation_block():
    """TV-04: RING_VIOLATION - wrong ring blocks execution"""
    session = {"allowed_tool_ids": [1]}
    call = {"tool_id": 1, "ring": 2, "args": {}}  # ring 2 instead of 1
    with pytest.raises(GuardError, match=r"ring\.violation"):
        validate_tool_call_p0(call, session, {"required_args": []})


def test_tv_05_bus_parity_placeholder():
    """TV-05: BUS_PARITY_PLACEHOLDER - placeholder for future bus parity checks"""
    # For now, this is a placeholder test that always passes
    # In future, this would validate bus parity constraints
    assert True


def test_guarded_call_p0_success():
    """P0 guarded call succeeds with valid inputs"""
    session = {"por_token": "por-test123", "allowed_tool_ids": ["test_tool"]}
    result = guarded_call_p0("test_tool", {"query": "test"}, session)

    assert result["por_ok"] is True
    assert result["schema_ok"] is True  # No schema file, so considered ok
    assert result["provenance_ok"] is True
    assert result["violations"] == []
    assert result["call"]["tool_id"] == "test_tool"


def test_guarded_call_p0_missing_por():
    """P0 guarded call fails with missing PoR"""
    session = {"por_token": "por-test123", "allowed_tool_ids": ["test_tool"]}
    # Manually create call without por_token to test PoR failure
    from agentpm.guard.impl import validate_tool_call_p0, GuardError

    call = {"tool_id": "test_tool", "ring": 1, "args": {"query": "test"}}  # No por_token
    try:
        validate_tool_call_p0(call, session, {})
        raise AssertionError("Should have raised GuardError")
    except GuardError as e:
        assert "MISSING_POR" in str(e)


def test_execute_guarded_tool_call_p0():
    """Gatekeeper P0 execution coordinates validation and returns result"""
    session = {"por_token": "por-test123", "allowed_tool_ids": ["test_tool"]}
    result = execute_guarded_tool_call_p0("test_tool", {"query": "test"}, session)

    # Should succeed with valid inputs
    assert result["por_ok"] is True
    assert result["executed"] is True
    assert result["call"]["tool_id"] == "test_tool"


def test_p0_jsonschema_validation():
    """Test jsonschema validation when schema file exists"""
    # Create a temporary schema file for testing
    import pathlib

    schema_dir = pathlib.Path("schemas/tools")
    schema_dir.mkdir(parents=True, exist_ok=True)

    # Create test schema
    test_schema = {
        "$id": "gemantria://v1/tools/test_tool.input.v1.json",
        "type": "object",
        "required": ["query"],
        "properties": {"query": {"type": "string"}},
    }

    schema_file = schema_dir / "test_tool.input.v1.json"
    schema_file.write_text(json.dumps(test_schema))

    try:
        session = {"por_token": "por-test123", "allowed_tool_ids": ["test_tool"]}
        # Valid args should pass
        result = guarded_call_p0("test_tool", {"query": "test"}, session)
        assert result["schema_ok"] is True

        # Invalid args should fail schema validation
        result = guarded_call_p0("test_tool", {"invalid": "args"}, session)
        assert result["schema_ok"] is False
        assert "args.schema" in str(result["violations"][0])

    finally:
        # Clean up
        if schema_file.exists():
            schema_file.unlink()


def test_tv_06_catalog_access_success():
    """TV-06: CATALOG_ACCESS_SUCCESS - End-to-end catalog access when available (PLAN-091 E103)"""
    pytest.importorskip("psycopg")  # Skip if psycopg not available

    from agentpm.adapters.mcp_db import catalog_read_ro

    # Test catalog read (should gracefully handle missing DB/view)
    result = catalog_read_ro()

    # Result should have expected structure
    assert isinstance(result, dict)
    assert "ok" in result
    assert "tools" in result
    assert "error" in result or result.get("ok") is True

    # If DB is available and view exists, should have tools
    if result.get("ok"):
        assert isinstance(result["tools"], list)
        # Each tool should have id, name, ring if present
        for tool in result["tools"]:
            assert isinstance(tool, dict)
            if tool:  # Non-empty tool entries
                assert "id" in tool
                assert "name" in tool
                assert "ring" in tool


def test_tv_07_guarded_catalog_call():
    """TV-07: GUARDED_CATALOG_CALL - Guarded call that accesses catalog when available (PLAN-091 E103)"""
    pytest.importorskip("psycopg")  # Skip if psycopg not available

    from agentpm.adapters.mcp_db import catalog_read_ro
    from agentpm.guard.impl import validate_por, validate_tool_call_p0

    # Test that we can make a "guarded" call to catalog access
    session = {"por_token": "por-catalog123", "allowed_tool_ids": ["catalog_read"]}

    # This is a synthetic call for testing - in real usage, this would come from tool execution
    call = {"tool_id": "catalog_read", "ring": 1, "args": {}, "por_token": "por-catalog123"}

    # Should pass PoR validation
    validate_por(call, session)

    # Should pass tool validation (minimal schema)
    validate_tool_call_p0(call, session, {"required_args": []})

    # Now actually try catalog access
    catalog_result = catalog_read_ro()

    # The call should complete (success or graceful failure)
    assert isinstance(catalog_result, dict)
    # Either succeeds with tools or fails gracefully with error
    assert catalog_result.get("ok") in [True, False]
