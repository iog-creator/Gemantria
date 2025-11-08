# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

"""
Infrastructure Runs Ledger

Manages pipeline run tracking and checkpointing.
"""

import os
import uuid
from datetime import datetime
from typing import Any, Dict

from src.persist.runs_ledger import mark_run_finished, mark_run_started


def create_run(book: str, versions: Dict[str, str]) -> str:
    """Create a new pipeline run and return its ID."""
    run_id = str(uuid.uuid4())

    # Mark run as started (tolerant if DSN missing)
    try:
        mark_run_started(run_id, book, notes=f"models: {versions}")
    except Exception:
        pass  # Tolerate missing DSN

    return run_id


def update_run_status(run_id: str, status: str, finished_at: datetime | None = None) -> None:
    """Update the status of a pipeline run."""
    notes = f"status: {status}"
    if finished_at:
        notes += f", finished_at: {finished_at.isoformat()}"

    # Mark run as finished (tolerant if DSN missing)
    try:
        mark_run_finished(run_id, notes=notes)
    except Exception:
        pass  # Tolerate missing DSN


def save_checkpoint(run_id: str, stage: str, data: Dict[str, Any]) -> None:
    """Save a checkpoint for the pipeline run at the given stage."""
    # For now, this is a no-op - checkpointing could be added later
    # The data would be persisted to track pipeline progress
    pass


def get_model_versions() -> Dict[str, str]:
    """Get the versions of models being used in the pipeline."""
    return {
        "embedding_model": os.getenv("EMBEDDING_MODEL", "unknown"),
        "reranker_model": os.getenv("RERANKER_MODEL", "unknown"),
        "theology_model": os.getenv("THEOLOGY_MODEL", "unknown"),
        "math_model": os.getenv("MATH_MODEL", "unknown"),
    }


def get_schema_version() -> str:
    """Get the current schema version for the pipeline."""
    return "v1.0"  # Placeholder - could be read from a version file
