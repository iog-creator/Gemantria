"""Semantic agent for embedding-based retrieval and extraction."""

from __future__ import annotations

from src.services.lmstudio_client import EMBEDDING_MODEL, LMStudioClient


def extract_semantic_features(noun: dict) -> dict:
    """Extract semantic embeddings for noun."""
    text = f"{noun.get('name', '')} {noun.get('hebrew', '')}"
    client = LMStudioClient()
    embeddings = client.get_embeddings([text])
    if embeddings:
        return {"embedding": embeddings[0], "model": EMBEDDING_MODEL}
    return {"embedding": [], "model": EMBEDDING_MODEL}


def retrieve_semantic_similar(noun_id: str, threshold: float = 0.75) -> list[dict]:
    """Retrieve semantically similar nouns (placeholder - requires DB integration)."""
    # TODO: Implement pgvector KNN retrieval
    return []
