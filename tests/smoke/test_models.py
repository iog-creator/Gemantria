import json
import os
import socket

import pytest

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # pytest will skip if requests not available


def _is_open(host: str, port: int, timeout: float = 0.75) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _get(url: str, timeout: float = 2.0) -> dict:
    if requests is None:
        pytest.skip("requests not installed")
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.json()


def _post(url: str, payload: dict[str, str], timeout: float = 4.0) -> dict:
    if requests is None:
        pytest.skip("requests not installed")
    r = requests.post(
        url,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
        timeout=timeout,
    )
    r.raise_for_status()
    return r.json()


@pytest.mark.smoke
def test_models_endpoint_has_answerer() -> None:
    """
    Asserts our configured answerer is advertised by the local LM Studio
    (OpenAI-compatible) endpoint. Skips cleanly if the service is not running.
    """
    host = os.getenv("LM_CHAT_HOST", "127.0.0.1")
    port = int(os.getenv("LM_CHAT_PORT", "9991"))
    if not _is_open(host, port):
        pytest.skip(f"LM chat endpoint not reachable at {host}:{port}")

    url = f"http://{host}:{port}/v1/models"
    data = _get(url)

    model_ids = {m.get("id") for m in data.get("data", []) if isinstance(m, dict)}
    primary = os.getenv("ANSWERER_MODEL_PRIMARY", "christian-bible-expert-v2.0-12b")
    alt = os.getenv("ANSWERER_MODEL_ALT", "Qwen2.5-14B-Instruct-GGUF")

    assert model_ids, "No models returned from /v1/models"
    assert (primary in model_ids) or (alt in model_ids), (
        f"Neither primary ({primary}) nor alt ({alt}) appears in /v1/models. Seen: {sorted(model_ids)}"  # type: ignore[arg-type]
    )


@pytest.mark.smoke
def test_embeddings_dimension_is_1024() -> None:
    """
    Calls the local embeddings endpoint and verifies dim==1024.
    Skips if the service is not running. Uses minimal payload to keep it fast.
    """
    host = os.getenv("LM_EMBED_HOST", "127.0.0.1")
    port = int(os.getenv("LM_EMBED_PORT", "9994"))
    if not _is_open(host, port):
        pytest.skip(f"Embedding endpoint not reachable at {host}:{port}")

    model = os.getenv("EMBEDDING_MODEL", "text-embedding-bge-m3")
    url = f"http://{host}:{port}/v1/embeddings"
    j = _post(url, {"model": model, "input": "ping"})

    emb = j.get("data", [{}])[0].get("embedding")
    assert isinstance(emb, list) and emb, "No embedding returned"
    assert len(emb) == 1024, f"Expected 1024-dim embedding, got {len(emb)}"
