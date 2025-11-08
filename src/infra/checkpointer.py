# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from typing import Any

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

try:
    import psycopg

    HAS_DB = True
except Exception:  # pragma: no cover
    HAS_DB = False

WORKFLOW_ID = os.getenv("WORKFLOW_ID", "gemantria.v1")


class PostgresCheckpointer(BaseCheckpointSaver):
    """Full LangGraph-compatible Postgres checkpointer implementation."""

    def __init__(self, conn_string: str):
        if not conn_string:
            raise RuntimeError("GEMATRIA_DSN required for PostgresCheckpointer")
        if not HAS_DB:
            raise RuntimeError("psycopg not available in this environment")
        self.conn_string = conn_string

    def _connect(self):
        return psycopg.connect(self.conn_string)

    def get_tuple(self, config: dict[str, Any]) -> Any:
        """Get latest checkpoint tuple for thread."""
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return None

        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT checkpoint, metadata, parent_checkpoint_id
                FROM checkpointer_state
                WHERE workflow = %s AND thread_id = %s
                ORDER BY created_at DESC, checkpoint_id DESC
                LIMIT 1
                """,
                (WORKFLOW_ID, thread_id),
            )
            row = cur.fetchone()
            if not row:
                return None

            checkpoint, metadata, parent_checkpoint_id = row
            parent_config = (
                {
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_id": parent_checkpoint_id,
                    }
                }
                if parent_checkpoint_id
                else None
            )
            return (checkpoint, metadata, parent_config)

    def list(self, config: dict[str, Any], *, before: Any = None, limit: int | None = None) -> Iterator[Any]:
        """List checkpoints for thread with pagination."""
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return

        with self._connect() as conn, conn.cursor() as cur:
            if before:
                # Use before as exclusive upper bound
                before_created_at, before_checkpoint_id = before
                cur.execute(
                    """
                    SELECT checkpoint_id, checkpoint, metadata, parent_checkpoint_id, created_at
                    FROM checkpointer_state
                    WHERE workflow = %s AND thread_id = %s
                      AND (created_at, checkpoint_id) < (%s, %s)
                    ORDER BY created_at DESC, checkpoint_id DESC
                    LIMIT %s
                    """,
                    (
                        WORKFLOW_ID,
                        thread_id,
                        before_created_at,
                        before_checkpoint_id,
                        limit,
                    ),
                )
            else:
                cur.execute(
                    """
                    SELECT checkpoint_id, checkpoint, metadata, parent_checkpoint_id, created_at
                    FROM checkpointer_state
                    WHERE workflow = %s AND thread_id = %s
                    ORDER BY created_at DESC, checkpoint_id DESC
                    LIMIT %s
                    """,
                    (WORKFLOW_ID, thread_id, limit),
                )

            for row in cur:
                (
                    checkpoint_id,
                    checkpoint,
                    metadata,
                    parent_checkpoint_id,
                    created_at,
                ) = row
                config_out = {
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_id": checkpoint_id,
                    }
                }
                parent_config = (
                    {
                        "configurable": {
                            "thread_id": thread_id,
                            "checkpoint_id": parent_checkpoint_id,
                        }
                    }
                    if parent_checkpoint_id
                    else None
                )
                yield (config_out, checkpoint, metadata, parent_config, created_at)

    def put(
        self,
        config: dict[str, Any],
        checkpoint: dict[str, Any],
        metadata: dict[str, Any],
    ) -> Any:
        """Store checkpoint with atomic upsert."""
        thread_id = config.get("configurable", {}).get("thread_id")
        checkpoint_id = config.get("configurable", {}).get("checkpoint_id")
        if not thread_id or not checkpoint_id:
            raise ValueError("thread_id and checkpoint_id required in config")

        parent_checkpoint_id = checkpoint.get("config", {}).get("configurable", {}).get("checkpoint_id")

        with self._connect() as conn, conn.cursor() as cur:
            # Atomic upsert
            cur.execute(
                """
                INSERT INTO checkpointer_state
                (workflow, thread_id, checkpoint_id, parent_checkpoint_id, checkpoint, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (workflow, thread_id, checkpoint_id)
                DO UPDATE SET
                    parent_checkpoint_id = EXCLUDED.parent_checkpoint_id,
                    checkpoint = EXCLUDED.checkpoint,
                    metadata = EXCLUDED.metadata,
                    created_at = NOW()
                """,
                (
                    WORKFLOW_ID,
                    thread_id,
                    checkpoint_id,
                    parent_checkpoint_id,
                    json.dumps(checkpoint),
                    json.dumps(metadata or {}),
                ),
            )
            conn.commit()

        return config

    def put_writes(self, config: dict[str, Any], writes: list[tuple[str, Any, Any]], task_id: str) -> Any:
        """Store pending writes."""
        thread_id = config.get("configurable", {}).get("thread_id")
        checkpoint_id = config.get("configurable", {}).get("checkpoint_id")
        if not thread_id or not checkpoint_id:
            raise ValueError("thread_id and checkpoint_id required in config")

        with self._connect() as conn, conn.cursor() as cur:
            for idx, (channel, value) in enumerate(writes):
                cur.execute(
                    """
                    INSERT INTO checkpointer_writes
                    (workflow, thread_id, checkpoint_id, task_id, idx, channel, value)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        WORKFLOW_ID,
                        thread_id,
                        checkpoint_id,
                        task_id,
                        idx,
                        channel,
                        json.dumps(value),
                    ),
                )
            conn.commit()

        return config


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
    """Get Postgres checkpointer (full implementation)."""
    dsn = os.getenv("GEMATRIA_DSN")
    if not dsn:
        raise RuntimeError("GEMATRIA_DSN environment variable required for postgres checkpointer")

    return PostgresCheckpointer(dsn)
