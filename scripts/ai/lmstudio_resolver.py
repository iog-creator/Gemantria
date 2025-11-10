# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

import os


def base_url() -> str:
    """Resolve LM Studio OpenAI-compatible base URL.

    Precedence: LMSTUDIO_BASE_URL (full, includes /v1) > LM_STUDIO_HOST (append /v1) > construct from LM_EMBED_HOST/LM_EMBED_PORT > default."""
    raw = os.environ.get("LMSTUDIO_BASE_URL")
    if raw:
        return raw.rstrip("/")
    host = os.environ.get("LM_STUDIO_HOST", "").rstrip("/")
    if host:
        return f"{host}/v1"
    # Fallback: construct from LM_EMBED_HOST and LM_EMBED_PORT (from .env.example)
    embed_host = os.environ.get("LM_EMBED_HOST", "localhost")
    embed_port = os.environ.get("LM_EMBED_PORT", "9994")
    return f"http://{embed_host}:{embed_port}/v1"
