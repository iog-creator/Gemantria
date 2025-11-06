"""
Runs ledger for pipeline execution tracking.

Manages pipeline runs with versions, evidence, and status tracking.
Integrates with checkpointer for node-level snapshots.

Related Rules: Rule-039 (Execution Contract), Rule-050 (OPS Contract)
Related ADRs: ADR-004 (Postgres Checkpointer), ADR-019 (Data Contracts)
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime
from typing import Any

# Status values
STATUS_RUNNING = "running"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_CANCELLED = "cancelled"


def _compute_sha256_12(data: Any) -> str:
    """Compute first 12 characters of SHA-256 hash for evidence tracking."""
    if isinstance(data, str):
        content = data.encode("utf-8")
    else:
        content = json.dumps(data, sort_keys=True).encode("utf-8")
    return hashlib.sha256(content).hexdigest()[:12]


def create_run(book: str, versions: dict[str, Any] | None = None) -> str:
    """
    Create a new pipeline run and return run_id.

    Args:
        book: Book name being processed
        versions: Dictionary of version information (model versions, schema versions, etc.)

    Returns:
        run_id: UUID string for the run
    """
    import psycopg

    run_id = str(uuid.uuid4())
    dsn = os.getenv("GEMATRIA_DSN")
    if not dsn:
        raise RuntimeError("GEMATRIA_DSN not set")

    versions_json = json.dumps(versions or {})
    evidence_json = json.dumps([])

    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO runs (run_id, book, status, versions, evidence)
            VALUES (%s, %s, %s, %s::jsonb, %s::jsonb)
            """,
            (run_id, book, STATUS_RUNNING, versions_json, evidence_json),
        )
        conn.commit()

    return run_id


def update_run_status(run_id: str, status: str, finished_at: datetime | None = None):
    """
    Update run status and optionally set finished_at timestamp.

    Args:
        run_id: Run UUID
        status: New status (running, completed, failed, cancelled)
        finished_at: Optional completion timestamp
    """
    import psycopg

    dsn = os.getenv("GEMATRIA_DSN")
    if not dsn:
        raise RuntimeError("GEMATRIA_DSN not set")

    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        if finished_at:
            cur.execute(
                """
                UPDATE runs
                SET status = %s, finished_at = %s, updated_at = NOW()
                WHERE run_id = %s
                """,
                (status, finished_at, run_id),
            )
        else:
            cur.execute(
                """
                UPDATE runs
                SET status = %s, updated_at = NOW()
                WHERE run_id = %s
                """,
                (status, run_id),
            )
        conn.commit()


def add_run_evidence(run_id: str, artifact_type: str, artifact_data: Any):
    """
    Add evidence artifact to run (sha256_12 hash for integrity verification).

    Args:
        run_id: Run UUID
        artifact_type: Type of artifact (e.g., 'graph', 'stats', 'envelope')
        artifact_data: Artifact content (will be hashed)
    """
    import psycopg

    dsn = os.getenv("GEMATRIA_DSN")
    if not dsn:
        raise RuntimeError("GEMATRIA_DSN not set")

    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        # Get current evidence
        cur.execute("SELECT evidence FROM runs WHERE run_id = %s", (run_id,))
        result = cur.fetchone()
        if not result:
            return

        evidence = json.loads(result[0] or "[]")
        sha256_12 = _compute_sha256_12(artifact_data)

        evidence.append({"type": artifact_type, "sha256_12": sha256_12})

        cur.execute(
            """
            UPDATE runs
            SET evidence = %s::jsonb, updated_at = NOW()
            WHERE run_id = %s
            """,
            (json.dumps(evidence), run_id),
        )
        conn.commit()


def save_checkpoint(run_id: str, node: str, payload: dict[str, Any]):
    """
    Save a checkpoint snapshot for a specific node in the pipeline.

    Args:
        run_id: Run UUID
        node: Node name (e.g., 'ai.nouns', 'ai.enrich', 'graph.build')
        payload: Checkpoint state data
    """
    import psycopg

    dsn = os.getenv("GEMATRIA_DSN")
    if not dsn:
        # Skip checkpoint if no DB configured (e.g., in CI/test mode)
        return

    payload_json = json.dumps(payload)

    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO checkpoints (run_id, node, payload)
            VALUES (%s, %s, %s::jsonb)
            """,
            (run_id, node, payload_json),
        )
        conn.commit()


def get_latest_checkpoint(run_id: str, node: str) -> dict[str, Any] | None:
    """
    Get the latest checkpoint for a specific node in a run.

    Args:
        run_id: Run UUID
        node: Node name

    Returns:
        Checkpoint payload or None if not found
    """
    import psycopg

    dsn = os.getenv("GEMATRIA_DSN")
    if not dsn:
        return None

    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT payload FROM checkpoints
            WHERE run_id = %s AND node = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (run_id, node),
        )
        result = cur.fetchone()

        if result:
            return json.loads(result[0])
    return None


def get_run_info(run_id: str) -> dict[str, Any] | None:
    """
    Get run information including status, versions, and evidence.

    Args:
        run_id: Run UUID

    Returns:
        Run information dictionary or None if not found
    """
    import psycopg

    dsn = os.getenv("GEMATRIA_DSN")
    if not dsn:
        return None

    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT run_id, book, started_at, finished_at, status, versions, evidence
            FROM runs
            WHERE run_id = %s
            """,
            (run_id,),
        )
        result = cur.fetchone()

        if not result:
            return None

        row = result
        return {
            "run_id": row[0],
            "book": row[1],
            "started_at": row[2],
            "finished_at": row[3],
            "status": row[4],
            "versions": json.loads(row[5] or "{}"),
            "evidence": json.loads(row[6] or "[]"),
        }


def get_model_versions() -> dict[str, str]:
    """
    Get current model versions from environment variables.

    Returns:
        Dictionary of model names to versions
    """
    return {
        "theology_model": os.getenv("THEOLOGY_MODEL", "unknown"),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "unknown"),
        "reranker_model": os.getenv("RERANKER_MODEL", "unknown"),
        "math_model": os.getenv("MATH_MODEL", "unknown"),
    }


def get_schema_version() -> str:
    """Get current schema version (from migration number or constant)."""
    # For now, return a constant; can be enhanced to read from migration metadata
    return "v1.0"
