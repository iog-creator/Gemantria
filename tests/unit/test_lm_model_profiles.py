"""Unit tests for LM model profile resolution and retrieval lanes."""

from __future__ import annotations

import importlib
from typing import Iterable

import pytest


def _reset_env(monkeypatch: pytest.MonkeyPatch, keys: Iterable[str]) -> None:
    for key in keys:
        monkeypatch.delenv(key, raising=False)


@pytest.fixture(autouse=True)
def _clear_profile_env(monkeypatch: pytest.MonkeyPatch) -> None:
    keys = [
        "RETRIEVAL_PROFILE",
        "EMBEDDING_MODEL",
        "RERANKER_MODEL",
        "LOCAL_AGENT_MODEL",
        "THEOLOGY_MODEL",
        "GRANITE_EMBEDDING_MODEL",
        "GRANITE_RERANKER_MODEL",
        "GRANITE_LOCAL_AGENT_MODEL",
        "LM_EMBED_MODEL",
        "QWEN_RERANKER_MODEL",
    ]
    _reset_env(monkeypatch, keys)
    monkeypatch.setenv("INFERENCE_PROVIDER", "lmstudio")
    monkeypatch.setenv("DISABLE_DOTENV", "1")
    # Reload module to ensure defaults are consistent when running entire suite.
    import scripts.config.env as env_config

    importlib.reload(env_config)


def test_legacy_profile_default(monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts.config import env as env_config

    cfg = env_config.get_lm_model_config()
    assert cfg["retrieval_profile"] == "LEGACY"

    lane = env_config.get_retrieval_lane_models()
    assert lane["profile"] == "LEGACY"
    assert lane["embedding_model"] == "text-embedding-bge-m3"
    assert lane["reranker_model"] == "qwen.qwen3-reranker-0.6b"
    assert lane["granite_active"] is False


def test_granite_profile_uses_granite_models(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from scripts.config import env as env_config

    monkeypatch.setenv("RETRIEVAL_PROFILE", "GRANITE")
    monkeypatch.setenv("GRANITE_EMBEDDING_MODEL", "ibm-granite/custom-embed")
    monkeypatch.setenv("GRANITE_RERANKER_MODEL", "ibm-granite/custom-rerank")
    lane = env_config.get_retrieval_lane_models()
    captured = capsys.readouterr()

    assert lane["profile"] == "GRANITE"
    assert lane["embedding_model"] == "ibm-granite/custom-embed"
    assert lane["reranker_model"] == "ibm-granite/custom-rerank"
    assert lane["granite_active"] is True
    assert "using GRANITE profile" in captured.out


def test_granite_profile_falls_back_when_missing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from scripts.config import env as env_config

    monkeypatch.setenv("RETRIEVAL_PROFILE", "GRANITE")
    monkeypatch.setenv("EMBEDDING_MODEL", "text-embedding-bge-m3")
    monkeypatch.setenv("RERANKER_MODEL", "qwen.qwen3-reranker-0.6b")

    lane = env_config.get_retrieval_lane_models()
    captured = capsys.readouterr()

    assert lane["profile"] == "GRANITE"
    assert lane["granite_active"] is False
    assert lane["embedding_model"] == "text-embedding-bge-m3"
    assert "falling back to LEGACY" in captured.out


def test_explicit_legacy_profile_override(monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts.config import env as env_config

    monkeypatch.setenv("RETRIEVAL_PROFILE", "LEGACY")
    monkeypatch.setenv("EMBEDDING_MODEL", "custom-embed")
    monkeypatch.setenv("RERANKER_MODEL", "custom-rerank")

    lane = env_config.get_retrieval_lane_models()
    assert lane["profile"] == "LEGACY"
    assert lane["embedding_model"] == "custom-embed"
    assert lane["reranker_model"] == "custom-rerank"
