"""Ollama proxy router - forwards requests to Ollama and logs them."""

import json
import os
import time
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

from src.services.ollama_monitor.store import create_request_log, update_request_log

router = APIRouter(prefix="/api/ollama", tags=["ollama"])

# Ollama base URL from environment
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def infer_endpoint(pathname: str) -> str:
    """Infer endpoint type from pathname."""
    if "/generate" in pathname:
        return "generate"
    if "/chat" in pathname:
        return "chat"
    if "/embeddings" in pathname:
        return "embeddings"
    return "raw"


@router.post("/proxy/{path:path}")
async def proxy_ollama(request: Request, path: str):
    """Proxy POST requests to Ollama and log them."""
    # Read request body
    body_bytes = await request.body()
    body_text = body_bytes.decode("utf-8")

    # Parse body to extract model and prompt
    body: dict[str, Any] = {}
    try:
        body = json.loads(body_text) if body_text else {}
    except json.JSONDecodeError:
        pass

    model = body.get("model")
    prompt = None

    # Extract prompt from different formats
    if "prompt" in body:
        prompt = body["prompt"]
    elif "messages" in body:
        # Extract from messages array
        messages = body.get("messages", [])
        prompt = "\n".join(msg.get("content", "") for msg in messages if isinstance(msg, dict))

    prompt_preview = None
    if prompt:
        if isinstance(prompt, str):
            prompt_preview = prompt[:200]
        else:
            prompt_preview = json.dumps(prompt)[:200]

    endpoint = infer_endpoint(path)

    # Create request log
    log = create_request_log(
        endpoint=endpoint,
        method="POST",
        model=model,
        prompt_preview=prompt_preview,
    )

    started_at = time.time()

    try:
        # Forward request to Ollama
        target_url = f"{OLLAMA_BASE_URL}/{path}"

        # Forward headers (excluding host)
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)

        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                target_url,
                content=body_bytes,
                headers=headers,
            )

        duration_ms = (time.time() - started_at) * 1000

        # Try to extract output tokens from response
        output_tokens = None
        try:
            response_json = response.json()
            if isinstance(response_json, dict):
                # Ollama returns eval_count for tokens
                if "eval_count" in response_json:
                    output_tokens = response_json["eval_count"]
                elif "message" in response_json and "eval_count" in response_json.get("message", {}):
                    output_tokens = response_json["message"]["eval_count"]
        except (json.JSONDecodeError, KeyError):
            pass

        # Update log
        update_request_log(
            log["id"],
            status="success" if response.is_success else "error",
            duration_ms=duration_ms,
            http_status=response.status_code,
            output_tokens=output_tokens,
        )

        # Return response
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )

    except Exception as e:
        duration_ms = (time.time() - started_at) * 1000
        error_message = str(e)

        update_request_log(
            log["id"],
            status="error",
            duration_ms=duration_ms,
            http_status=500,
            error_message=error_message,
        )

        raise HTTPException(
            status_code=500,
            detail={"error": "Proxy to Ollama failed", "details": error_message},
        ) from e


@router.get("/proxy/{path:path}")
async def proxy_ollama_get(request: Request, path: str):
    """Proxy GET requests to Ollama and log them."""
    endpoint = infer_endpoint(path)

    log = create_request_log(
        endpoint=endpoint,
        method="GET",
        model=None,
        prompt_preview=None,
    )

    started_at = time.time()

    try:
        target_url = f"{OLLAMA_BASE_URL}/{path}"

        # Forward query params
        query_params = dict(request.query_params)

        headers = dict(request.headers)
        headers.pop("host", None)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                target_url,
                params=query_params,
                headers=headers,
            )

        duration_ms = (time.time() - started_at) * 1000

        update_request_log(
            log["id"],
            status="success" if response.is_success else "error",
            duration_ms=duration_ms,
            http_status=response.status_code,
        )

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )

    except Exception as e:
        duration_ms = (time.time() - started_at) * 1000

        update_request_log(
            log["id"],
            status="error",
            duration_ms=duration_ms,
            http_status=500,
            error_message=str(e),
        )

        raise HTTPException(
            status_code=500,
            detail={"error": "Proxy to Ollama failed", "details": str(e)},
        ) from e


@router.get("/monitor")
async def get_monitor():
    """Get Ollama monitor snapshot."""
    from src.services.ollama_monitor.store import get_monitor_snapshot
    from fastapi.responses import JSONResponse

    try:
        snapshot = get_monitor_snapshot()
        return JSONResponse(content=snapshot)
    except Exception as e:
        from src.infra.structured_logger import get_logger

        LOG = get_logger("ollama_monitor")
        LOG.error(f"Failed to get monitor snapshot: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Failed to get monitor snapshot", "details": str(e)})
