#!/usr/bin/env python3
"""
LM Studio Control-Plane Logging

Phase-3C P1: Wraps LM Studio adapter calls with control-plane logging.
Writes to control.agent_run when DB is available; graceful no-op when DB is unavailable.

Phase-6: Added guarded_lm_call() wrapper that respects LM_STUDIO_ENABLED flag.
"""

from __future__ import annotations

import time
from typing import Any, Callable

from agentpm.adapters.lm_studio import lm_studio_chat
from agentpm.runtime.lm_budget import check_lm_budget
from scripts.config.env import get_lm_studio_enabled, get_rw_dsn


def _write_agent_run(
    tool: str,
    args_json: dict[str, Any],
    result_json: dict[str, Any],
    violations_json: list[dict[str, Any]] | None = None,
) -> str | None:
    """
    Write agent_run row to control.agent_run table.

    Returns:
        Run ID (UUID string) if successful, None if DB unavailable or error.
    """
    try:
        import psycopg  # noqa: PLC0415
    except ImportError:
        return None

    dsn = get_rw_dsn()
    if not dsn:
        return None

    try:
        with psycopg.connect(dsn) as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO control.agent_run
                (project_id, tool, args_json, result_json, violations_json)
                VALUES (1, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    tool,
                    psycopg.types.json.dumps(args_json),
                    psycopg.types.json.dumps(result_json),
                    psycopg.types.json.dumps(violations_json or []),
                ),
            )
            run_id = cur.fetchone()[0]
            conn.commit()
            return str(run_id)
    except Exception:
        # Graceful no-op when DB unavailable (hermetic DB-off behavior)
        return None


def lm_studio_chat_with_logging(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.0,
    max_tokens: int = 512,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """
    Call LM Studio adapter with control-plane logging.

    Phase-3C P1: Wraps lm_studio_chat() and logs to control.agent_run when DB is available.

    Args:
        messages: List of message dicts with "role" and "content" keys.
        temperature: Sampling temperature (default: 0.0).
        max_tokens: Maximum tokens to generate (default: 512).
        timeout: Request timeout in seconds (default: 30.0).

    Returns:
        Dictionary from lm_studio_chat() with same structure:
        {
            "ok": bool,
            "mode": "lm_on" | "lm_off",
            "reason": str | None,
            "response": dict | None,
        }
    """
    start_time = time.time()

    # Prepare args for logging
    args_json = {
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "timeout": timeout,
    }

    # Call LM Studio adapter
    result = lm_studio_chat(
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )

    # Calculate latency
    latency_ms = int((time.time() - start_time) * 1000)

    # Prepare result for logging
    result_json: dict[str, Any] = {
        "ok": result.get("ok", False),
        "mode": result.get("mode", "lm_off"),
        "latency_ms": latency_ms,
    }

    # Extract response details if available
    response = result.get("response")
    if response:
        # Extract token counts if available
        if usage := response.get("usage"):
            result_json["usage"] = usage
        # Extract response length
        if choices := response.get("choices"):
            content = choices[0].get("message", {}).get("content", "")
            result_json["response_length"] = len(content)

    # Prepare violations (empty for successful calls, error details for failures)
    violations_json: list[dict[str, Any]] = []
    if not result.get("ok"):
        violations_json.append(
            {
                "type": "lm_studio_error",
                "reason": result.get("reason", "unknown_error"),
            }
        )

    # Log to control-plane (graceful no-op if DB unavailable)
    _write_agent_run(
        tool="lm_studio",
        args_json=args_json,
        result_json=result_json,
        violations_json=violations_json,
    )

    return result


def guarded_lm_call(
    call_site: str,
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.0,
    max_tokens: int = 512,
    timeout: float = 30.0,
    fallback_fn: Callable[[list[dict[str, str]], dict[str, Any]], dict[str, Any]] | None = None,
    fallback_kwargs: dict[str, Any] | None = None,
    app_name: str | None = None,
) -> dict[str, Any]:
    """
    Phase-6: Guarded LM Studio call wrapper with call_site tracking and budget enforcement.

    This function respects the LM_STUDIO_ENABLED flag and budget limits. When enabled, it uses
    lm_studio_chat_with_logging() with control-plane observability. When disabled, budget exceeded,
    or LM Studio is unavailable, it falls back to the provided fallback function.

    Args:
        call_site: Identifier for where this call is made (e.g., "storymaker.idea_gen")
        messages: List of message dicts with "role" and "content" keys.
        temperature: Sampling temperature (default: 0.0).
        max_tokens: Maximum tokens to generate (default: 512).
        timeout: Request timeout in seconds (default: 30.0).
        fallback_fn: Optional fallback function to call when LM Studio is disabled/unavailable.
            Should accept (messages, kwargs) and return a dict with "ok" and "response" keys.
        fallback_kwargs: Optional kwargs to pass to fallback function.
        app_name: Application identifier for budget tracking (default: derived from call_site).

    Returns:
        Dictionary with:
        - ok: bool (True if call succeeded)
        - mode: "lm_on" | "lm_off" | "fallback" | "budget_exceeded"
        - reason: str | None (error reason if mode is lm_off or budget_exceeded)
        - response: dict | None (LM Studio or fallback response if ok)
        - call_site: str (the call_site identifier)
    """
    # Derive app_name from call_site if not provided
    if app_name is None:
        # Extract app name from call_site (e.g., "gemantria.runtime.generate_text" -> "gemantria.runtime")
        parts = call_site.split(".")
        app_name = ".".join(parts[:2]) if len(parts) >= 2 else parts[0] if parts else "unknown"

    # Check if LM Studio is enabled
    lm_enabled = get_lm_studio_enabled()

    if not lm_enabled:
        # LM Studio disabled - use fallback if provided
        if fallback_fn:
            fallback_kwargs = fallback_kwargs or {}
            result = fallback_fn(messages, fallback_kwargs)
            return {
                "ok": result.get("ok", False),
                "mode": "fallback",
                "reason": "lm_studio_disabled",
                "response": result.get("response"),
                "call_site": call_site,
            }
        # No fallback - return disabled response
        return {
            "ok": False,
            "mode": "lm_off",
            "reason": "lm_studio_disabled",
            "response": None,
            "call_site": call_site,
        }

    # Phase-6 6B: Check budget before making LM Studio call
    estimated_tokens = max_tokens  # Use max_tokens as estimate
    budget_ok = check_lm_budget(app_name, tokens=estimated_tokens)

    if not budget_ok:
        # Budget exceeded - skip LM Studio and use fallback
        if fallback_fn:
            fallback_kwargs = fallback_kwargs or {}
            result = fallback_fn(messages, fallback_kwargs)
            # Log budget exceeded to control-plane
            _write_agent_run(
                tool="lm_studio",
                args_json={
                    "call_site": call_site,
                    "app_name": app_name,
                    "messages": messages,
                    "max_tokens": max_tokens,
                },
                result_json={
                    "ok": False,
                    "mode": "budget_exceeded",
                    "reason": "budget_exceeded",
                },
                violations_json=[
                    {
                        "type": "budget_exceeded",
                        "reason": f"Budget exceeded for {app_name}",
                    }
                ],
            )
            return {
                "ok": result.get("ok", False),
                "mode": "budget_exceeded",
                "reason": "budget_exceeded",
                "response": result.get("response"),
                "call_site": call_site,
            }
        # No fallback - return budget exceeded response
        _write_agent_run(
            tool="lm_studio",
            args_json={
                "call_site": call_site,
                "app_name": app_name,
                "messages": messages,
                "max_tokens": max_tokens,
            },
            result_json={
                "ok": False,
                "mode": "budget_exceeded",
                "reason": "budget_exceeded",
            },
            violations_json=[
                {
                    "type": "budget_exceeded",
                    "reason": f"Budget exceeded for {app_name}",
                }
            ],
        )
        return {
            "ok": False,
            "mode": "budget_exceeded",
            "reason": "budget_exceeded",
            "response": None,
            "call_site": call_site,
        }

    # LM Studio enabled and within budget - try to use it
    result = lm_studio_chat_with_logging(
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )

    # Add app_name and call_site to result for observability
    if isinstance(result.get("response"), dict):
        result["response"]["app_name"] = app_name
    result["call_site"] = call_site

    # If LM Studio call failed and fallback is available, use it
    if not result.get("ok") and fallback_fn:
        fallback_kwargs = fallback_kwargs or {}
        fallback_result = fallback_fn(messages, fallback_kwargs)
        return {
            "ok": fallback_result.get("ok", False),
            "mode": "fallback",
            "reason": result.get("reason", "lm_studio_unavailable"),
            "response": fallback_result.get("response"),
            "call_site": call_site,
        }

    return result
