#!/usr/bin/env python3
"""
Guard: LM (Language Model) Health Check

Checks LM Studio/Ollama endpoint availability and response validity.
Returns JSON verdict summarizing LM posture (lm_ready, lm_off).

Phase-3C P1: Updated to use LM Studio adapter from agentpm.adapters.lm_studio.
Phase-7E: Added Ollama provider support with automatic model discovery.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

# Import lightweight health check (doesn't trigger model loads)
from agentpm.lm.lm_status import check_lmstudio_health, check_ollama_health  # noqa: E402
from scripts.config.env import get_lm_model_config, get_lm_studio_settings  # noqa: E402


def check_lm_health() -> dict:
    """
    Check LM Studio/Ollama health posture using the unified adapter.

    Phase-3C P1: Uses agentpm.adapters.lm_studio.lm_studio_chat() for health check.
    Phase-7E: Supports Ollama provider with automatic model discovery.

    Returns:
        Dictionary with health status:
        {
            "ok": bool,
            "mode": "lm_ready" | "lm_off",
            "details": {
                "endpoint": str,
                "provider": str,
                "errors": list[str],
            },
        }
    """
    cfg = get_lm_model_config()
    provider = cfg.get("provider", "lmstudio").strip()
    endpoint = cfg.get("base_url" if provider == "lmstudio" else "ollama_base_url", "http://localhost:1234/v1")

    result: dict = {
        "ok": False,
        "mode": "lm_off",
        "details": {
            "endpoint": endpoint,
            "provider": provider,
            "errors": [],
        },
    }

    # Phase-7E: Ollama provider discovery and auto-installation
    if provider == "ollama":
        try:
            from scripts.ollama_discovery import check_ollama_server, ensure_models

            base_url = cfg.get("ollama_base_url", "http://127.0.0.1:11434")
            if not check_ollama_server(base_url):
                result["details"]["errors"].append("ollama_server_not_running")
                return result

            # Auto-discover and install required models
            required_models = []
            for key in [
                "local_agent_model",
                "embedding_model",
                "theology_model",
                "math_model",
                "reranker_model",
            ]:
                model = cfg.get(key)
                if model:
                    required_models.append(model)

            if required_models:
                ensure_results = ensure_models(base_url, required_models, skip_embeddings=True)
                # None = skipped (embeddings), False = failed, True = success
                failed = [m for m, ok in ensure_results.items() if ok is False]
                if failed:
                    result["details"]["errors"].append(f"models_missing: {','.join(failed)}")
                    return result
                # Warn about skipped embeddings but don't fail
                skipped = [m for m, ok in ensure_results.items() if ok is None]
                if skipped:
                    result["details"]["warnings"] = result["details"].get("warnings", [])
                    result["details"]["warnings"].append(f"embeddings_skipped: {','.join(skipped)}")

            # Test Ollama with lightweight health check (doesn't trigger model loads)
            service_status = check_ollama_health(base_url)

            if service_status == "OK":
                result["ok"] = True
                result["mode"] = "lm_ready"
                return result
            else:
                result["details"]["errors"].append(f"ollama_unreachable: {service_status}")
                return result

        except ImportError:
            result["details"]["errors"].append("ollama_discovery_not_available")
            return result
        except Exception as e:
            result["details"]["errors"].append(f"ollama_discovery_error: {e!s}")
            return result

    # LM Studio path (legacy)
    settings = get_lm_studio_settings()
    if not settings.get("enabled") or not settings.get("base_url"):
        result["details"]["errors"].append("lm_studio_disabled_or_unconfigured")
        return result

    # Health check: lightweight connection test (doesn't trigger model loads)
    # Use the lightweight health check from lm_status.py which only verifies server reachability
    base_url = settings.get("base_url", "http://127.0.0.1:1234")
    # Remove /v1 suffix if present for health check
    clean_base = base_url.rstrip("/")
    if clean_base.endswith("/v1"):
        clean_base = clean_base[:-3]

    service_status = check_lmstudio_health(clean_base)

    if service_status == "OK":
        result["ok"] = True
        result["mode"] = "lm_ready"
        return result
    else:
        result["details"]["errors"].append(f"lm_studio_unreachable: {service_status}")
        return result


def main() -> int:
    """Main entry point."""
    health = check_lm_health()
    print(json.dumps(health, indent=2))
    # Always exit 0 (safe for CI; JSON indicates status)
    return 0


if __name__ == "__main__":
    sys.exit(main())
