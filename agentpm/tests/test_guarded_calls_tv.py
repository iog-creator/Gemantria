import pytest
from agentpm.guard.impl import GuardError, validate_first_response, validate_tool_call


def test_tv_01_missing_por_block():
    session = {"por_token": "por-abcdef12"}
    first_msg = {"por_token": "por-xxxxxxx"}  # mismatch
    with pytest.raises(GuardError):
        validate_first_response(first_msg, session)


def test_tv_02_forbidden_tool_block():
    session = {"allowed_tool_ids": [1, 2]}
    call = {"tool_id": 7, "ring": 1, "args": {}}
    with pytest.raises(GuardError):
        validate_tool_call(call, session, {"required_args": []})


def test_tv_03_arg_schema_invalid_block():
    session = {"allowed_tool_ids": [1]}
    call = {"tool_id": 1, "ring": 1, "args": {"foo": "bar"}}
    with pytest.raises(GuardError):
        validate_tool_call(call, session, {"required_args": ["query"]})


def test_tv_04_ring_violation_fatal():
    session = {"allowed_tool_ids": [1]}
    call = {"tool_id": 1, "ring": 2, "args": {}}
    with pytest.raises(GuardError):
        validate_tool_call(call, session, {"required_args": []})


def test_tv_05_bus_parity_placeholder():
    assert True
