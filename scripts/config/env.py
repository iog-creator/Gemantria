#!/usr/bin/env python3
from __future__ import annotations

import os
import json
import re
from typing import Callable, TypeVar

# Optional dotenv support, disabled when DISABLE_DOTENV=1
try:
    if os.environ.get("DISABLE_DOTENV", "0") != "1":
        from dotenv import load_dotenv, find_dotenv  # type: ignore
    else:
        load_dotenv = None
        find_dotenv = None
except Exception:
    load_dotenv = None
    find_dotenv = None

_T = TypeVar("_T")
_REDACT = re.compile(r"://[^@]*@")

_LOADED = False


def _ensure_loaded() -> None:
    global _LOADED
    if not _LOADED:
        # Load nearest .env if present (non-fatal) and not disabled
        if load_dotenv is not None and find_dotenv is not None:
            path = find_dotenv(usecwd=True)
            if path:
                load_dotenv(path, override=False)
        _LOADED = True


def redact(value: str | None) -> str | None:
    if value is None:
        return None
    return _REDACT.sub("://***@", value)


def env(
    key: str,
    default: _T | None = None,
    *,
    cast: Callable[[str], _T] | None = None,
    required: bool = False,
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
    """
    Write-enabled DSN precedence: GEMATRIA_DSN → RW_DSN → AI_AUTOMATION_DSN → ATLAS_DSN_RW → ATLAS_DSN.
    Set DISABLE_DOTENV=1 in tests to prevent .env from affecting resolution.
    """
    for key in ("GEMATRIA_DSN", "RW_DSN", "AI_AUTOMATION_DSN", "ATLAS_DSN_RW", "ATLAS_DSN"):
        value = env(key)
        if value:
            return value
    return None


def get_ro_dsn() -> str | None:
    """
    Read-only DSN precedence: GEMATRIA_RO_DSN | ATLAS_DSN_RO (peers) → ATLAS_DSN → (fallback) RW.
    RO-DSN peer equivalence: GEMATRIA_RO_DSN and ATLAS_DSN_RO are equal primaries for tag builds.
    """
    # Peer equivalence: try both RO DSNs as primaries
    ro = env("GEMATRIA_RO_DSN") or env("ATLAS_DSN_RO")
    if ro:
        return ro
    # Fallback to generic ATLAS_DSN, then RW
    return env("ATLAS_DSN") or get_rw_dsn()


def get_bible_db_dsn() -> str | None:
    """
    Bible database DSN (read-only) precedence: BIBLE_DB_DSN → BIBLE_RO_DSN → RO_DSN → ATLAS_DSN_RO → ATLAS_DSN.
    Set DISABLE_DOTENV=1 in tests to prevent .env from affecting resolution.
    """
    for key in ("BIBLE_DB_DSN", "BIBLE_RO_DSN", "RO_DSN", "ATLAS_DSN_RO", "ATLAS_DSN"):
        value = env(key)
        if value:
            return value
    return None


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


def get_lm_studio_settings() -> dict[str, str | None | bool]:
    """
    Centralized LM Studio config loader.
    Only place where we touch os.environ for LM_STUDIO_*.

    Phase-6: LM_STUDIO_ENABLED is now a master switch. When false, LM Studio
    is disabled regardless of base_url/model configuration.

    Returns:
        Dictionary with:
        - enabled: bool (True if LM_STUDIO_ENABLED is true AND base_url/model are present)
        - base_url: str | None (from LM_STUDIO_BASE_URL, default: http://localhost:1234/v1)
        - model: str | None (from LM_STUDIO_MODEL)
        - api_key: str | None (from LM_STUDIO_API_KEY, optional)
    """
    _ensure_loaded()
    base_url = env("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
    model = env("LM_STUDIO_MODEL")
    api_key = env("LM_STUDIO_API_KEY")
    enabled_flag = env("LM_STUDIO_ENABLED", "false").lower()

    # Phase-6: LM_STUDIO_ENABLED is a master switch
    # Must be explicitly enabled AND have base_url and model configured
    flag_enabled = enabled_flag in ("1", "true", "yes")
    enabled = bool(flag_enabled and base_url and model)

    return {
        "enabled": enabled,
        "base_url": base_url,
        "model": model,
        "api_key": api_key,
    }


def get_lm_studio_enabled() -> bool:
    """
    Phase-6: Check if LM Studio is enabled via LM_STUDIO_ENABLED flag.

    Returns:
        True if LM_STUDIO_ENABLED is set to true/1/yes, False otherwise.
    """
    _ensure_loaded()
    enabled_flag = env("LM_STUDIO_ENABLED", "false").lower()
    return enabled_flag in ("1", "true", "yes")


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
