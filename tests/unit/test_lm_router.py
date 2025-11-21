#!/usr/bin/env python3
"""
Unit tests for LM Router (Phase-7C)

Tests router decision logic, slot selection, and fallback behavior.
All tests are hermetic (no network calls, use dry_run mode).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402

from agentpm.lm.router import DryRunRouter, GraniteRouter, RouterDecision, RouterTask  # noqa: E402


@pytest.fixture
def mock_config():
    """Mock LM model configuration for testing."""
    return {
        "provider": "lmstudio",
        "ollama_enabled": True,
        "lm_studio_enabled": True,
        "local_agent_provider": "lmstudio",
        "local_agent_model": "granite4:tiny-h",
        "embedding_provider": "ollama",
        "embedding_model": "granite-embedding:278m",
        "reranker_provider": "ollama",
        "reranker_model": "granite4:tiny-h",
        "theology_provider": "lmstudio",
        "theology_model": "christian-bible-expert-v2.0-12b",
        "math_model": "self-certainty-qwen3-1.7b-base-math",
    }


def test_router_task_creation():
    """Test RouterTask dataclass creation."""
    task = RouterTask(kind="chat", domain="theology", needs_tools=False)
    assert task.kind == "chat"
    assert task.domain == "theology"
    assert task.needs_tools is False
    assert task.language is None
    assert task.max_tokens is None
    assert task.temperature is None


def test_router_decision_creation():
    """Test RouterDecision dataclass creation."""
    decision = RouterDecision(
        slot="theology",
        provider="lmstudio",
        model_name="christian-bible-expert-v2.0-12b",
        temperature=0.6,
    )
    assert decision.slot == "theology"
    assert decision.provider == "lmstudio"
    assert decision.model_name == "christian-bible-expert-v2.0-12b"
    assert decision.temperature == 0.6
    assert decision.extra_params == {}


def test_router_embedding_task(mock_config):
    """Test routing for embedding tasks."""
    router = DryRunRouter(config=mock_config)
    task = RouterTask(kind="embed", domain=None)
    decision = router.route_task(task)

    assert decision.slot == "embedding"
    assert decision.provider == "ollama"
    assert decision.model_name == "granite-embedding:278m"
    assert decision.temperature == 0.0  # Embedding tasks use 0.0


def test_router_rerank_task(mock_config):
    """Test routing for reranking tasks."""
    router = DryRunRouter(config=mock_config)
    task = RouterTask(kind="rerank", domain=None)
    decision = router.route_task(task)

    assert decision.slot == "reranker"
    assert decision.provider == "ollama"
    assert decision.model_name == "granite4:tiny-h"
    assert decision.temperature == 0.0  # Rerank tasks use 0.0


def test_router_math_task(mock_config):
    """Test routing for math verification tasks."""
    router = DryRunRouter(config=mock_config)
    task = RouterTask(kind="math_verification", domain="math")
    decision = router.route_task(task)

    assert decision.slot == "math"
    assert decision.model_name == "self-certainty-qwen3-1.7b-base-math"
    assert decision.temperature == 0.0  # Math tasks use 0.0


def test_router_math_task_fallback(mock_config):
    """Test math task falls back to local_agent if math model not configured."""
    config_no_math = mock_config.copy()
    config_no_math.pop("math_model")
    router = DryRunRouter(config=config_no_math)
    task = RouterTask(kind="math_verification", domain="math")
    decision = router.route_task(task)

    assert decision.slot == "local_agent"
    assert decision.model_name == "granite4:tiny-h"


def test_router_theology_task(mock_config):
    """Test routing for theology enrichment tasks."""
    router = DryRunRouter(config=mock_config)
    task = RouterTask(kind="theology_enrichment", domain="theology")
    decision = router.route_task(task)

    assert decision.slot == "theology"
    assert decision.provider == "lmstudio"
    assert decision.model_name == "christian-bible-expert-v2.0-12b"
    assert decision.temperature == 0.35  # Theology enrichment uses 0.35


def test_router_bible_domain(mock_config):
    """Test routing for Bible domain tasks."""
    router = DryRunRouter(config=mock_config)
    task = RouterTask(kind="chat", domain="bible")
    decision = router.route_task(task)

    assert decision.slot == "theology"
    assert decision.model_name == "christian-bible-expert-v2.0-12b"


def test_router_tool_calling_task(mock_config):
    """Test routing for tool-calling tasks."""
    router = DryRunRouter(config=mock_config)
    task = RouterTask(kind="chat", domain="general", needs_tools=True)
    decision = router.route_task(task)

    assert decision.slot == "local_agent"
    assert decision.model_name == "granite4:tiny-h"
    assert decision.extra_params.get("tool_choice") == "auto"
    assert decision.extra_params.get("response_format") == {"type": "json_object"}


def test_router_general_task(mock_config):
    """Test routing for general tasks (default to local_agent)."""
    router = DryRunRouter(config=mock_config)
    task = RouterTask(kind="chat", domain="general", needs_tools=False)
    decision = router.route_task(task)

    assert decision.slot == "local_agent"
    assert decision.model_name == "granite4:tiny-h"
    assert decision.temperature == 0.6  # General tasks use 0.6


def test_router_temperature_override(mock_config):
    """Test that task temperature preference is respected."""
    router = DryRunRouter(config=mock_config)
    task = RouterTask(kind="chat", domain="general", temperature=0.8)
    decision = router.route_task(task)

    assert decision.temperature == 0.8  # Task preference overrides default


def test_router_max_tokens(mock_config):
    """Test that max_tokens from task is included in extra_params."""
    router = DryRunRouter(config=mock_config)
    task = RouterTask(kind="chat", domain="general", max_tokens=1024)
    decision = router.route_task(task)

    assert decision.extra_params.get("max_tokens") == 1024


def test_router_provider_unavailable():
    """Test router raises error when provider is disabled."""
    config = {
        "provider": "lmstudio",
        "ollama_enabled": False,
        "lm_studio_enabled": False,
        "local_agent_provider": "lmstudio",
        "local_agent_model": "granite4:tiny-h",
    }
    router = GraniteRouter(config=config, dry_run=False)

    task = RouterTask(kind="chat", domain="general")
    with pytest.raises(RuntimeError, match="LM Studio is disabled"):
        router.route_task(task)


def test_router_no_model_configured():
    """Test router raises error when no model is configured."""
    config = {
        "provider": "lmstudio",
        "ollama_enabled": True,
        "lm_studio_enabled": True,
        "local_agent_provider": "lmstudio",
        # No local_agent_model configured
    }
    router = DryRunRouter(config=config)

    task = RouterTask(kind="chat", domain="general")
    with pytest.raises(RuntimeError, match="No model configured"):
        router.route_task(task)


def test_router_determinism(mock_config):
    """Test that same inputs produce same outputs (determinism)."""
    router = DryRunRouter(config=mock_config)
    task = RouterTask(kind="theology_enrichment", domain="theology")

    decision1 = router.route_task(task)
    decision2 = router.route_task(task)

    assert decision1.slot == decision2.slot
    assert decision1.provider == decision2.provider
    assert decision1.model_name == decision2.model_name
    assert decision1.temperature == decision2.temperature


def test_router_provider_fallback(mock_config):
    """Test that provider falls back to main provider if slot-specific not set."""
    config = mock_config.copy()
    config.pop("theology_provider")
    router = DryRunRouter(config=config)
    task = RouterTask(kind="theology_enrichment", domain="theology")
    decision = router.route_task(task)

    # Should use main provider (lmstudio) as fallback
    assert decision.provider == "lmstudio"


def test_router_slot_provider_override(mock_config):
    """Test that slot-specific provider overrides main provider."""
    config = mock_config.copy()
    config["provider"] = "lmstudio"
    config["embedding_provider"] = "ollama"
    router = DryRunRouter(config=config)
    task = RouterTask(kind="embed", domain=None)
    decision = router.route_task(task)

    # Should use slot-specific provider (ollama), not main provider
    assert decision.provider == "ollama"
