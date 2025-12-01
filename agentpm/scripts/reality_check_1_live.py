"""

Reality Check #1 — LIVE



This script enforces a *real* runtime check:



1. Uses the centralized env config (scripts.config.env) and the LM Studio

   resolver (lmstudio_resolver.base_url) to determine the LM endpoint.

2. Verifies DB connectivity via centralized DSN loaders.

3. Verifies LM Studio is reachable at the resolved base URL.

4. Actively pings each configured model (theology, math, embedding, reranker,

   LM_EMBED_MODEL) with a tiny request.

   **IMPORTANT**: Model endpoint selection:

   - Embedding models (EMBEDDING_MODEL, LM_EMBED_MODEL) MUST use `/v1/embeddings` endpoint

   - Chat/completion models (THEOLOGY_MODEL, MATH_MODEL, RERANKER_MODEL) MUST use `/v1/chat/completions` endpoint

   This distinction is enforced by the `_embedding()` and `_chat_completion()` helper functions.

5. Runs the docs→DB→LM Q&A pipeline end-to-end.

6. Exits non-zero if ANY of the above fail.



This is intended to be called via either:

  - `pmagent reality-check live`

  - `make reality.check.1.live`



Related: ADR-026 (Reranker Bi-Encoder Proxy) documents the endpoint usage pattern.

"""

from __future__ import annotations


import json

import os

import subprocess

import sys

from typing import Any, Dict, List, Tuple


import requests

from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout


from scripts.config import env as config_env

import scripts.ai.lmstudio_resolver as lmstudio_resolver


def _run(cmd: List[str]) -> Tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    return proc.returncode, proc.stdout, proc.stderr


def check_db() -> Dict[str, Any]:
    """Use centralized DSN loader to verify DB connectivity."""

    try:
        dsn = config_env.get_rw_dsn()

    except Exception as e:  # noqa: BLE001
        return {"ok": False, "reason": f"get_rw_dsn_failed: {e}"}

    # Use pmagent health db if it exists as the authoritative guard

    code, out, err = _run(["pmagent", "health", "db"])

    if code == 0:
        return {"ok": True, "reason": "pmagent_health_db_ok", "details": out.strip()}

    return {
        "ok": False,
        "reason": "pmagent_health_db_failed",
        "exit_code": code,
        "stdout": out,
        "stderr": err,
        "dsn": dsn,
    }


def check_lmstudio_endpoint() -> Dict[str, Any]:
    """Resolve LM Studio base URL and ensure it's reachable."""

    base = lmstudio_resolver.base_url().rstrip("/")

    url = f"{base}/models"

    try:
        resp = requests.get(url, timeout=10)

        resp.raise_for_status()

        data = resp.json()

        return {
            "ok": True,
            "reason": "lmstudio_models_ok",
            "base_url": base,
            "models_raw": data,
        }

    except (ConnectionError, Timeout) as e:
        return {
            "ok": False,
            "reason": f"lmstudio_unreachable: {e}",
            "base_url": base,
        }

    except HTTPError as e:
        return {
            "ok": False,
            "reason": f"lmstudio_http_error: {e}",
            "base_url": base,
        }

    except ValueError as e:
        return {
            "ok": False,
            "reason": f"lmstudio_invalid_json: {e}",
            "base_url": base,
        }

    except RequestException as e:
        return {
            "ok": False,
            "reason": f"lmstudio_request_error: {e}",
            "base_url": base,
        }

    except Exception as e:  # noqa: BLE001
        return {
            "ok": False,
            "reason": f"lmstudio_unexpected_error: {e}",
            "base_url": base,
        }


def _chat_completion(base_url: str, model: str, prompt: str) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}/chat/completions"

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 16,
        "temperature": 0.0,
    }

    try:
        resp = requests.post(url, json=payload, timeout=20)

        resp.raise_for_status()

        data = resp.json()

        return {"ok": True, "response": data}

    except (ConnectionError, Timeout) as e:
        return {"ok": False, "reason": f"chat_error: {e}"}

    except HTTPError as e:
        return {"ok": False, "reason": f"http_error: {e}"}

    except ValueError as e:
        return {"ok": False, "reason": f"invalid_json: {e}"}

    except RequestException as e:
        return {"ok": False, "reason": f"request_error: {e}"}

    except Exception as e:  # noqa: BLE001
        return {"ok": False, "reason": f"unexpected_error: {e}"}


def _embedding(base_url: str, model: str, input_text: str) -> Dict[str, Any]:
    """Test embedding model using /embeddings endpoint."""
    url = f"{base_url.rstrip('/')}/embeddings"

    payload = {
        "model": model,
        "input": input_text,
    }

    try:
        resp = requests.post(url, json=payload, timeout=20)

        resp.raise_for_status()

        data = resp.json()

        return {"ok": True, "response": data}

    except (ConnectionError, Timeout) as e:
        return {"ok": False, "reason": f"embedding_error: {e}"}

    except HTTPError as e:
        return {"ok": False, "reason": f"http_error: {e}"}

    except ValueError as e:
        return {"ok": False, "reason": f"invalid_json: {e}"}

    except RequestException as e:
        return {"ok": False, "reason": f"request_error: {e}"}

    except Exception as e:  # noqa: BLE001
        return {"ok": False, "reason": f"unexpected_error: {e}"}


def check_models(base_url: str) -> Dict[str, Any]:
    """Ping each configured model with appropriate endpoint (chat for LLMs, embeddings for embedding models)."""

    models_to_check = []

    # Pull from env_example contract

    theology = os.getenv("THEOLOGY_MODEL")

    math_model = os.getenv("MATH_MODEL")

    embedding = os.getenv("EMBEDDING_MODEL") or os.getenv("LM_EMBED_MODEL")

    reranker = os.getenv("RERANKER_MODEL")

    for name, value in [
        ("THEOLOGY_MODEL", theology),
        ("MATH_MODEL", math_model),
        ("EMBEDDING_MODEL", embedding),
        ("RERANKER_MODEL", reranker),
    ]:
        if value:
            models_to_check.append((name, value))

    results: Dict[str, Any] = {"ok": True, "models": []}

    for env_name, model in models_to_check:
        # Use embeddings endpoint for embedding models, chat for others
        if "embedding" in env_name.lower() or "embed" in model.lower():
            ping = _embedding(base_url, model, "Health check")
        else:
            ping = _chat_completion(base_url, model, f"Health check for {env_name}")

        entry = {"env": env_name, "model": model, **ping}

        results["models"].append(entry)

        if not ping.get("ok"):
            results["ok"] = False

    if not models_to_check:
        results["ok"] = False

        results["reason"] = "no_models_configured"

    return results


def run_pipeline() -> Dict[str, Any]:
    """Run docs ingest + golden Q&A via pmagent."""

    ingest_code, ingest_out, ingest_err = _run(
        [sys.executable, "-m", "agentpm.scripts.ingest_docs"]
    )

    ask_code, ask_out, ask_err = _run(["pmagent", "ask", "docs", "What does Phase-6P deliver?"])

    ok = ingest_code == 0 and ask_code == 0

    return {
        "ok": ok,
        "ingest": {
            "exit_code": ingest_code,
            "stdout": ingest_out,
            "stderr": ingest_err,
        },
        "ask_docs": {
            "exit_code": ask_code,
            "stdout": ask_out,
            "stderr": ask_err,
        },
    }


def main() -> None:
    report: Dict[str, Any] = {"ok": False, "steps": {}}

    db_status = check_db()

    report["steps"]["db"] = db_status

    lm_endpoint = check_lmstudio_endpoint()

    report["steps"]["lm_endpoint"] = lm_endpoint

    models_status: Dict[str, Any] | None = None

    pipeline_status: Dict[str, Any] | None = None

    if db_status.get("ok") and lm_endpoint.get("ok"):
        base_url = lm_endpoint.get("base_url") or lmstudio_resolver.base_url()

        models_status = check_models(base_url)

        report["steps"]["lm_models"] = models_status

        if models_status.get("ok"):
            pipeline_status = run_pipeline()

            report["steps"]["pipeline"] = pipeline_status

    # Determine overall ok

    if (
        db_status.get("ok")
        and lm_endpoint.get("ok")
        and models_status is not None
        and models_status.get("ok")
        and pipeline_status is not None
        and pipeline_status.get("ok")
    ):
        report["ok"] = True

        report["summary"] = (
            "Reality Check #1 LIVE passed: DB, LM Studio, models, and pipeline all OK"
        )

    else:
        report["ok"] = False

        report["summary"] = "Reality Check #1 LIVE failed (see steps)"

    print(json.dumps(report, indent=2))

    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
