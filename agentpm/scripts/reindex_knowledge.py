#!/usr/bin/env python3
"""
Reindex Knowledge Base Embeddings.

Scans control.kb_document for files and updates their embeddings using the configured provider.
"""

import sys
import logging
from pathlib import Path

# Add repo root to path for imports
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from sqlalchemy import text

from agentpm.db.loader import get_control_engine
from agentpm.knowledge.vector_store import VectorStore

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("reindex_knowledge")


def reindex_all(force: bool = False):
    """
    Reindex all documents in the knowledge base.

    Args:
        force: If True, re-embed even if embedding already exists.
    """
    engine = get_control_engine()
    store = VectorStore()

    logger.info("Starting knowledge base reindexing...")

    # Get all documents
    query = text("SELECT path, embedding FROM control.kb_document")

    with engine.connect() as conn:
        rows = conn.execute(query).fetchall()

    total = len(rows)
    logger.info(f"Found {total} documents in registry.")

    success_count = 0
    skip_count = 0
    fail_count = 0

    for i, row in enumerate(rows):
        path = row[0]
        has_embedding = row[1] is not None

        if has_embedding and not force:
            skip_count += 1
            continue

        logger.info(f"[{i + 1}/{total}] Processing {path}...")

        # Read file content
        try:
            file_path = Path(path)
            if not file_path.exists():
                logger.warning(f"File not found: {path}")
                fail_count += 1
                continue

            content = file_path.read_text(encoding="utf-8")

            # Upsert embedding
            if store.upsert_embedding(path, content):
                success_count += 1
            else:
                logger.error(f"Failed to generate embedding for {path}")
                fail_count += 1

        except Exception as e:
            logger.error(f"Error processing {path}: {e}")
            fail_count += 1

    logger.info("Reindexing complete.")
    logger.info(f"Success: {success_count}")
    logger.info(f"Skipped: {skip_count}")
    logger.info(f"Failed: {fail_count}")


if __name__ == "__main__":
    force_reindex = "--force" in sys.argv
    reindex_all(force=force_reindex)
