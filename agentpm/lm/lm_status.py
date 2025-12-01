#!/usr/bin/env python3
"""
LM Status Module

Phase-7G: Introspect LM configuration and local service health.
"""

from __future__ import annotations

import requests
from typing import Any

from scripts.config.env import get_lm_model_config


def check_ollama_health(base_url: str) -> str:
    """Check if Ollama service is reachable.

    Args:
        base_url: Ollama base URL (e.g., "http://127.0.0.1:11434")

    Returns:
        "OK" if reachable, "DOWN" on connection error, "UNKNOWN" on unexpected errors.
    """
    # Security: Only allow localhost/127.0.0.1
    if "127.0.0.1" not in base_url and "localhost" not in base_url:
        return "UNKNOWN"

    try:
        url = f"{base_url.rstrip('/')}/api/tags"
        response = requests.get(url, timeout=2.0)
        if response.status_code == 200:
            return "OK"
        return "DOWN"
    except requests.exceptions.ConnectionError:
        return "DOWN"
    except Exception:
        return "UNKNOWN"


def check_lmstudio_health(base_url: str) -> str:
    """Check if LM Studio service is reachable.

    Uses a TCP connection test to avoid HTTP endpoint errors.
    Per docs: health checks should verify server reachability without loading models.

    Args:
        base_url: LM Studio base URL (e.g., "http://127.0.0.1:9994")

    Returns:
        "OK" if reachable, "DOWN" on connection error, "UNKNOWN" on unexpected errors.
    """
    # Security: Only allow localhost/127.0.0.1
    if "127.0.0.1" not in base_url and "localhost" not in base_url:
        return "UNKNOWN"

    try:
        import socket
        from urllib.parse import urlparse

        # Parse URL to get host and port
        parsed = urlparse(base_url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or (9994 if "9994" in base_url else 1234)

        # Use TCP socket connection test (lightweight, no HTTP overhead)
        # This just checks if the port is open, doesn't trigger any HTTP endpoints
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            return "OK"
        return "DOWN"
    except Exception:
        return "UNKNOWN"


def compute_lm_status() -> dict[str, Any]:
    """Compute LM status for all slots.

    Returns:
        Dictionary with slot status information.
    """
    cfg = get_lm_model_config()

    # Define slots
    slots = [
        {
            "name": "local_agent",
            "provider_key": "local_agent_provider",
            "model_key": "local_agent_model",
        },
        {"name": "embedding", "provider_key": "embedding_provider", "model_key": "embedding_model"},
        {"name": "reranker", "provider_key": "reranker_provider", "model_key": "reranker_model"},
        {"name": "theology", "provider_key": "theology_provider", "model_key": "theology_model"},
    ]

    # Default providers (if not set)
    default_providers = {
        "local_agent": "ollama",
        "embedding": "ollama",
        "reranker": "ollama",
        "theology": "lmstudio",
    }

    status_slots = []
    for slot in slots:
        slot_name = slot["name"]
        provider = cfg.get(slot["provider_key"]) or default_providers.get(slot_name, "ollama")
        model = cfg.get(slot["model_key"])

        # Compute service status
        service_status = "UNKNOWN"
        if provider == "ollama":
            ollama_base_url = cfg.get("ollama_base_url", "http://127.0.0.1:11434")
            if cfg.get("ollama_enabled", True):
                service_status = check_ollama_health(ollama_base_url)
            else:
                service_status = "DISABLED"
        elif provider in ("lmstudio", "theology_lmstudio"):
            # For theology, use theology_lmstudio_base_url if available
            if slot_name == "theology":
                base_url = cfg.get("theology_lmstudio_base_url") or cfg.get(
                    "base_url", "http://127.0.0.1:9994"
                )
            else:
                base_url = cfg.get("base_url", "http://127.0.0.1:9994")
            if cfg.get("lm_studio_enabled", True):
                service_status = check_lmstudio_health(base_url)
            else:
                service_status = "DISABLED"
        else:
            service_status = "UNSUPPORTED"

        # Format model display (add reranker strategy if applicable)
        model_display = model or "NOT_CONFIGURED"
        if slot_name == "reranker" and cfg.get("reranker_strategy"):
            model_display = f"{model_display} ({cfg.get('reranker_strategy')})"

        status_slots.append(
            {
                "slot": slot_name,
                "provider": provider,
                "model": model_display,
                "service_status": service_status,
            }
        )

    return {
        "ok": all(slot["service_status"] == "OK" for slot in status_slots),
        "slots": status_slots,
    }


def print_lm_status_table(status: dict[str, Any]) -> str:
    """Print human-readable LM status table.

    Args:
        status: Status dictionary from compute_lm_status()

    Returns:
        Formatted table string.
    """
    slots = status.get("slots", [])

    # Table header
    lines = []
    lines.append("Slot        Provider           Model                            Service")
    lines.append("----------  -----------------  --------------------------------  --------")

    # Table rows
    for slot in slots:
        slot_name = slot["slot"]
        provider = slot["provider"]
        model = slot["model"]
        service = slot["service_status"]

        # Truncate long model names
        if len(model) > 32:
            model = model[:29] + "..."

        lines.append(f"{slot_name:<11} {provider:<18} {model:<33} {service}")

    return "\n".join(lines)
