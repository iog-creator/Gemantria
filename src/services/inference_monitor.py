# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`

"""Inference model monitoring helpers.

Provides centralized functions for querying inference model activity from
both Ollama and LM Studio providers.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import requests

from scripts.config.env import get_rw_dsn
from src.infra.structured_logger import get_logger

LOG = get_logger("inference_monitor")


def get_ollama_loaded_models(base_url: str) -> list[dict[str, Any]]:
    """Get list of loaded models from Ollama.

    Args:
        base_url: Ollama base URL (e.g., "http://127.0.0.1:11434")

    Returns:
        List of model dicts with "id" and "name" keys.
        Returns empty list if Ollama is unavailable.
    """
    try:
        url = f"{base_url.rstrip('/')}/api/tags"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        models = []
        for model in data.get("models", []):
            model_id = model.get("name", "")
            models.append({"id": model_id, "name": model_id})
        return models
    except Exception as e:
        LOG.debug(f"Failed to get Ollama models from {base_url}: {e}")
        return []


def get_lmstudio_loaded_models(base_urls: list[str]) -> list[dict[str, Any]]:
    """Get list of loaded models from LM Studio instances.

    Args:
        base_urls: List of LM Studio base URLs to query

    Returns:
        List of model dicts with "id" and "base_url" keys.
        Returns empty list if all LM Studio instances are unavailable.
    """
    models = []
    for base_url in base_urls:
        try:
            # Ensure base_url ends with /v1
            clean_url = base_url.rstrip("/")
            if not clean_url.endswith("/v1"):
                clean_url = f"{clean_url}/v1"
            url = f"{clean_url}/models"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            for model in data.get("data", []):
                model_id = model.get("id", "")
                models.append({"id": model_id, "base_url": base_url})
        except Exception as e:
            LOG.debug(f"Failed to get LM Studio models from {base_url}: {e}")
            continue
    return models


def extract_file_context(args_json: dict[str, Any]) -> str:
    """Extract file/process context from agent_run args_json.

    Args:
        args_json: The args_json field from control.agent_run

    Returns:
        String describing the file/process context, or "unknown" if not available.
    """
    if not args_json:
        return "unknown"

    # Try call_site first (most specific)
    call_site = args_json.get("call_site")
    if call_site:
        return call_site

    # Try app_name as fallback
    app_name = args_json.get("app_name")
    if app_name:
        return app_name

    return "unknown"


def extract_output_preview(result_json: dict[str, Any]) -> str:
    """Extract output preview from agent_run result_json.

    Args:
        result_json: The result_json field from control.agent_run

    Returns:
        Truncated output preview string, or empty string if not available.
    """
    if not result_json:
        return ""

    # Try to get response content from nested structure
    response = result_json.get("response")
    if response:
        # OpenAI-compatible format
        choices = response.get("choices", [])
        if choices and isinstance(choices, list) and len(choices) > 0:
            message = choices[0].get("message", {})
            content = message.get("content", "")
            if content:
                # Truncate to 200 chars
                return content[:200] + ("..." if len(content) > 200 else "")

        # Direct content field
        content = response.get("content", "")
        if content:
            return content[:200] + ("..." if len(content) > 200 else "")

    # Fallback to response_length if available
    response_length = result_json.get("response_length")
    if response_length:
        return f"[{response_length} chars]"

    return ""


def simplify_inference_output(output_preview: str, endpoint: str | None = None) -> str:
    """Simplify inference output for orchestrator readability.

    Args:
        output_preview: Raw output preview text
        endpoint: Endpoint type (e.g., "embeddings", "chat", "generate")

    Returns:
        Simplified human-readable summary (e.g., "embedding complete", "two examples")
    """
    if not output_preview:
        return "—"

    # For embeddings, check if it's a vector
    if endpoint == "embeddings" or "embedding" in output_preview.lower():
        # Check if it's a list/array of numbers
        if "[" in output_preview and "]" in output_preview:
            # Count dimensions or just say "embedding complete"
            return "embedding complete"
        return "embedding complete"

    # For chat/generate, try to extract key information
    preview_lower = output_preview.lower()

    # Check for common patterns
    if "error" in preview_lower or "failed" in preview_lower:
        return "error occurred"

    # Count examples or items
    if "example" in preview_lower:
        # Try to extract number
        import re

        match = re.search(r"(\d+)\s+example", preview_lower)
        if match:
            count = match.group(1)
            return f"{count} examples"
        return "examples found"

    # Check for list-like structures
    if preview_lower.count("[") > 0 and preview_lower.count("]") > 0:
        # Count items in list
        items = preview_lower.split(",")
        if len(items) > 1:
            return f"{len(items)} items"
        return "list output"

    # For long text, just truncate to first meaningful phrase
    if len(output_preview) > 100:
        # Try to find first sentence
        sentences = output_preview.split(".")
        if sentences and len(sentences[0]) < 80:
            return sentences[0].strip() + "..."
        return output_preview[:80] + "..."

    return output_preview


def get_lmstudio_recent_activity(days: int = 2, limit: int = 1000) -> list[dict[str, Any]]:
    """Get recent LM Studio activity from control.agent_run table (last N days).

    Args:
        days: Number of days to look back (default: 2)
        limit: Maximum number of recent activities to return (default: 1000)

    Returns:
        List of activity dicts with:
        - id: str
        - model: str (extracted from args_json or result_json)
        - timestamp: str (ISO format)
        - input_tokens: int | None
        - output_tokens: int | None
        - duration_ms: int | None
        - status: str ("success" or "error")
        - call_site: str
        - app_name: str
        - output_preview: str
        - file_context: str
        - inference_summary: str (simplified output for orchestrator)
    """
    dsn = get_rw_dsn()
    if not dsn:
        LOG.debug("No DSN available for LM Studio activity query")
        return []

    try:
        import psycopg  # noqa: PLC0415
    except ImportError:
        LOG.debug("psycopg not available for LM Studio activity query")
        return []

    try:
        with psycopg.connect(dsn) as conn, conn.cursor() as cur:
            # Filter by last N days
            cur.execute(
                """
                SELECT id, tool, args_json, result_json, violations_json, created_at
                FROM control.agent_run
                WHERE tool = 'lm_studio'
                  AND created_at >= NOW() - INTERVAL '%s days'
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (days, limit),
            )

            activities = []
            for row in cur.fetchall():
                run_id, _tool, args_json_raw, result_json_raw, violations_json_raw, created_at = row

                # Parse JSON fields
                args_json = json.loads(args_json_raw) if args_json_raw else {}
                result_json = json.loads(result_json_raw) if result_json_raw else {}
                violations_json = json.loads(violations_json_raw) if violations_json_raw else []

                # Determine status
                status = "error" if violations_json else "success"
                if not result_json.get("ok", False):
                    status = "error"

                # Extract model from args_json or result_json
                model = "unknown"
                if "model" in args_json:
                    model = args_json["model"]
                elif "model" in result_json:
                    model = result_json["model"]

                # Extract token counts
                input_tokens = None
                output_tokens = None
                usage = result_json.get("usage", {})
                if isinstance(usage, dict):
                    input_tokens = usage.get("prompt_tokens")
                    output_tokens = usage.get("completion_tokens") or usage.get("total_tokens")

                # Extract duration
                duration_ms = result_json.get("latency_ms")

                # Extract context
                call_site = args_json.get("call_site", "unknown")
                app_name = args_json.get("app_name", "unknown")
                file_context = extract_file_context(args_json)
                output_preview = extract_output_preview(result_json)

                # Infer endpoint type from call_site or args
                endpoint = None
                if "embed" in call_site.lower() or "embed" in str(args_json).lower():
                    endpoint = "embeddings"
                elif "chat" in call_site.lower() or "chat" in str(args_json).lower():
                    endpoint = "chat"
                elif "generate" in call_site.lower() or "generate" in str(args_json).lower():
                    endpoint = "generate"

                # Create simplified inference summary
                inference_summary = simplify_inference_output(output_preview, endpoint)

                # Format timestamp
                if isinstance(created_at, datetime):
                    timestamp = created_at.isoformat()
                elif isinstance(created_at, str):
                    timestamp = created_at
                else:
                    timestamp = datetime.now(UTC).isoformat()

                activities.append(
                    {
                        "id": str(run_id),
                        "model": model,
                        "timestamp": timestamp,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "duration_ms": duration_ms,
                        "status": status,
                        "call_site": call_site,
                        "app_name": app_name,
                        "output_preview": output_preview,
                        "file_context": file_context,
                        "inference_summary": inference_summary,
                        "endpoint": endpoint,
                    }
                )

            return activities
    except Exception as e:
        LOG.warning(f"Failed to query LM Studio activity: {e}")
        return []
