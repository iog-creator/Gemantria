#!/usr/bin/env python3
"""
Guard: LM (Language Model) Health Check

Checks LM Studio endpoint availability and response validity.
Returns JSON verdict summarizing LM posture (lm_ready, lm_off).

Phase-3C P1: Updated to use LM Studio adapter from agentpm.adapters.lm_studio.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

# Import LM Studio adapter (E402: imports after sys.path modification)
from agentpm.adapters.lm_studio import lm_studio_chat  # noqa: E402
from scripts.config.env import get_lm_studio_settings  # noqa: E402


def check_lm_health() -> dict:
    """
    Check LM Studio health posture using the LM Studio adapter.

    Phase-3C P1: Uses agentpm.adapters.lm_studio.lm_studio_chat() for health check.

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
    settings = get_lm_studio_settings()
    endpoint = settings.get("base_url", "http://localhost:1234/v1")

    result: dict = {
        "ok": False,
        "mode": "lm_off",
        "details": {
            "endpoint": endpoint,
            "errors": [],
        },
    }

    # If LM Studio is not enabled or not configured, return lm_off
    if not settings.get("enabled") or not settings.get("base_url") or not settings.get("model"):
        result["details"]["errors"].append("lm_studio_disabled_or_unconfigured")
        return result

    # Health check: minimal chat completion request using adapter
    # Use tiny prompt and low max_tokens for fast response
    timeout = float(os.getenv("LM_HEALTH_TIMEOUT", "1.0"))
    health_result = lm_studio_chat(
        messages=[{"role": "user", "content": "hi"}],
        max_tokens=1,
        temperature=0.0,
        timeout=timeout,
    )

    # Map adapter response to health check format
    if health_result.get("ok") and health_result.get("mode") == "lm_on":
        result["ok"] = True
        result["mode"] = "lm_ready"
        return result
    else:
        # Extract error reason from adapter response
        reason = health_result.get("reason", "unknown_error")
        result["details"]["errors"].append(reason)
        return result


def main() -> int:
    """Main entry point."""
    health = check_lm_health()
    print(json.dumps(health, indent=2))
    # Always exit 0 (safe for CI; JSON indicates status)
    return 0


if __name__ == "__main__":
    sys.exit(main())
