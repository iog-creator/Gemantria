#!/usr/bin/env python3
import hashlib
import json
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = ROOT / ".cache" / "rerank"
CACHE.mkdir(parents=True, exist_ok=True)


def cache_key(text_a: str, text_b: str) -> str:
    h = hashlib.sha256()
    h.update(text_a.encode("utf-8") + b"\x00" + text_b.encode("utf-8"))
    return h.hexdigest()  # hex string


def _cache_path(key: str) -> pathlib.Path:
    return CACHE / f"{key}.json"


def _read_cache(key: str) -> dict[str, str | float] | None:
    p = _cache_path(key)
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
            return None
        except Exception:
            return None
    return None


def _write_cache(key: str, payload: dict[str, str | float]) -> None:
    _cache_path(key).write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _provider_lmstudio(a: str, b: str) -> float:
    # Local-only LM Studio HTTP provider (optional). If not configured, raises.
    import json as _json  # noqa: E402
    import urllib.request  # noqa: E402

    url = os.environ.get("LMSTUDIO_RERANK_URL", "http://127.0.0.1:1234/v1/rerank")
    model = os.environ.get("LMSTUDIO_RERANK_MODEL", "qwen2.5-rerank")
    payload = {"model": model, "query": a, "documents": [b]}
    req = urllib.request.Request(
        url,
        data=_json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = _json.loads(resp.read().decode("utf-8"))
    # Expect a score in [0,1] or [0,100]; normalize safely.
    score = data.get("results", [{}])[0].get("relevance_score", 0.0)
    try:
        score = float(score)
    except Exception:
        score = 0.0
    if score > 1.0:
        score = score / 100.0
    return max(0.0, min(1.0, score))


def rerank(a: str, b: str) -> float:
    """
    Returns a deterministic score in [0,1].
    Uses cache first; then provider; falls back to cosine parity (0.5) if unavailable.
    """
    key = cache_key(a, b)
    hit = _read_cache(key)
    if hit is not None and "score" in hit:
        score_value = hit["score"]
        if isinstance(score_value, int | float):
            return float(score_value)
        return 0.5
    # Provider selection
    provider = os.environ.get("RERANK_PROVIDER", "none").lower()
    if provider in ("lmstudio", "lm"):
        try:
            score: float = _provider_lmstudio(a, b)
        except Exception:
            score = 0.5  # neutral fallback
    else:
        score = 0.5  # neutral fallback
    _write_cache(key, {"score": score, "a": a[:120], "b": b[:120]})
    return score
