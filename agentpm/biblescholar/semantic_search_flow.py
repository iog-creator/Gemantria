"""BibleScholar semantic search flow (read-only).

Provides semantic search over Bible verses using vector embeddings.
Users can search by concepts, questions, or themes rather than exact keywords.

See:
- docs/SSOT/BIBLESCHOLAR_MIGRATION_PLAN.md
- agentpm/biblescholar/AGENTS.md
"""

from __future__ import annotations

from dataclasses import dataclass

from agentpm.adapters.lm_studio import embed
from agentpm.biblescholar.vector_adapter import BibleVectorAdapter, VerseSimilarityResult


@dataclass
class SemanticSearchResult:
    """Result from a semantic search query.

    Attributes:
        query: The original search query.
        results: List of similar verses with scores.
        model: Embedding model used.
        total_results: Total number of results found.
    """

    query: str
    results: list[VerseSimilarityResult]
    model: str = "text-embedding-bge-m3"
    total_results: int = 0


def semantic_search(
    query: str,
    limit: int = 20,
    translation: str = "KJV",
    model: str = "text-embedding-bge-m3",
) -> SemanticSearchResult:
    """Search Bible verses by semantic meaning.

    Embeds the user's query using BGE-M3 and finds verses with similar
    semantic meaning using cosine similarity.

    Args:
        query: User's search query (e.g., "hope in difficult times").
        limit: Maximum number of results to return.
        translation: Bible translation to search (default: KJV).
        model: Embedding model to use (default: BGE-M3).

    Returns:
        SemanticSearchResult with matching verses.

    Example:
        >>> result = semantic_search("faith and trust in God", limit=5)
        >>> for verse in result.results:
        ...     print(f"{verse.book_name} {verse.chapter_num}:{verse.verse_num} ({verse.similarity_score:.2%})")
    """
    # 1. Embed the query using BGE-M3
    query_embeddings = embed(query, model_slot="embedding")
    # embed() returns list[list[float]], so take first element for single query
    if not query_embeddings or not query_embeddings[0]:
        return SemanticSearchResult(
            query=query,
            results=[],
            model=model,
            total_results=0,
        )

    query_embedding = query_embeddings[0]

    # 2. Search for similar verses using vector adapter
    adapter = BibleVectorAdapter()

    # Use find_similar_by_embedding method
    results = adapter.find_similar_by_embedding(
        query_embedding,
        limit=limit,
        translation_source=translation if translation else None,
    )

    return SemanticSearchResult(
        query=query,
        results=results,
        model=model,
        total_results=len(results),
    )
