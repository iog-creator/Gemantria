#!/usr/bin/env python3
"""
LM Studio Control-Plane Logging

Phase-3C P1: Wraps LM Studio adapter calls with control-plane logging.
Writes to control.agent_run when DB is available; graceful no-op when DB is unavailable.
"""

from __future__ import annotations

import time
from typing import Any

from agentpm.adapters.lm_studio import lm_studio_chat
from scripts.config.env import get_rw_dsn


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
