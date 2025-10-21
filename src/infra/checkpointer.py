from __future__ import annotations

import os
from typing import Any

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver


# Simple postgres checkpointer implementation
class PostgresCheckpointer(BaseCheckpointSaver):
    """Simple Postgres checkpointer implementation."""

    def __init__(self, conn_string: str):
        self.conn_string = conn_string
        # TODO: Implement full postgres checkpointer in future PR
        # For now, this is a placeholder that raises NotImplementedError

    def get_tuple(self, config: dict[str, Any]) -> Any:
        raise NotImplementedError("Postgres checkpointer not yet implemented")

    def list(self, config: dict[str, Any], *, before: Any = None, limit: int | None = None) -> Any:
        raise NotImplementedError("Postgres checkpointer not yet implemented")

    def put(self, config: dict[str, Any], checkpoint: dict[str, Any], metadata: dict[str, Any]) -> Any:
        raise NotImplementedError("Postgres checkpointer not yet implemented")

    def put_writes(self, config: dict[str, Any], writes: list[tuple[str, Any, Any]], task_id: str) -> Any:
        raise NotImplementedError("Postgres checkpointer not yet implemented")


def get_checkpointer() -> MemorySaver | PostgresCheckpointer:
    """Get checkpointer based on CHECKPOINTER env var. Defaults to memory."""
    checkpointer_type = os.getenv("CHECKPOINTER", "memory").lower()

    if checkpointer_type == "postgres":
        return _get_postgres_checkpointer()
    else:
        return _get_memory_checkpointer()


def _get_memory_checkpointer() -> MemorySaver:
    """Get memory checkpointer (default for CI/development)."""
    return MemorySaver()


def _get_postgres_checkpointer() -> PostgresCheckpointer:
    """Get Postgres checkpointer (placeholder implementation)."""
    dsn = os.getenv("GEMATRIA_DSN")
    if not dsn:
        raise ValueError("GEMATRIA_DSN environment variable required for postgres checkpointer")

    return PostgresCheckpointer(dsn)
