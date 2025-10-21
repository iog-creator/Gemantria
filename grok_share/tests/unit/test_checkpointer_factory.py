import os
from unittest.mock import patch

import pytest

from src.infra.checkpointer import PostgresCheckpointer, get_checkpointer


def test_invalid_checkpointer_env_defaults_to_memory():
    """Test that invalid CHECKPOINTER value defaults to memory checkpointer."""
    with patch.dict(os.environ, {"CHECKPOINTER": "invalid"}, clear=True):
        checkpointer = get_checkpointer()
        # Should default to memory saver for unknown values
        assert checkpointer.__class__.__name__ == "InMemorySaver"


def test_postgres_missing_dsn_raises_error():
    """Test that postgres checkpointer without DSN raises clear error."""
    with (
        patch.dict(os.environ, {"CHECKPOINTER": "postgres"}, clear=True),
        pytest.raises(ValueError, match="GEMATRIA_DSN.*required")
    ):
        get_checkpointer()


def test_memory_checkpointer_has_required_methods():
    """Test that memory checkpointer exposes required methods."""
    with patch.dict(os.environ, {}, clear=True):  # Default to memory
        checkpointer = get_checkpointer()
        # Check that it has the basic methods needed for checkpointing
        assert hasattr(checkpointer, 'get')
        assert hasattr(checkpointer, 'put')
        # Note: MemorySaver might not have 'flush' but should have core methods


def test_postgres_checkpointer_method_signatures():
    """Test that postgres checkpointer has expected method signatures."""
    checkpointer = PostgresCheckpointer("test://dsn")

    # Test that all methods exist (even though they raise NotImplementedError)
    assert hasattr(checkpointer, 'get_tuple')
    assert hasattr(checkpointer, 'list')
    assert hasattr(checkpointer, 'put')
    assert hasattr(checkpointer, 'put_writes')

    # Test that they raise NotImplementedError when called
    config = {"configurable": {"thread_id": "test"}}

    try:
        checkpointer.get_tuple(config)
        raise AssertionError("Should raise NotImplementedError")
    except NotImplementedError:
        pass

    try:
        checkpointer.list(config)
        raise AssertionError("Should raise NotImplementedError")
    except NotImplementedError:
        pass

    try:
        checkpointer.put(config, {}, {})
        raise AssertionError("Should raise NotImplementedError")
    except NotImplementedError:
        pass

    try:
        checkpointer.put_writes(config, [], "task")
        raise AssertionError("Should raise NotImplementedError")
    except NotImplementedError:
        pass
