#!/usr/bin/env python3
from __future__ import annotations

import os
import json
import re
from typing import Callable, TypeVar

from dotenv import load_dotenv, find_dotenv

_T = TypeVar("_T")
_REDACT = re.compile(r"://[^@]*@")

_LOADED = False


def _ensure_loaded() -> None:
    global _LOADED
    if not _LOADED:
        # Load nearest .env if present (non-fatal)
        path = find_dotenv(usecwd=True)
        if path:
            load_dotenv(path, override=False)
        _LOADED = True


def redact(value: str | None) -> str | None:
    if value is None:
        return None
    return _REDACT.sub("://***@", value)


def env(
    key: str, default: _T | None = None, *, cast: Callable[[str], _T] | None = None, required: bool = False
) -> _T | None:
    """Fetch an env var with optional casting and 'required' enforcement."""
    _ensure_loaded()
    raw = os.getenv(key)
    if raw is None or raw == "":
        if required and default is None:
            raise RuntimeError(f"missing required env: {key}")
        return default
    return cast(raw) if cast else raw  # type: ignore[return-value]


def get_rw_dsn() -> str | None:
    """Write-enabled DSN preference: ATLAS_DSN_RW → GEMATRIA_DSN."""
    return env("ATLAS_DSN_RW") or env("GEMATRIA_DSN")


def get_ro_dsn() -> str | None:
    """Read DSN preference: ATLAS_DSN → (fallback) RW."""
    return env("ATLAS_DSN") or get_rw_dsn()


def openai_cfg() -> dict:
    """OpenAI-compatible cfg; supports either OPENAI_BASE_URL or LM_STUDIO_HOST, adds /v1 if missing."""
    host = env("OPENAI_BASE_URL") or env("LM_STUDIO_HOST")
    if host:
        u = host.rstrip("/")
        if not u.endswith("/v1"):
            u = f"{u}/v1"
        base_url = u
    else:
        # Fallback: construct from LM_EMBED_HOST and LM_EMBED_PORT (from .env.example)
        embed_host = env("LM_EMBED_HOST", "localhost")
        embed_port = env("LM_EMBED_PORT", "9994")
        base_url = f"http://{embed_host}:{embed_port}/v1"
    return {
        "api_key": env("OPENAI_API_KEY", "sk-local-placeholder"),
        "base_url": base_url,
        "embed_model": env("LM_EMBED_MODEL", "text-embedding-bge-m3"),
    }


def snapshot(path: str) -> None:
    """Write a redacted snapshot of key env vars for evidence (no secrets)."""
    _ensure_loaded()
    cfg = openai_cfg()
    data = {
        "ATLAS_DSN": redact(env("ATLAS_DSN")),
        "ATLAS_DSN_RW": redact(env("ATLAS_DSN_RW")),
        "GEMATRIA_DSN": redact(env("GEMATRIA_DSN")),
        "OPENAI_BASE_URL": cfg["base_url"],  # Use resolved value from openai_cfg()
        "LM_EMBED_MODEL": cfg["embed_model"],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
