import os
from unittest.mock import patch

from src.graph.graph import PipelineState
from src.infra.checkpointer import get_checkpointer, PostgresCheckpointer


def test_memory_checkpointer_default():
    """Test that memory checkpointer is used by default."""
    checkpointer = get_checkpointer()
    assert checkpointer.__class__.__name__ == "InMemorySaver"


def test_postgres_checkpointer_with_env():
    """Test Postgres checkpointer when CHECKPOINTER=postgres and DSN is set."""
    mock_dsn = "postgresql://test:test@localhost/test"

    with patch.dict(os.environ, {"CHECKPOINTER": "postgres", "GEMATRIA_DSN": mock_dsn}):
        checkpointer = get_checkpointer()
        assert isinstance(checkpointer, PostgresCheckpointer)


def test_postgres_checkpointer_missing_dsn():
    """Test that Postgres checkpointer raises error when DSN is missing."""
    with patch.dict(os.environ, {"CHECKPOINTER": "postgres"}, clear=True):
        try:
            get_checkpointer()
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "GEMATRIA_DSN" in str(e)


def test_postgres_checkpointer_not_implemented():
    """Test that Postgres checkpointer raises NotImplementedError for operations."""
    mock_dsn = "postgresql://test:test@localhost/test"
    checkpointer = PostgresCheckpointer(mock_dsn)

    config = {"configurable": {"thread_id": "test"}}

    try:
        checkpointer.get_tuple(config)
        raise AssertionError("Should have raised NotImplementedError")
    except NotImplementedError:
        pass


def test_checkpointer_instantiation():
    """Test that checkpointer can be instantiated without errors."""
    checkpointer = get_checkpointer()
    # Basic smoke test - checkpointer should be created successfully
    assert checkpointer is not None
    assert hasattr(checkpointer, 'put')
    assert hasattr(checkpointer, 'get')
