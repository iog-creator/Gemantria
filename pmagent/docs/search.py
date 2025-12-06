"""Documentation search via control-plane embeddings.

This module provides semantic search over governance/docs content stored in
the control-plane (control.doc_embedding + control.doc_fragment + control.doc_registry).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict

# Add project root to path for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

from pmagent.adapters import lm_studio
from pmagent.db.loader import get_control_engine
from scripts.config.env import get_retrieval_lane_models


def _get_retrieval_embedding_model() -> str:
    """Resolve embedding model for retrieval lane (profile-aware)."""
    lane = get_retrieval_lane_models()
    model = lane.get("embedding_model")
    if not model:
        raise RuntimeError("No EMBEDDING_MODEL configured for retrieval lane")
    return model


def search_docs(
    query: str,
    k: int = 10,
    model_name: str | None = None,
    tier0_only: bool = True,
) -> Dict[str, object]:
    """
    Search governance/docs content via semantic similarity.

    Args:
        query: Search query text
        k: Number of results to return (default: 10)
        model_name: Embedding model name (defaults to config)
        tier0_only: If True, only search Tier-0 docs (AGENTS_ROOT + AGENTS::*)

    Returns:
        Dict with:
            - ok: bool
            - query: str
            - model_name: str
            - results: List[Dict] with logical_name, score, fragment_type, content (snippet)
            - error: str (if ok=False)
    """
    result: Dict[str, object] = {
        "ok": False,
        "query": query,
        "model_name": "",
        "results": [],
        "error": "",
    }

    # Get model name
    try:
        model = model_name or _get_retrieval_embedding_model()
        result["model_name"] = model
    except Exception as e:
        result["error"] = f"Failed to get embedding model: {e}"
        return result

    # Generate query embedding
    try:
        embeddings = lm_studio.embed(query, model_slot="embedding")
        if not embeddings or not embeddings[0]:
            result["error"] = "Failed to generate query embedding"
            return result
        query_embedding = embeddings[0]
    except Exception as e:
        result["error"] = f"Failed to generate embedding: {e}"
        return result

    # Pad to 1024 dimensions if needed (granite-embedding:278m returns 768)
    if len(query_embedding) == 768:
        query_embedding = query_embedding + [0.0] * (1024 - 768)
    elif len(query_embedding) != 1024:
        result["error"] = f"Unsupported embedding dimension: {len(query_embedding)}. Expected 768 or 1024."
        return result

    # Convert to JSON string for pgvector
    embedding_json = json.dumps(query_embedding)

    # Connect to DB and run similarity search
    try:
        engine = get_control_engine()
    except Exception as e:
        result["error"] = f"Failed to connect to control DB: {e}"
        return result

    try:
        with engine.connect() as conn:
            # Build query with optional Tier-0 filter
            tier0_filter = ""
            if tier0_only:
                tier0_filter = """
                    AND (dr.logical_name = 'AGENTS_ROOT' OR dr.logical_name LIKE 'AGENTS::%')
                """

            query_sql = text(
                f"""
                SELECT
                    dr.logical_name,
                    df.fragment_type,
                    df.content,
                    1 - (e.embedding <-> CAST(:query_embedding AS vector)) AS score
                FROM control.doc_embedding e
                INNER JOIN control.doc_fragment df ON df.id = e.fragment_id
                INNER JOIN control.doc_registry dr ON dr.doc_id = df.doc_id
                WHERE e.model_name = :model_name
                  AND dr.is_ssot = TRUE
                  AND dr.enabled = TRUE
                  {tier0_filter}
                ORDER BY e.embedding <-> CAST(:query_embedding AS vector)
                LIMIT :k
                """
            )

            rows = conn.execute(
                query_sql,
                {
                    "query_embedding": embedding_json,
                    "model_name": model,
                    "k": k,
                },
            ).fetchall()

            # Format results
            results = []
            for row in rows:
                logical_name, fragment_type, content, score = row
                # Extract snippet (first ~200 chars)
                snippet = content[:200] if content else ""
                if len(content) > 200:
                    snippet += "..."

                results.append(
                    {
                        "logical_name": logical_name,
                        "fragment_type": fragment_type,
                        "score": float(score),
                        "content": snippet,
                    }
                )

            result["ok"] = True
            result["results"] = results

    except Exception as e:
        result["error"] = f"Database query failed: {e}"
        return result

    return result
