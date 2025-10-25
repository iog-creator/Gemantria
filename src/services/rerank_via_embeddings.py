"""
Bi-encoder rerank proxy using LM Studio /v1/embeddings endpoint.

This replaces the previous reranker implementation that used /v1/chat/completions
with a bi-encoder approach that computes cosine similarity between BGE-M3 embeddings
of concept name pairs. This works with LM Studio's actual API capabilities.

The rerank_pairs function maintains the same interface as the previous implementation
for drop-in replacement.
"""

import math
import os
import re
import unicodedata

import requests

# Guard against mocks for this run
if os.getenv("USE_MOCKS", "0") == "1":
    raise RuntimeError("Mocks are disabled for this run. Set USE_MOCKS=0.")


# Environment configuration
LM_BASE = os.getenv("EMBED_URL", "http://127.0.0.1:9994/v1")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-bge-m3")


def _norm(text: str) -> str:
    """
    Normalize text for stable embeddings across Greek/Hebrew scripts.

    Applies NFC normalization and whitespace squeezing to ensure
    consistent embeddings regardless of text formatting variations.

    Args:
        text: Input text string

    Returns:
        Normalized text string
    """
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _embed(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a batch of texts using LM Studio /v1/embeddings.

    Args:
        texts: List of text strings to embed

    Returns:
        List of embedding vectors

    Raises:
        requests.HTTPError: If the API call fails
    """
    r = requests.post(
        f"{LM_BASE}/embeddings", json={"model": EMBED_MODEL, "input": texts}, timeout=60
    )
    r.raise_for_status()
    return [item["embedding"] for item in r.json()["data"]]


def _cos(a: list[float], b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    Args:
        a: First embedding vector
        b: Second embedding vector

    Returns:
        Cosine similarity score in [0, 1]
    """
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return 0.0 if na == 0 or nb == 0 else dot / (na * nb)


def rerank_via_embeddings(
    pairs: list[tuple[int, int]], name_map: dict[int, str]
) -> list[float]:
    """
    Rerank concept pairs by computing cosine similarity of their BGE-M3 embeddings.

    This is a bi-encoder proxy that replaces the previous cross-encoder reranker.
    It maintains the same interface for drop-in replacement.

    Args:
        pairs: List of (source_id, target_id) tuples
        name_map: Dict mapping concept_ids to their display names

    Returns:
        List of similarity scores [0.0, 1.0] for each pair
    """
    if not pairs:
        return []

    # Extract and normalize texts in fixed order for efficient batch embedding
    A = [_norm(name_map.get(sid, str(sid))) for sid, _ in pairs]
    B = [_norm(name_map.get(tid, str(tid))) for _, tid in pairs]

    # Batch embed all texts at once
    vecA = _embed(A)
    vecB = _embed(B)

    # Compute cosine similarities
    return [_cos(a, b) for a, b in zip(vecA, vecB, strict=False)]
