"""In-memory store for Ollama request/response logging."""

import time
import uuid
from collections import deque
from typing import Any

# Maximum number of recent requests to keep
MAX_RECENT = 200

# In-memory storage
recent_requests: deque = deque(maxlen=MAX_RECENT)
active_requests: dict[str, dict[str, Any]] = {}


def create_request_log(
    endpoint: str,
    method: str,
    model: str | None = None,
    prompt_preview: str | None = None,
) -> dict[str, Any]:
    """Create a new request log entry."""
    log_id = str(uuid.uuid4())
    timestamp = time.time()

    log: dict[str, Any] = {
        "id": log_id,
        "timestamp": timestamp,
        "endpoint": endpoint,
        "method": method,
        "model": model,
        "promptPreview": prompt_preview,
        "inputTokens": None,
        "outputTokens": None,
        "durationMs": None,
        "status": "pending",
        "httpStatus": None,
        "errorMessage": None,
    }

    active_requests[log_id] = log
    recent_requests.appendleft(log)

    return log


def update_request_log(
    log_id: str,
    status: str | None = None,
    duration_ms: float | None = None,
    http_status: int | None = None,
    output_tokens: int | None = None,
    error_message: str | None = None,
) -> dict[str, Any] | None:
    """Update an existing request log entry."""
    # Try to find in active requests first
    log = active_requests.get(log_id)

    # If not in active, search recent requests
    if not log:
        for req in recent_requests:
            if req["id"] == log_id:
                log = req
                break

    if not log:
        return None

    # Update fields
    if status is not None:
        log["status"] = status
    if duration_ms is not None:
        log["durationMs"] = duration_ms
    if http_status is not None:
        log["httpStatus"] = http_status
    if output_tokens is not None:
        log["outputTokens"] = output_tokens
    if error_message is not None:
        log["errorMessage"] = error_message

    # Remove from active if no longer pending
    if log["status"] != "pending" and log_id in active_requests:
        del active_requests[log_id]

    return log


def get_monitor_snapshot() -> dict[str, Any]:
    """Get current monitor snapshot."""
    import datetime

    def convert_timestamp(ts: Any) -> str:
        """Convert timestamp to ISO string."""
        if isinstance(ts, str):
            # Already an ISO string
            return ts
        elif isinstance(ts, (int, float)):
            # Unix timestamp
            return datetime.datetime.fromtimestamp(ts, tz=datetime.UTC).isoformat()
        else:
            # Fallback to current time
            return datetime.datetime.now(tz=datetime.UTC).isoformat()

    # Convert timestamps to ISO strings for JSON serialization
    active_list = []
    for req in active_requests.values():
        req_copy = req.copy()
        req_copy["timestamp"] = convert_timestamp(req.get("timestamp"))
        active_list.append(req_copy)

    recent_list = []
    for req in recent_requests:
        req_copy = req.copy()
        req_copy["timestamp"] = convert_timestamp(req.get("timestamp"))
        recent_list.append(req_copy)

    return {
        "lastUpdated": datetime.datetime.now(tz=datetime.UTC).isoformat(),
        "activeRequests": active_list,
        "recentRequests": recent_list,
    }
