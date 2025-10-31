#!/usr/bin/env python3
import json
import os

from src.infra.env_loader import ensure_env_loaded

ensure_env_loaded()
wanted = [
    "GEMATRIA_DSN",
    "BIBLE_DB_DSN",
    "LM_STUDIO_HOST",
    "ANSWERER_USE_ALT",
    "ANSWERER_MODEL_PRIMARY",
    "ANSWERER_MODEL_ALT",
    "EMBEDDING_MODEL",
    "EMBED_BATCH_MAX",
    "EDGE_ALPHA",
    "EDGE_STRONG",
    "EDGE_WEAK",
    "NN_TOPK",
]
print(json.dumps({k: os.getenv(k) for k in wanted}, indent=2))
