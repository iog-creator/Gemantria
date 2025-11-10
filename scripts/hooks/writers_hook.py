#!/usr/bin/env python3
from __future__ import annotations

from typing import Iterable

from openai import OpenAI

from scripts.config.env import openai_cfg
from scripts.db.upsert_helpers import upsert_edge, upsert_embedding, upsert_node


def ensure_nodes(surfaces: Iterable[str]) -> list[str]:
    """Ensure concepts exist; returns list of node_id (UUID strings)."""
    ids = []
    for s in surfaces:
        node_id = upsert_node(surface=s, kind="concept")  # 'class' column name → param 'kind'
        ids.append(node_id)
    return ids


def embed_nodes(node_ids: list[str], texts: list[str]) -> None:
    cfg = openai_cfg()
    client = OpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"])
    for node_id, text in zip(node_ids, texts, strict=False):
        emb = client.embeddings.create(model=cfg["embed_model"], input=[text]).data[0].embedding
        upsert_embedding(node_id, emb)


def relate(a: str, b: str, edge_type: str = "related_to", weight: float | None = None) -> str:
    return upsert_edge(a, b, kind=edge_type, weight=weight, meta={"source": "writers_hook"})
