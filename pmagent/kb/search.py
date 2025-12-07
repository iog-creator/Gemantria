"""
Code Search Module (Layer 4 Phase 4.5)

Purpose: Semantic code search using pgvector embeddings.

Enables queries like "find code that does X" through semantic similarity search.
"""

from __future__ import annotations

import json
from typing import Any

from pmagent.adapters.lm_studio import embed
from pmagent.db.loader import get_control_engine
from sqlalchemy import text


def search_code(
    query: str,
    k: int = 10,
    subsystem: str | None = None,
    model_name: str | None = None,
) -> dict[str, Any]:
    """
    Search code fragments using semantic similarity.

    Layer 4 Phase 4.5: Code search via pgvector.

    Args:
        query: Search query (e.g., "Hebrew gematria calculation")
        k: Number of results to return (default: 10)
        subsystem: Optional subsystem filter (e.g., "gematria", "biblescholar")
        model_name: Optional embedding model name (defaults to configured model)

    Returns:
        Dictionary with:
        - results: List of {logical_name, repo_path, fragment_type, content, score, meta}
        - query: Original query
        - k: Number of results requested
        - model: Model name used
    """
    result: dict[str, Any] = {
        "query": query,
        "k": k,
        "results": [],
        "model": model_name or "text-embedding-bge-m3",
    }

    # Generate query embedding
    try:
        embeddings = embed([query], model_slot="embedding")
        if not embeddings or not embeddings[0]:
            result["error"] = "Failed to generate query embedding"
            return result
        query_embedding = embeddings[0]
    except Exception as e:
        result["error"] = f"Embedding generation failed: {e}"
        return result

    # Pad to 1024 dimensions if needed (granite-embedding:278m returns 768)
    if len(query_embedding) == 768:
        query_embedding = query_embedding + [0.0] * (1024 - 768)

    embedding_json = json.dumps(query_embedding)

    # Connect to DB and run similarity search
    try:
        engine = get_control_engine()
    except Exception as e:
        result["error"] = f"Failed to connect to control DB: {e}"
        return result

    try:
        with engine.connect() as conn:
            # Build query with optional subsystem filter
            subsystem_filter = ""
            if subsystem:
                subsystem_filter = """
                    AND (df.meta->>'subsystem' = :subsystem)
                """

            query_sql = text(
                f"""
                SELECT
                    dr.logical_name,
                    dr.repo_path,
                    df.fragment_type,
                    df.content,
                    df.meta,
                    1 - (e.embedding <-> CAST(:query_embedding AS vector)) AS score
                FROM control.doc_embedding e
                INNER JOIN control.doc_fragment df ON df.id = e.fragment_id
                INNER JOIN control.doc_registry dr ON dr.doc_id = df.doc_id
                WHERE e.model_name = :model_name
                  AND dr.is_ssot = TRUE
                  AND dr.enabled = TRUE
                  AND (dr.repo_path LIKE '%.py' OR dr.repo_path LIKE '%.ts' OR dr.repo_path LIKE '%.tsx')
                  {subsystem_filter}
                ORDER BY e.embedding <-> CAST(:query_embedding AS vector)
                LIMIT :k
                """
            )

            params = {
                "query_embedding": embedding_json,
                "model_name": result["model"],
                "k": k,
            }
            if subsystem:
                params["subsystem"] = subsystem

            rows = conn.execute(query_sql, params).fetchall()

            # Format results
            results = []
            for row in rows:
                logical_name, repo_path, fragment_type, content, meta_json, score = row
                results.append(
                    {
                        "logical_name": logical_name,
                        "repo_path": repo_path,
                        "fragment_type": fragment_type,
                        "content": content[:500] if content else "",  # Truncate for display
                        "score": float(score),
                        "meta": json.loads(meta_json) if meta_json else {},
                    }
                )

            result["results"] = results
            return result

    except Exception as e:
        result["error"] = f"Search query failed: {e}"
        return result
