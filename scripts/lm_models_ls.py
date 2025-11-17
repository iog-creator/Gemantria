#!/usr/bin/env python3
"""LM Studio model discovery and validation CLI.

Lists available models from LM Studio and validates that configured
model IDs (EMBEDDING_MODEL, THEOLOGY_MODEL, LOCAL_AGENT_MODEL, RERANKER_MODEL)
actually exist in the discovered list.
"""

import json
import sys
import urllib.request
from typing import Any, Dict, List

from scripts.config.env import get_lm_model_config


def _build_models_url(base_url: str) -> str:
    """Build the /v1/models endpoint URL from base URL."""
    # Expect base like http://host:port/v1
    if base_url.endswith("/v1"):
        return base_url + "/models"
    if base_url.endswith("/v1/"):
        return base_url + "models"
    # Fallback: assume caller gave root
    if base_url.endswith("/"):
        return base_url + "v1/models"
    return base_url + "/v1/models"


def fetch_models() -> List[Dict[str, Any]]:
    """Fetch available models from LM Studio /v1/models endpoint."""
    cfg = get_lm_model_config()
    url = _build_models_url(cfg["base_url"])

    req = urllib.request.Request(url)
    # LM Studio ignores the actual key but expects the header
    req.add_header("Authorization", "Bearer lm-studio")

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    # OpenAI-compatible: {"data": [{ "id": "...", ... }, ...]}
    return data.get("data", [])


def validate_config(models: List[Dict[str, Any]]) -> int:
    """Validate that configured model IDs exist in the discovered models list.

    Returns:
        0 if all configured models are found, 1 otherwise.
    """
    cfg = get_lm_model_config()
    available_ids = {m.get("id") for m in models if "id" in m}

    required = {
        "EMBEDDING_MODEL": cfg.get("embedding_model"),
        "THEOLOGY_MODEL": cfg.get("theology_model"),
        "LOCAL_AGENT_MODEL": cfg.get("local_agent_model"),
        "RERANKER_MODEL": cfg.get("reranker_model"),
    }

    missing = {name: mid for name, mid in required.items() if mid and mid not in available_ids}

    if missing:
        print("LM model discovery: some configured models were not found:", file=sys.stderr)
        for name, mid in missing.items():
            print(f"  - {name}={mid!r} not in LM Studio /v1/models", file=sys.stderr)
        return 1

    return 0


def main() -> None:
    """Main entry point for LM Studio model discovery CLI."""
    try:
        models = fetch_models()
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Failed to fetch models from LM Studio: {exc}", file=sys.stderr)
        sys.exit(1)

    if not models:
        print("No models returned from LM Studio /v1/models")
    else:
        print("LM Studio models:")
        print("ID")
        print("-" * 40)
        for m in models:
            mid = m.get("id", "<unknown-id>")
            print(mid)

    rc = validate_config(models)
    if rc != 0:
        # Non-zero exit code to signal config drift; caller may treat as advisory.
        sys.exit(rc)


if __name__ == "__main__":
    main()
