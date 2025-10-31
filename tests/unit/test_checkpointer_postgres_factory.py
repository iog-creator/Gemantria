import os
from unittest.mock import patch

import pytest

from src.infra.checkpointer import get_checkpointer


def test_factory_memory_default():
    with patch.dict(os.environ, {"CHECKPOINTER": ""}, clear=True):
        cp = get_checkpointer()
        assert cp.__class__.__name__ == "InMemorySaver"


def test_factory_unknown_uses_memory():
    with patch.dict(os.environ, {"CHECKPOINTER": "bogus"}, clear=True):
        cp = get_checkpointer()
        assert cp.__class__.__name__ == "InMemorySaver"


def test_factory_postgres_missing_dsn_raises_runtime_error():
    with (
        patch.dict(os.environ, {"CHECKPOINTER": "postgres"}, clear=True),
        pytest.raises(RuntimeError, match="GEMATRIA_DSN environment variable required"),
    ):
        get_checkpointer()
