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

_PROFILE_DEFAULTS = {
    "LEGACY": {
        "embedding_model": "text-embedding-bge-m3",
        "reranker_model": "qwen.qwen3-reranker-0.6b",
        "local_agent_model": "qwen/qwen3-8b",
        "theology_model": "christian-bible-expert-v2.0-12b",
    },
    "GRANITE": {
        "embedding_model": "ibm-granite/granite-embedding-english-r2",
        "reranker_model": "ibm-granite/granite-embedding-reranker-english-r2",
        "local_agent_model": "ibm-granite/granite-4.0-h-tiny-GGUF",
        "theology_model": "christian-bible-expert-v2.0-12b",
    },
}


def _ensure_loaded() -> None:
    global _LOADED
    if not _LOADED:
        # Load nearest .env if present (non-fatal) and not disabled
        if load_dotenv is not None and find_dotenv is not None:
            path = find_dotenv(usecwd=True)
            if path:
                load_dotenv(path, override=False)
            # Also load .env.local if present (overrides .env values)
            from pathlib import Path

            env_local = Path.cwd() / ".env.local"
            if env_local.exists():
                load_dotenv(env_local, override=True)
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
        - base_url: str | None (from LM_STUDIO_BASE_URL or LM_STUDIO_HOST, default: http://localhost:1234/v1)
        - model: str | None (from LM_STUDIO_MODEL)
        - api_key: str | None (from LM_STUDIO_API_KEY, optional)
    """
    _ensure_loaded()

    # Check LM_STUDIO_BASE_URL first, then fall back to LM_STUDIO_HOST
    base_url = env("LM_STUDIO_BASE_URL")
    if not base_url:
        # Try LM_STUDIO_HOST (legacy format)
        lm_host = env("LM_STUDIO_HOST")
        if lm_host:
            # Ensure it has /v1 suffix
            if not lm_host.endswith("/v1"):
                # Remove trailing slash if present, then add /v1
                base_url = f"{lm_host.rstrip('/')}/v1"
            else:
                base_url = lm_host
        else:
            # Fall back to LM_EMBED_HOST/LM_EMBED_PORT (older legacy format)
            embed_host = env("LM_EMBED_HOST", "localhost")
            embed_port = env("LM_EMBED_PORT", "1234")
            base_url = f"http://{embed_host}:{embed_port}/v1"

    # Default if nothing is set
    if not base_url:
        base_url = "http://localhost:1234/v1"

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


def get_lm_model_config() -> dict[str, str | None]:
    """
    Phase-7B/7E: Centralized LM model configuration loader.

    This is the SSOT for local/remote LM configuration. It is intentionally
    provider-agnostic and supports both LM Studio and Ollama:

      provider:
        - "lmstudio": use OPENAI_BASE_URL and the LM Studio adapter
        - "ollama":   use OLLAMA_BASE_URL and the Ollama adapter
        - other:      reserved for future providers

    Normalizes canonical env vars with legacy fallbacks for backward compatibility.
    All model configuration should use this function instead of direct os.getenv() calls.

    Returns:
        Dictionary with:
        - provider: str - Default inference provider (default: "lmstudio")
        - ollama_enabled: bool - Whether Ollama is enabled (default: True)
        - lm_studio_enabled: bool - Whether LM Studio is enabled (from LM_STUDIO_ENABLED)
        - base_url: str - Base URL for OpenAI-compatible API (default: "http://127.0.0.1:9994/v1")
        - ollama_base_url: str - Base URL for Ollama API (default: "http://127.0.0.1:11434")
        - local_agent_provider: str | None - Provider for local agent slot (defaults to provider)
        - local_agent_model: str | None - Local agent/workflow model ID
        - embedding_provider: str | None - Provider for embedding slot (defaults to provider)
        - embedding_model: str | None - Embedding model ID (canonical: EMBEDDING_MODEL, legacy: LM_EMBED_MODEL)
        - reranker_provider: str | None - Provider for reranker slot (defaults to provider)
        - reranker_model: str | None - Reranker model ID (canonical: RERANKER_MODEL, legacy: QWEN_RERANKER_MODEL)
        - reranker_strategy: str | None - Reranker strategy (default: "embedding_only", options: "embedding_only", "granite_llm")
        - theology_provider: str | None - Provider for theology slot (default: "lmstudio")
        - theology_model: str | None - Theology/general reasoning model ID
        - theology_lmstudio_base_url: str | None - LM Studio base URL for theology (default: "http://127.0.0.1:1234")
        - theology_lmstudio_api_key: str | None - LM Studio API key for theology (optional)
        - math_model: str | None - Math verification model ID
        - retrieval_profile: str - Active retrieval profile ("LEGACY" default)
        - granite_embedding_model: str | None - Granite embedding model ID reference
        - granite_reranker_model: str | None - Granite reranker model ID reference
        - granite_local_agent_model: str | None - Granite local agent model ID reference
        - legacy_profile_defaults: dict - Reference defaults for LEGACY profile slots
        - granite_profile_defaults: dict - Reference defaults for GRANITE profile slots
        - planning_provider: str | None - Optional planning lane provider (Gemini/Codex/local)
        - planning_model: str | None - Model/CLI identifier for planning lane
        - gemini_enabled: bool - Whether Gemini CLI integrations are allowed
        - codex_enabled: bool - Whether Codex CLI integrations are allowed
        - gemini_cli_path: str - CLI executable path for Gemini
        - codex_cli_path: str - CLI executable path for Codex

    Legacy Support:
        - LM_EMBED_MODEL → EMBEDDING_MODEL (deprecated, will be removed in Phase-8)
        - QWEN_RERANKER_MODEL → RERANKER_MODEL (deprecated, will be removed in Phase-8)
    """
    _ensure_loaded()
    import warnings

    provider = (env("INFERENCE_PROVIDER", "lmstudio") or "lmstudio").strip()
    retrieval_profile = (env("RETRIEVAL_PROFILE", "LEGACY") or "LEGACY").strip().upper()
    if retrieval_profile not in _PROFILE_DEFAULTS:
        retrieval_profile = "LEGACY"

    granite_models = {
        "embedding_model": env("GRANITE_EMBEDDING_MODEL"),
        "reranker_model": env("GRANITE_RERANKER_MODEL"),
        "local_agent_model": env("GRANITE_LOCAL_AGENT_MODEL"),
    }

    # Provider enable/disable flags
    ollama_enabled = env("OLLAMA_ENABLED", "true").lower() in ("1", "true", "yes")
    lm_studio_enabled = get_lm_studio_enabled()

    # Get base URL from existing openai_cfg() function
    cfg = openai_cfg()
    base_url = cfg.get("base_url", "http://127.0.0.1:9994/v1")
    ollama_base_url = env("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

    # Per-slot provider configuration (defaults to main provider)
    local_agent_provider = env("LOCAL_AGENT_PROVIDER") or provider
    embedding_provider = env("EMBEDDING_PROVIDER") or provider
    reranker_provider = env("RERANKER_PROVIDER") or provider
    theology_provider = env("THEOLOGY_PROVIDER") or "lmstudio"

    # Canonical vars
    legacy_defaults = _PROFILE_DEFAULTS["LEGACY"]
    granite_defaults = _PROFILE_DEFAULTS["GRANITE"]

    embedding = env("EMBEDDING_MODEL") or legacy_defaults["embedding_model"]
    theology = env("THEOLOGY_MODEL") or legacy_defaults["theology_model"]
    theology_lmstudio_base_url = env("THEOLOGY_LMSTUDIO_BASE_URL") or base_url
    theology_lmstudio_api_key = env("THEOLOGY_LMSTUDIO_API_KEY")
    local_agent = env("LOCAL_AGENT_MODEL") or legacy_defaults["local_agent_model"]
    math_model = env("MATH_MODEL")
    reranker = env("RERANKER_MODEL") or legacy_defaults["reranker_model"]
    reranker_strategy = env("RERANKER_STRATEGY", "embedding_only")

    # Planning lane (Codex CLI helper; Gemini CLI deprecated for local inference)
    planning_provider_raw = env("PLANNING_PROVIDER", "granite").strip().lower()
    planning_provider = planning_provider_raw if planning_provider_raw else "granite"
    planning_model = env("PLANNING_MODEL") or "granite-4.0-small"
    gemini_enabled = env("GEMINI_ENABLED", "false").lower() in (
        "1",
        "true",
        "yes",
    )  # Deprecated: disabled by default for local inference
    codex_enabled = env("CODEX_ENABLED", "false").lower() in ("1", "true", "yes")
    gemini_cli_path = env("GEMINI_CLI_PATH") or "gemini"
    codex_cli_path = env("CODEX_CLI_PATH") or "codex"

    # Vision lane (Qwen3-VL-4B for multimodal tasks)
    vision_provider = env("VISION_PROVIDER", "lmstudio").strip().lower()
    vision_model = env("VISION_MODEL", "qwen3-vl-4b")
    lmstudio_base_url = env("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
    ollama_base_url = env("OLLAMA_BASE_URL", "http://localhost:11434")

    # Phase-7F: Normalize model names for Ollama when provider is ollama
    if provider == "ollama":
        # Normalize embedding model name
        if embedding and "bge-m3" in embedding.lower() and ":" not in embedding:
            embedding = "bge-m3:latest"
        elif embedding and "text-embedding-bge-m3" in embedding.lower():
            embedding = "bge-m3:latest"

        # Normalize reranker model name
        if reranker and "bge-reranker" in reranker.lower() and ":" not in reranker:
            reranker = "bge-reranker-v2-m3:latest"
        elif reranker and "bge-reranker-v2-m3" in reranker.lower() and ":" not in reranker:
            reranker = "bge-reranker-v2-m3:latest"

    # Legacy fallbacks (with deprecation warnings)
    if not embedding:
        legacy_embed = env("LM_EMBED_MODEL")
        if legacy_embed:
            warnings.warn(
                "LM_EMBED_MODEL is deprecated, use EMBEDDING_MODEL instead. Support will be removed in Phase-8.",
                DeprecationWarning,
                stacklevel=2,
            )
            embedding = legacy_embed

    if not reranker:
        legacy_rerank = env("QWEN_RERANKER_MODEL")
        if legacy_rerank:
            warnings.warn(
                "QWEN_RERANKER_MODEL is deprecated, use RERANKER_MODEL instead. Support will be removed in Phase-8.",
                DeprecationWarning,
                stacklevel=2,
            )
            reranker = legacy_rerank

    return {
        "provider": provider,
        "ollama_enabled": ollama_enabled,
        "lm_studio_enabled": lm_studio_enabled,
        "base_url": base_url,
        "ollama_base_url": ollama_base_url,
        "local_agent_provider": local_agent_provider,
        "local_agent_model": local_agent,
        "embedding_provider": embedding_provider,
        "embedding_model": embedding,
        "reranker_provider": reranker_provider,
        "reranker_model": reranker,
        "reranker_strategy": reranker_strategy,
        "theology_provider": theology_provider,
        "theology_model": theology,
        "theology_lmstudio_base_url": theology_lmstudio_base_url,
        "theology_lmstudio_api_key": theology_lmstudio_api_key,
        "math_model": math_model,
        "retrieval_profile": retrieval_profile,
        "granite_embedding_model": granite_models["embedding_model"],
        "granite_reranker_model": granite_models["reranker_model"],
        "granite_local_agent_model": granite_models["local_agent_model"],
        "legacy_profile_defaults": legacy_defaults.copy(),
        "granite_profile_defaults": granite_defaults.copy(),
        "planning_provider": planning_provider,
        "planning_model": planning_model,
        "gemini_enabled": gemini_enabled,
        "codex_enabled": codex_enabled,
        "gemini_cli_path": gemini_cli_path,
        "codex_cli_path": codex_cli_path,
        "vision_provider": vision_provider,
        "vision_model": vision_model,
        "lmstudio_base_url": lmstudio_base_url,
    }


def get_embedding_model() -> str:
    """
    Phase-7B: Get embedding model ID with legacy fallback.

    Returns:
        Embedding model ID (default: "text-embedding-bge-m3")
    """
    cfg = get_lm_model_config()
    return cfg.get("embedding_model") or "text-embedding-bge-m3"


def get_theology_model() -> str:
    """
    Phase-7B: Get theology model ID.

    Returns:
        Theology model ID (default: "christian-bible-expert-v2.0-12b")
    """
    cfg = get_lm_model_config()
    return cfg.get("theology_model") or "christian-bible-expert-v2.0-12b"


def get_math_model() -> str:
    """
    Phase-7B: Get math verification model ID.

    Returns:
        Math model ID (default: "self-certainty-qwen3-1.7b-base-math")
    """
    cfg = get_lm_model_config()
    return cfg.get("math_model") or "self-certainty-qwen3-1.7b-base-math"


def get_reranker_model() -> str:
    """
    Phase-7B: Get reranker model ID with legacy fallback.

    Returns:
        Reranker model ID (default: "qwen-reranker")
    """
    cfg = get_lm_model_config()
    return cfg.get("reranker_model") or "qwen-reranker"


def get_retrieval_lane_models() -> dict[str, str | bool | None]:
    """
    Phase-7C: Determine retrieval lane models (embedding + reranker) with profile awareness.

    Returns:
        Dict containing:
        - profile: Active retrieval profile ("LEGACY" or "GRANITE")
        - embedding_model: Model ID to use for embeddings (profile aware)
        - reranker_model: Model ID to use for reranker (profile aware)
        - granite_active: bool flag indicating Granite lane is active
    """
    cfg = get_lm_model_config()
    profile = (cfg.get("retrieval_profile") or "LEGACY").upper()
    legacy_defaults = cfg.get("legacy_profile_defaults") or {}
    default_embedding = legacy_defaults.get("embedding_model", "text-embedding-bge-m3")
    default_reranker = legacy_defaults.get("reranker_model", "qwen.qwen3-reranker-0.6b")
    embedding = cfg.get("embedding_model") or default_embedding
    reranker = cfg.get("reranker_model") or default_reranker
    granite_active = False

    if profile == "GRANITE":
        granite_embedding = cfg.get("granite_embedding_model")
        granite_reranker = cfg.get("granite_reranker_model")
        missing: list[str] = []

        if granite_embedding:
            embedding = granite_embedding
        else:
            missing.append("embedding")

        if granite_reranker:
            reranker = granite_reranker
        else:
            missing.append("reranker")

        if missing:
            print(
                f"HINT: retrieval: GRANITE profile requested but missing {', '.join(missing)} model(s); "
                "falling back to LEGACY retrieval lane (BGE + Qwen)",
                flush=True,
            )
        else:
            granite_active = True
            print(
                f"HINT: retrieval: using GRANITE profile (embed={embedding}, rerank={reranker})",
                flush=True,
            )

    return {
        "profile": profile,
        "embedding_model": embedding,
        "reranker_model": reranker,
        "granite_active": granite_active,
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
