#!/usr/bin/env python3
"""
Ollama Model Discovery & Auto-Installation Tool

Phase-7E: Automatically discovers and installs required Ollama models
based on environment configuration.

This script:
1. Checks if Ollama server is running
2. Lists available models via /api/tags
3. Checks if required models (from get_lm_model_config()) are installed
4. Automatically pulls missing models via /api/pull
5. Verifies models are ready for use
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.config.env import get_lm_model_config


def _get_json(base_url: str, path: str) -> dict[str, Any]:
    """GET JSON from Ollama API."""
    url = base_url.rstrip("/") + path
    req = Request(url, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=10) as resp:  # noqa: S310
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except (HTTPError, URLError) as e:
        raise RuntimeError(f"Ollama API request failed: {e}") from e


def _post_json(base_url: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    """POST JSON to Ollama API."""
    url = base_url.rstrip("/") + path
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=300) as resp:  # noqa: S310 - long timeout for model pulls
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except (HTTPError, URLError) as e:
        raise RuntimeError(f"Ollama API request failed: {e}") from e


def _post_json_stream(base_url: str, path: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    """POST JSON to Ollama API with streaming response."""
    url = base_url.rstrip("/") + path
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=300) as resp:  # noqa: S310
            chunks = []
            while True:
                line = resp.readline()
                if not line:
                    break
                line_str = line.decode("utf-8").strip()
                if line_str:
                    try:
                        chunks.append(json.loads(line_str))
                    except json.JSONDecodeError:
                        pass
            return chunks
    except (HTTPError, URLError) as e:
        raise RuntimeError(f"Ollama API request failed: {e}") from e


def check_ollama_server(base_url: str) -> bool:
    """Check if Ollama server is running."""
    try:
        _get_json(base_url, "/api/tags")
        return True
    except Exception:
        return False


def list_installed_models(base_url: str) -> list[str]:
    """List all installed models."""
    try:
        data = _get_json(base_url, "/api/tags")
        models = data.get("models", [])
        return [m.get("name", "") for m in models if m.get("name")]
    except Exception as e:
        print(f"Warning: Failed to list models: {e}", file=sys.stderr)
        return []


def pull_model(base_url: str, model_name: str, stream: bool = True) -> bool:
    """Pull a model from Ollama registry."""
    print(f"Pulling model: {model_name}...", file=sys.stderr)
    payload = {"model": model_name, "stream": stream}
    try:
        if stream:
            chunks = _post_json_stream(base_url, "/api/pull", payload)
            # Check last chunk for success
            if chunks:
                last = chunks[-1]
                status = last.get("status", "")
                if "success" in status.lower() or "complete" in status.lower():
                    print(f"✓ Successfully pulled {model_name}", file=sys.stderr)
                    return True
                print(f"Pull status: {status}", file=sys.stderr)
            return False
        else:
            result = _post_json(base_url, "/api/pull", payload)
            status = result.get("status", "")
            if "success" in status.lower():
                print(f"✓ Successfully pulled {model_name}", file=sys.stderr)
                return True
            return False
    except Exception as e:
        print(f"Error pulling {model_name}: {e}", file=sys.stderr)
        return False


def _normalize_model_name(model_name: str) -> str:
    """Normalize model names for Ollama compatibility.

    Phase-7F: Maps LM Studio naming conventions to Ollama model names:
    - BGE-M3 embeddings: text-embedding-bge-m3 -> bge-m3:latest
    - BGE reranker: bge-reranker-v2-m3 -> bge-reranker-v2-m3:latest
    - Granite models: granite4:tiny-h, granite-embedding:latest
    """
    # Remove common prefixes/suffixes
    normalized = model_name.lower()

    # Phase-7F: Handle BGE-M3 embedding models
    if "bge-m3" in normalized or "bge_m3" in normalized:
        if ":" not in model_name:
            return "bge-m3:latest"
        return model_name  # Already has tag

    # Phase-7F: Handle BGE reranker models
    if "bge" in normalized and "rerank" in normalized:
        if "v2-m3" in normalized or "v2_m3" in normalized:
            if ":" not in model_name:
                return "bge-reranker-v2-m3:latest"
            return model_name
        # Fallback for other BGE reranker variants
        if ":" not in model_name:
            return "bge-reranker-v2-m3:latest"
        return model_name

    # Handle text-embedding-bge-m3 (LM Studio name)
    if "text-embedding-bge-m3" in normalized or "text_embedding_bge_m3" in normalized:
        return "bge-m3:latest"

    # Handle Granite reranker models
    if "granite" in normalized and "rerank" in normalized:
        if "r2" in normalized or "english" in normalized:
            return "granite-reranker"  # Try this first
        return "granite-reranker"  # Default fallback

    # Handle Granite embedding variants
    if "granite" in normalized and "embedding" in normalized:
        if "r2" in normalized or "278m" in normalized:
            return "granite-embedding:278m"  # Multilingual version
        elif "30m" in normalized:
            return "granite-embedding:30m"  # English-only version
        else:
            return "granite-embedding:latest"  # Default to latest

    # Handle Granite chat models
    if "granite" in normalized and ("4.0" in normalized or "4" in normalized):
        if "tiny" in normalized or "tiny-h" in normalized:
            return "granite4:tiny-h"  # or ibm/granite4.0-preview:tiny

    # Return as-is if no normalization needed
    return model_name


def ensure_models(base_url: str, required_models: list[str], skip_embeddings: bool = False) -> dict[str, bool]:
    """Ensure all required models are installed, pulling missing ones.

    Args:
        base_url: Ollama server base URL
        required_models: List of model names to ensure
        skip_embeddings: If True, skip embedding models that fail (they may not be in Ollama registry)

    Returns:
        Dictionary mapping model names to success status
    """
    installed = list_installed_models(base_url)
    results = {}

    for model in required_models:
        if not model:
            continue

        # Normalize model name for Ollama compatibility
        normalized_model = _normalize_model_name(model)
        original_model = model  # Keep original for reporting

        # Check if model is installed (exact match or prefix match)
        # Check both original and normalized names
        is_installed = any(
            installed_model == model
            or installed_model.startswith(f"{model}:")
            or installed_model == normalized_model
            or installed_model.startswith(f"{normalized_model}:")
            or (normalized_model != model and installed_model.startswith(normalized_model.split(":")[0]))
            for installed_model in installed
        )

        if is_installed:
            print(f"✓ Model already installed: {model}", file=sys.stderr)
            results[model] = True
        else:
            # Try normalized name if different
            pull_name = normalized_model if normalized_model != model else model
            print(f"⚠ Model not found: {model}", file=sys.stderr)
            if normalized_model != model:
                print(f"  → Trying normalized name: {normalized_model}", file=sys.stderr)
            if pull_model(base_url, pull_name):
                results[model] = True
            else:
                # For embedding/reranker models, warn but don't fail hard (they may not be in Ollama registry)
                is_embedding = "embedding" in model.lower() or "bge" in model.lower()
                is_reranker = "rerank" in model.lower()
                if skip_embeddings and (is_embedding or is_reranker):
                    model_type = "reranker" if is_reranker else "embedding"
                    print(
                        f"⚠ Skipping {model_type} model {model} (not in Ollama registry). "
                        f"Consider using LM Studio for {model_type} models or Ollama-compatible alternatives.",
                        file=sys.stderr,
                    )
                    results[model] = None  # None = skipped, not failed
                else:
                    results[model] = False

    return results


def main() -> int:
    """Main discovery and installation routine."""
    cfg = get_lm_model_config()
    provider = cfg.get("provider", "lmstudio").strip()
    base_url = cfg.get("ollama_base_url", "http://127.0.0.1:11434")

    if provider != "ollama":
        print(f"INFERENCE_PROVIDER={provider}, skipping Ollama discovery", file=sys.stderr)
        return 0

    # Check if Ollama server is running
    if not check_ollama_server(base_url):
        print(f"ERROR: Ollama server not running at {base_url}", file=sys.stderr)
        print("Please start Ollama: ollama serve", file=sys.stderr)
        return 1

    print(f"✓ Ollama server running at {base_url}", file=sys.stderr)

    # Collect required models from config
    required_models = []
    if cfg.get("local_agent_model"):
        required_models.append(cfg["local_agent_model"])
    if cfg.get("embedding_model"):
        required_models.append(cfg["embedding_model"])
    if cfg.get("theology_model"):
        required_models.append(cfg["theology_model"])
    if cfg.get("math_model"):
        required_models.append(cfg["math_model"])
    if cfg.get("reranker_model"):
        required_models.append(cfg["reranker_model"])

    if not required_models:
        print("No models configured, nothing to check", file=sys.stderr)
        return 0

    print(f"Checking {len(required_models)} required model(s)...", file=sys.stderr)

    # Ensure all models are installed (skip embedding models gracefully)
    results = ensure_models(base_url, required_models, skip_embeddings=True)

    # Report results (None = skipped, True = success, False = failed)
    failed = [m for m, ok in results.items() if ok is False]
    skipped = [m for m, ok in results.items() if ok is None]
    succeeded = [m for m, ok in results.items() if ok is True]

    if failed:
        print(f"✗ Failed to install {len(failed)} model(s): {', '.join(failed)}", file=sys.stderr)
        return 1
    elif skipped:
        print(
            f"⚠ Skipped {len(skipped)} embedding model(s) (not in Ollama registry): {', '.join(skipped)}",
            file=sys.stderr,
        )
        print(
            "  Note: BGE embeddings may need LM Studio. Consider using Ollama-compatible embedding models.",
            file=sys.stderr,
        )
        # Don't fail if only embeddings were skipped
        if succeeded:
            print(f"✓ Successfully installed {len(succeeded)} model(s)", file=sys.stderr)
            return 0
        return 1
    else:
        print(f"✓ All required models are available ({len(succeeded)} model(s))", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
