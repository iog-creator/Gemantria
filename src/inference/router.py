# src/inference/router.py

import os


PROVIDER = os.getenv("INFERENCE_PROVIDER", "lmstudio")

BASE_URL = os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:9994")


MODELS = {
    "theology": os.getenv("THEOLOGY_MODEL", "christian-bible-expert-v2.0-12b"),
    "general": os.getenv("ANSWERER_MODEL_ALT", "Qwen2.5-14B-Instruct-GGUF"),
    "math": os.getenv("MATH_MODEL", "self-certainty-qwen3-1.7b-base-math"),
    "embed": os.getenv("EMBEDDING_MODEL", "text-embedding-bge-m3"),
    "reranker": os.getenv("RERANKER_MODEL", "qwen.qwen3-reranker-0.6b"),
}


def pick(task: str) -> dict:
    """

    Return a connection dict {provider, base_url, model} for the given logical task.

    Valid tasks: discovery, enrichment, triage, adr, math, embed, reranker

    """

    if task in {"discovery", "enrichment"}:
        return {"provider": PROVIDER, "base_url": BASE_URL, "model": MODELS["theology"]}

    if task in {"triage", "adr"}:
        return {"provider": PROVIDER, "base_url": BASE_URL, "model": MODELS["general"]}

    if task == "math":
        return {"provider": PROVIDER, "base_url": BASE_URL, "model": MODELS["math"]}

    if task == "embed":
        return {"provider": PROVIDER, "base_url": BASE_URL, "model": MODELS["embed"]}

    if task == "reranker":
        return {"provider": PROVIDER, "base_url": BASE_URL, "model": MODELS["reranker"]}

    raise ValueError(f"Unknown task: {task}")
