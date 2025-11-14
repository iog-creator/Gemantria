#!/usr/bin/env python3
"""
Guard: LM (Language Model) Health Check

Checks LM Studio endpoint availability and response validity.
Returns JSON verdict summarizing LM posture (lm_ready, lm_off).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests
from requests.exceptions import ConnectionError, Timeout, RequestException

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))


def get_lm_studio_endpoint() -> str:
    """
    Get LM Studio endpoint URL from environment.

    Returns:
        Base URL for LM Studio (e.g., "http://127.0.0.1:1234")
    """
    # Check LM_STUDIO_HOST first (primary)
    host = os.getenv("LM_STUDIO_HOST")
    if host:
        if not host.startswith("http"):
            # Assume http:// if protocol missing
            host = f"http://{host}"
        return host

    # Fallback to LM_EMBED_HOST/LM_EMBED_PORT
    embed_host = os.getenv("LM_EMBED_HOST", "127.0.0.1")
    embed_port = os.getenv("LM_EMBED_PORT", "1234")
    return f"http://{embed_host}:{embed_port}"


def check_lm_health() -> dict:
    """
    Check LM Studio health posture.

    Returns:
        Dictionary with health status:
        {
            "ok": bool,
            "mode": "lm_ready" | "lm_off",
            "details": {
                "endpoint": str,
                "errors": list[str],
            },
        }
    """
    endpoint = get_lm_studio_endpoint()
    chat_endpoint = f"{endpoint}/v1/chat/completions"

    result: dict = {
        "ok": False,
        "mode": "lm_off",
        "details": {
            "endpoint": endpoint,
            "errors": [],
        },
    }

    # Health check: minimal chat completion request
    # Use tiny prompt and low max_tokens for fast response
    payload = {
        "model": "test",  # Model name doesn't matter for health check
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 1,
        "temperature": 0.0,
    }

    try:
        # Short timeout (0.5-1.0 seconds) to avoid hanging when LM Studio is off
        timeout = float(os.getenv("LM_HEALTH_TIMEOUT", "1.0"))
        response = requests.post(
            chat_endpoint,
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )

        # Check if response is valid
        if response.status_code == 200:
            try:
                data = response.json()
                # Verify response has expected structure (has choices or error)
                if "choices" in data or "error" in data:
                    result["ok"] = True
                    result["mode"] = "lm_ready"
                    return result
                else:
                    result["details"]["errors"].append(
                        "invalid_response: Response missing expected fields (choices/error)"
                    )
                    return result
            except json.JSONDecodeError:
                result["details"]["errors"].append("invalid_response: Response is not valid JSON")
                return result
        else:
            result["details"]["errors"].append(f"http_error: HTTP {response.status_code}: {response.text[:100]}")
            return result

    except ConnectionError as e:
        result["details"]["errors"].append(f"connection_refused: {e}")
        return result
    except Timeout:
        result["details"]["errors"].append(f"timeout: Request timed out after {timeout}s")
        return result
    except RequestException as e:
        result["details"]["errors"].append(f"request_error: {e}")
        return result
    except Exception as e:
        result["details"]["errors"].append(f"unexpected_error: {e}")
        return result


def main() -> int:
    """Main entry point."""
    health = check_lm_health()
    print(json.dumps(health, indent=2))
    # Always exit 0 (safe for CI; JSON indicates status)
    return 0


if __name__ == "__main__":
    sys.exit(main())
