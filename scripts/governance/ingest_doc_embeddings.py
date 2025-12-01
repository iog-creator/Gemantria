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
from pathlib import Path
from typing import List

# Add project root to path for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

from agentpm.adapters import lm_studio
from agentpm.db.loader import get_control_engine
from scripts.config.env import get_retrieval_lane_models


REPO_ROOT = Path(__file__).resolve().parents[2]


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
    limit: int | None = None,
) -> List[dict]:
    """
    Query fragments that don't have embeddings for the target model.

    Returns list of dicts with: fragment_id, doc_id, content, fragment_index.
    """
    # Build WHERE clause for Tier-0 docs
    where_clauses = []
    if only_agents:
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


def embed_fragments(fragments: List[dict], model_name: str, dry_run: bool = False) -> List[dict]:
    """
    Generate embeddings for fragments.

    Returns list of dicts with: fragment_id, embedding (list of floats).
    """
    if dry_run:
        # Return mock embeddings for dry-run
        return [{"fragment_id": f["fragment_id"], "embedding": [0.0] * 1024} for f in fragments]

    # Extract text content
    texts = [f["content"] for f in fragments]

    # Generate embeddings using the provider-aware adapter
    try:
        embeddings = lm_studio.embed(texts, model_slot="embedding")
    except Exception as e:
        raise RuntimeError(f"Failed to generate embeddings: {e}") from e

    # Validate embedding dimensions
    if not embeddings:
        raise RuntimeError("No embeddings returned from model")
    if len(embeddings) != len(fragments):
        raise RuntimeError(f"Embedding count mismatch: expected {len(fragments)}, got {len(embeddings)}")

    # Check dimension (should be 1024 for BGE-M3, but some models like granite-embedding:278m return 768)
    dim = len(embeddings[0])
    if dim not in (768, 1024):
        raise RuntimeError(
            f"Unsupported embedding dimension: {dim}. Expected 768 or 1024. "
            f"Please use a model that produces 768 or 1024-dimensional embeddings."
        )
    if dim != 1024:
        print(
            f"[WARN] Embedding dimension is {dim}, expected 1024. "
            f"Schema expects vector(1024); this may cause issues with pgvector.",
            file=sys.stderr,
        )

    # Combine fragment IDs with embeddings
    return [{"fragment_id": f["fragment_id"], "embedding": emb} for f, emb in zip(fragments, embeddings)]


def store_embeddings(conn, embeddings: List[dict], model_name: str, dry_run: bool = False) -> int:
    """Store embeddings in control.doc_embedding."""
    if dry_run:
        return len(embeddings)

    inserted = 0
    for emb_data in embeddings:
        fragment_id = emb_data["fragment_id"]
        embedding = emb_data["embedding"]

        # Convert embedding list to JSON string for pgvector
        # Use json.dumps() to match existing codebase patterns (see scripts/db/upsert_helpers.py)
        embedding_json = json.dumps(embedding)

        # Pad to 1024 dimensions if needed (granite-embedding:278m returns 768)
        embedding_list = embedding
        if len(embedding_list) == 768:
            # Pad with zeros to reach 1024 dimensions
            embedding_list = embedding_list + [0.0] * (1024 - 768)
            embedding_json = json.dumps(embedding_list)
            print(
                f"[INFO] Padded embedding from 768 to 1024 dimensions for fragment {fragment_id}",
                file=sys.stderr,
            )

        # Use text() with parameter binding for pgvector
        # Note: We use CAST instead of ::vector to avoid SQLAlchemy parameter binding issues
        insert_query = text(
            """
            INSERT INTO control.doc_embedding (fragment_id, model_name, embedding)
            VALUES (:fragment_id, :model_name, CAST(:embedding AS vector))
            ON CONFLICT (fragment_id, model_name) DO NOTHING
            """
        )

        conn.execute(
            insert_query,
            {
                "fragment_id": fragment_id,
                "model_name": model_name,
                "embedding": embedding_json,
            },
        )
        inserted += 1

    conn.commit()
    return inserted


def ingest_embeddings(
    dry_run: bool = False,
    only_agents: bool = True,
    limit: int | None = None,
    model_name: str | None = None,
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
        fragments = get_fragments_needing_embeddings(conn, model, only_agents, limit)

        if not fragments:
            return {
                "docs_processed": 0,
                "fragments_embedded": 0,
                "model_name": model,
                "dry_run": dry_run,
                "message": "No fragments need embeddings",
            }

        # Group by doc for stats
        docs_processed = len(set(f["doc_id"] for f in fragments))

        # Generate embeddings
        try:
            embedded_data = embed_fragments(fragments, model, dry_run)
        except RuntimeError as e:
            return {
                "error": str(e),
                "docs_processed": docs_processed,
                "fragments_embedded": 0,
                "model_name": model,
                "dry_run": dry_run,
            }

        # Store embeddings
        inserted = store_embeddings(conn, embedded_data, model, dry_run)

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
        "--model-name",
        type=str,
        help="Override default embedding model",
    )

    args = parser.parse_args()

    only_agents = args.only_agents and not args.all_tier0

    result = ingest_embeddings(
        dry_run=args.dry_run,
        only_agents=only_agents,
        limit=args.limit,
        model_name=args.model_name,
    )

    print(json.dumps(result, indent=2))

    if "error" in result:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
