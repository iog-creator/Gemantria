#!/usr/bin/env python3
"""
LM Studio Adapter

Phase-3C P0: LM Studio HTTP client adapter with hermetic lm_off behavior.
"""

from __future__ import annotations

from typing import Any

import requests
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout

from scripts.config.env import get_lm_studio_settings


def lm_studio_chat(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.0,
    max_tokens: int = 512,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """
    Call LM Studio if configured, otherwise return a hermetic lm_off payload.

    Args:
        messages: List of message dicts with "role" and "content" keys.
        temperature: Sampling temperature (default: 0.0).
        max_tokens: Maximum tokens to generate (default: 512).
        timeout: Request timeout in seconds (default: 30.0).

    Returns:
        Dictionary with:
        - ok: bool (True if call succeeded)
        - mode: "lm_on" | "lm_off"
        - reason: str | None (error reason if mode is lm_off)
        - response: dict | None (LM Studio API response if ok)
    """
    settings = get_lm_studio_settings()

    if not settings["enabled"] or not settings["base_url"] or not settings["model"]:
        return {
            "ok": False,
            "mode": "lm_off",
            "reason": "lm_studio_disabled_or_unconfigured",
            "response": None,
        }

    try:
        base_url = settings["base_url"].rstrip("/")
        if not base_url.endswith("/v1"):
            base_url = f"{base_url}/v1"

        url = f"{base_url}/chat/completions"
        payload = {
            "model": settings["model"],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        headers = {}
        if settings["api_key"]:
            headers["Authorization"] = f"Bearer {settings['api_key']}"

        resp = requests.post(
            url,
            json=payload,
            headers=headers if headers else None,
            timeout=timeout,
        )
        resp.raise_for_status()

        return {
            "ok": True,
            "mode": "lm_on",
            "reason": None,
            "response": resp.json(),
        }

    except ConnectionError as e:
        return {
            "ok": False,
            "mode": "lm_off",
            "reason": f"connection_error: {e}",
            "response": None,
        }
    except Timeout as e:
        return {
            "ok": False,
            "mode": "lm_off",
            "reason": f"timeout: {e}",
            "response": None,
        }
    except HTTPError as e:
        return {
            "ok": False,
            "mode": "lm_off",
            "reason": f"http_error: {e.response.status_code if e.response else 'unknown'}",
            "response": None,
        }
    except RequestException as e:
        return {
            "ok": False,
            "mode": "lm_off",
            "reason": f"request_error: {e}",
            "response": None,
        }
    except Exception as e:  # noqa: BLE001
        return {
            "ok": False,
            "mode": "lm_off",
            "reason": f"unexpected_error: {e}",
            "response": None,
        }
