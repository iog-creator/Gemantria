#!/usr/bin/env python

"""
Ingest document fragment embeddings into control.doc_embedding.

Purpose
-------
Read fragments from control.doc_fragment and generate embeddings for them,
storing the results in control.doc_embedding. This makes docs RAG-ready.

The script:
- Queries control.doc_fragment for fragments that don't have embeddings yet
- Focuses on Tier-0 docs (AGENTS*, MASTER_PLAN, RULES_INDEX, GPT_REFERENCE_GUIDE) by default
- Generates embeddings using the configured embedding model (Ollama or LM Studio)
- Stores embeddings in control.doc_embedding with pgvector format

This script does NOT:
- Modify source files
- Re-embed fragments that already have embeddings for the target model
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import List

# Add project root to path for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

from pmagent.adapters import lm_studio
from pmagent.db.loader import get_control_engine
from scripts.config.env import get_retrieval_lane_models


REPO_ROOT = Path(__file__).resolve().parents[2]

# Batch size for embedding generation and DB inserts
DEFAULT_EMBEDDING_BATCH_SIZE = 256  # Increased for better GPU throughput (16GB+ VRAM)
DEFAULT_DB_BATCH_SIZE = 100  # Batch size for DB inserts


def get_embedding_model(model_name: str | None = None) -> str:
    """Get embedding model name from config or override."""
    if model_name:
        return model_name
    cfg = get_retrieval_lane_models()
    model = cfg.get("embedding_model")
    if not model:
        raise RuntimeError("No EMBEDDING_MODEL configured. Set EMBEDDING_MODEL or a Granite override in .env")
    return model


def get_fragments_needing_embeddings(
    conn,
    model_name: str,
    only_agents: bool = True,
    all_docs: bool = False,
    limit: int | None = None,
) -> List[dict]:
    """
    Query fragments that don't have embeddings for the target model.

    Returns list of dicts with: fragment_id, doc_id, content, fragment_index.
    """
    # Build WHERE clause for Tier-0 docs
    where_clauses = []
    if all_docs:
        # Include all enabled documents (no filtering)
        where_clauses.append("dr.enabled = true")
    elif only_agents:
        where_clauses.append("(dr.logical_name = 'AGENTS_ROOT' OR dr.logical_name LIKE 'AGENTS::%')")
    else:
        # Include all Tier-0 docs
        where_clauses.append(
            """
            (dr.logical_name = 'AGENTS_ROOT'
             OR dr.logical_name LIKE 'AGENTS::%'
             OR dr.logical_name = 'MASTER_PLAN'
             OR dr.logical_name = 'RULES_INDEX'
             OR dr.logical_name = 'GPT_REFERENCE_GUIDE')
            """
        )

    where_sql = " AND ".join(where_clauses)

    limit_sql = ""
    if limit:
        limit_sql = f"LIMIT {limit}"

    query = text(
        f"""
        SELECT DISTINCT
            df.id AS fragment_id,
            df.doc_id,
            df.content,
            df.fragment_index,
            dr.logical_name
        FROM control.doc_fragment df
        INNER JOIN control.doc_registry dr ON df.doc_id = dr.doc_id
        LEFT JOIN control.doc_embedding de
            ON de.fragment_id = df.id
            AND de.model_name = :model_name
        WHERE de.id IS NULL
          AND df.content IS NOT NULL
          AND df.content != ''
          AND {where_sql}
        ORDER BY df.doc_id, df.fragment_index
        {limit_sql}
        """
    )

    result = conn.execute(query, {"model_name": model_name})
    rows = result.fetchall()

    return [
        {
            "fragment_id": str(row[0]),
            "doc_id": str(row[1]),
            "content": row[2],
            "fragment_index": row[3],
            "logical_name": row[4],
        }
        for row in rows
    ]


def embed_fragments(
    fragments: List[dict],
    model_name: str,
    dry_run: bool = False,
    batch_size: int = DEFAULT_EMBEDDING_BATCH_SIZE,
    show_progress: bool = True,
) -> List[dict]:
    """
    Generate embeddings for fragments in batches.

    Returns list of dicts with: fragment_id, embedding (list of floats).
    """
    if dry_run:
        # Return mock embeddings for dry-run
        return [{"fragment_id": f["fragment_id"], "embedding": [0.0] * 1024} for f in fragments]

    all_embeddings = []
    total = len(fragments)
    start_time = time.time()
    processed = 0

    # Process in batches for better performance and memory efficiency
    for batch_start in range(0, total, batch_size):
        batch_end = min(batch_start + batch_size, total)
        batch_fragments = fragments[batch_start:batch_end]
        texts = [f["content"] for f in batch_fragments]

        # Generate embeddings for this batch
        try:
            batch_embeddings = lm_studio.embed(texts, model_slot="embedding")
        except Exception as e:
            raise RuntimeError(f"Failed to generate embeddings for batch {batch_start}-{batch_end}: {e}") from e

        # Validate batch embeddings
        if not batch_embeddings:
            raise RuntimeError(f"No embeddings returned for batch {batch_start}-{batch_end}")
        if len(batch_embeddings) != len(batch_fragments):
            raise RuntimeError(
                f"Embedding count mismatch in batch {batch_start}-{batch_end}: "
                f"expected {len(batch_fragments)}, got {len(batch_embeddings)}"
            )

        # Check dimension (must be 1024-D - canonical format required)
        dim = len(batch_embeddings[0])
        if dim != 1024:
            raise RuntimeError(
                f"Critical violation: Embedding dimension is {dim}, expected 1024. "
                f"Legacy 768-D embeddings are not allowed. "
                f"Please use a model that produces 1024-dimensional embeddings."
            )

        # Combine fragment IDs with embeddings
        batch_results = [
            {"fragment_id": f["fragment_id"], "embedding": emb} for f, emb in zip(batch_fragments, batch_embeddings)
        ]
        all_embeddings.extend(batch_results)
        processed = batch_end

        # Progress output
        if (show_progress and processed % 100 == 0) or batch_end == total:
            elapsed = time.time() - start_time
            rate = processed / elapsed if elapsed > 0 else 0
            remaining = total - processed
            eta = remaining / rate if rate > 0 else 0
            pct = (processed / total) * 100
            print(
                f"[PROGRESS] {processed:,}/{total:,} ({pct:.1f}%) | Rate: {rate:.1f}/s | ETA: {eta / 60:.1f}m",
                file=sys.stderr,
                flush=True,
            )

    return all_embeddings


def store_embeddings(
    conn,
    embeddings: List[dict],
    model_name: str,
    dry_run: bool = False,
    batch_size: int = DEFAULT_DB_BATCH_SIZE,
) -> int:
    """Store embeddings in control.doc_embedding using bulk inserts."""
    if dry_run:
        return len(embeddings)

    inserted = 0
    total = len(embeddings)

    # Process in batches for better performance
    for batch_start in range(0, total, batch_size):
        batch_end = min(batch_start + batch_size, total)
        batch_embeddings = embeddings[batch_start:batch_end]

        # Prepare batch data
        batch_data = []
        for emb_data in batch_embeddings:
            fragment_id = emb_data["fragment_id"]
            embedding = emb_data["embedding"]
            embedding_json = json.dumps(embedding)
            batch_data.append(
                {
                    "fragment_id": fragment_id,
                    "model_name": model_name,
                    "embedding": embedding_json,
                }
            )

        # Bulk insert using executemany
        insert_query = text(
            """
            INSERT INTO control.doc_embedding (fragment_id, model_name, embedding)
            VALUES (:fragment_id, :model_name, CAST(:embedding AS vector))
            ON CONFLICT (fragment_id, model_name) DO NOTHING
            """
        )

        result = conn.execute(insert_query, batch_data)
        inserted += result.rowcount if hasattr(result, "rowcount") else len(batch_data)

    conn.commit()
    return inserted


def ingest_embeddings(
    dry_run: bool = False,
    only_agents: bool = True,
    all_docs: bool = False,
    limit: int | None = None,
    model_name: str | None = None,
    embedding_batch_size: int = DEFAULT_EMBEDDING_BATCH_SIZE,
    db_batch_size: int = DEFAULT_DB_BATCH_SIZE,
    show_progress: bool = True,
) -> dict:
    """
    Main ingestion function.

    Returns dict with stats: docs_processed, fragments_embedded, model_name, dry_run.
    """
    try:
        model = get_embedding_model(model_name)
    except RuntimeError as e:
        return {
            "error": str(e),
            "docs_processed": 0,
            "fragments_embedded": 0,
            "model_name": None,
            "dry_run": dry_run,
        }

    try:
        engine = get_control_engine()
    except Exception as e:
        return {
            "error": f"DB connection failed: {e}",
            "docs_processed": 0,
            "fragments_embedded": 0,
            "model_name": model,
            "dry_run": dry_run,
        }

    with engine.connect() as conn:
        # Get fragments needing embeddings
        fragments = get_fragments_needing_embeddings(conn, model, only_agents, all_docs, limit)

        if not fragments:
            if show_progress:
                print("[INFO] No fragments need embeddings", file=sys.stderr)
            return {
                "docs_processed": 0,
                "fragments_embedded": 0,
                "model_name": model,
                "dry_run": dry_run,
                "message": "No fragments need embeddings",
            }

        # Group by doc for stats
        docs_processed = len(set(f["doc_id"] for f in fragments))
        total_fragments = len(fragments)

        if show_progress:
            print(
                f"[INFO] Processing {total_fragments:,} fragments from {docs_processed} docs "
                f"(embedding batch: {embedding_batch_size}, DB batch: {db_batch_size})",
                file=sys.stderr,
            )

        start_time = time.time()

        # Generate embeddings
        try:
            embedded_data = embed_fragments(fragments, model, dry_run, embedding_batch_size, show_progress)
            if show_progress:
                elapsed = time.time() - start_time
                print(
                    f"[INFO] Generated {len(embedded_data):,} embeddings in {elapsed:.1f}s "
                    f"({len(embedded_data) / elapsed:.1f} embeddings/s)",
                    file=sys.stderr,
                )
        except RuntimeError as e:
            return {
                "error": str(e),
                "docs_processed": docs_processed,
                "fragments_embedded": 0,
                "model_name": model,
                "dry_run": dry_run,
            }

        # Store embeddings
        store_start = time.time()
        inserted = store_embeddings(conn, embedded_data, model, dry_run, db_batch_size)
        if show_progress:
            store_elapsed = time.time() - store_start
            total_elapsed = time.time() - start_time
            print(
                f"[INFO] Stored {inserted:,} embeddings in {store_elapsed:.1f}s "
                f"({inserted / store_elapsed:.1f} inserts/s) | Total: {total_elapsed:.1f}s",
                file=sys.stderr,
            )

        return {
            "docs_processed": docs_processed,
            "fragments_embedded": inserted,
            "model_name": model,
            "dry_run": dry_run,
        }


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Ingest document fragment embeddings into control.doc_embedding")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log which fragments would be embedded, no DB writes",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Cap number of fragments processed",
    )
    parser.add_argument(
        "--only-agents",
        action="store_true",
        default=True,
        help="Restrict to AGENTS docs (default: True)",
    )
    parser.add_argument(
        "--all-tier0",
        action="store_true",
        help="Include all Tier-0 docs (AGENTS, MASTER_PLAN, RULES_INDEX, GPT_REFERENCE_GUIDE)",
    )
    parser.add_argument(
        "--all-docs",
        action="store_true",
        help="Include all enabled documents (overrides --only-agents and --all-tier0)",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        help="Override default embedding model",
    )
    parser.add_argument(
        "--embedding-batch-size",
        type=int,
        default=DEFAULT_EMBEDDING_BATCH_SIZE,
        help=f"Batch size for embedding generation (default: {DEFAULT_EMBEDDING_BATCH_SIZE})",
    )
    parser.add_argument(
        "--db-batch-size",
        type=int,
        default=DEFAULT_DB_BATCH_SIZE,
        help=f"Batch size for DB inserts (default: {DEFAULT_DB_BATCH_SIZE})",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress indicators",
    )

    args = parser.parse_args()

    only_agents = args.only_agents and not args.all_tier0 and not args.all_docs

    result = ingest_embeddings(
        dry_run=args.dry_run,
        only_agents=only_agents,
        all_docs=args.all_docs,
        limit=args.limit,
        model_name=args.model_name,
        embedding_batch_size=args.embedding_batch_size,
        db_batch_size=args.db_batch_size,
        show_progress=not args.no_progress,
    )

    print(json.dumps(result, indent=2))

    if "error" in result:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
