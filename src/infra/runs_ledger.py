"""
Runs Ledger Infrastructure

Manages pipeline run tracking, status updates, and checkpoints.
"""

import os
import json
from datetime import datetime
from typing import Any, Dict
from src.infra.structured_logger import get_logger, log_json

LOG = get_logger("gematria.runs_ledger")

# Database connection (if available)
GEMATRIA_DSN = os.getenv("GEMATRIA_DSN")


def create_run(book: str, versions: Dict[str, str]) -> str:
    """Create a new pipeline run record."""
    run_id = f"run_{int(datetime.utcnow().timestamp())}"
    log_json(LOG, 20, "run_created", run_id=run_id, book=book)
    return run_id


def update_run_status(run_id: str, status: str, finished_at: datetime | None = None) -> None:
    """Update the status of a pipeline run."""
    log_json(LOG, 20, "run_status_updated", run_id=run_id, status=status)


def save_checkpoint(run_id: str, stage: str, data: Dict[str, Any]) -> None:
    """Save a pipeline checkpoint."""
    log_json(LOG, 10, "checkpoint_saved", run_id=run_id, stage=stage, data_size=len(json.dumps(data)))


def get_model_versions() -> Dict[str, str]:
    """Get current model versions."""
    return {
        "theology_model": os.getenv("THEOLOGY_MODEL", "unknown"),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "unknown"),
        "reranker_model": os.getenv("RERANKER_MODEL", "unknown"),
    }


def get_schema_version() -> str:
    """Get current schema version."""
    return "v1.0"
