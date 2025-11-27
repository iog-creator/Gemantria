# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

"""
Model Router for Agentic Pipeline

Maps logical model names (theology, math, embedding, reranker, general)
to concrete LM Studio model IDs from .env configuration.

Provides type-safe model resolution with fallbacks and validation.
"""

import os
from enum import Enum
from typing import Dict, List
from dataclasses import dataclass

import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from infra.env_loader import ensure_env_loaded
from scripts.config.env import get_lm_model_config


class Modality(str, Enum):
    """Model modality types."""

    TEXT = "text"
    VISION_TEXT = "vision_text"


class ModelRole(str, Enum):
    """Model role types."""

    GENERAL = "general"
    REASONING = "reasoning"
    VISION = "vision"


@dataclass
class ModelConfig:
    """Configuration for a model with name and optional fallback."""

    name: str
    fallback: str | None = None


@dataclass
class ModelRegistryConfig:
    """Extended model configuration for registry with modality and role."""

    name: str  # provider-specific model id
    provider: str  # "granite" | "ollama" | "lmstudio"
    modality: Modality
    role: ModelRole
    slot: str  # "local_agent" | "planning" | "vision"
    max_context: int = 131072


def get_model_registry() -> Dict[str, ModelRegistryConfig]:
    """Get the centralized model registry.

    Returns:
        Dictionary mapping slot names to ModelRegistryConfig
    """
    settings = get_lm_model_config()

    # Determine local_agent model based on planning provider
    if settings.get("planning_provider") == "granite":
        local_agent_name = settings.get("local_agent_model", "granite-4.0-small")
    else:
        local_agent_name = settings.get("local_agent_model", "granite-4.0-small")

    return {
        "local_agent": ModelRegistryConfig(
            name=local_agent_name,
            provider="granite",
            modality=Modality.TEXT,
            role=ModelRole.GENERAL,
            slot="local_agent",
        ),
        "planning": ModelRegistryConfig(
            name=settings.get("planning_model", "granite-4.0-small"),
            provider=settings.get("planning_provider", "granite"),
            modality=Modality.TEXT,
            role=ModelRole.REASONING,
            slot="planning",
        ),
        "vision": ModelRegistryConfig(
            name=settings.get("vision_model", "qwen3-vl-4b"),
            provider=settings.get("vision_provider", "lmstudio"),
            modality=Modality.VISION_TEXT,
            role=ModelRole.VISION,
            slot="vision",
        ),
    }


# Global registry instance
_MODEL_REGISTRY: Dict[str, ModelRegistryConfig] | None = None


def MODEL_REGISTRY() -> Dict[str, ModelRegistryConfig]:
    """Get the global model registry (cached)."""
    global _MODEL_REGISTRY
    if _MODEL_REGISTRY is None:
        _MODEL_REGISTRY = get_model_registry()
    return _MODEL_REGISTRY


class ModelRouter:
    """
    Routes logical model names to concrete LM Studio model IDs.

    Handles model resolution with fallbacks and validation against
    the agentic pipeline routing configuration.
    """

    def __init__(self):
        ensure_env_loaded()

        # Core models from .env
        self._models = {
            "theology": ModelConfig(
                name=os.getenv("THEOLOGY_MODEL", "christian-bible-expert-v2.0-12b"),
                fallback=os.getenv("ANSWERER_MODEL_ALT", "Qwen2.5-14B-Instruct-GGUF"),
            ),
            "general": ModelConfig(
                name=os.getenv("ANSWERER_MODEL_ALT", "Qwen2.5-14B-Instruct-GGUF"),
                fallback=os.getenv("THEOLOGY_MODEL", "christian-bible-expert-v2.0-12b"),
            ),
            "math": ModelConfig(name=os.getenv("MATH_MODEL", "self-certainty-qwen3-1.7b-base-math")),
            "embedding": ModelConfig(name=os.getenv("EMBEDDING_MODEL", "text-embedding-bge-m3")),
            "reranker": ModelConfig(name=os.getenv("RERANKER_MODEL", "qwen.qwen3-reranker-0.6b")),
        }

        # Agent-to-model routing (matches AGENTS.md routing table)
        self._routing = {
            "ingestion": None,
            "discovery": "theology",
            "enrichment": "theology",
            "graph_build": None,
            "rerank": ["embedding", "reranker"],  # Dual model for rerank
            "analytics": None,
            "guard": None,
            "release": None,
            "triage": "general",
            "math": "math",
            "adr": "general",
        }

    def get_model(self, logical_name: str) -> str | None:
        """
        Get concrete model name for a logical model identifier.

        Args:
            logical_name: Logical name (theology, math, embedding, reranker, general)

        Returns:
            Concrete model ID or None if no model needed
        """
        if logical_name not in self._models:
            raise ValueError(f"Unknown logical model name: {logical_name}")

        config = self._models[logical_name]
        return config.name

    def get_model_with_fallback(self, logical_name: str) -> str:
        """
        Get concrete model name with fallback if primary unavailable.

        Args:
            logical_name: Logical name (theology, math, embedding, reranker, general)

        Returns:
            Concrete model ID (primary or fallback)

        Raises:
            ValueError: If no model available (primary or fallback)
        """
        config = self._models.get(logical_name)
        if not config:
            raise ValueError(f"Unknown logical model name: {logical_name}")

        # Try primary first, then fallback
        if config.name:
            return config.name
        elif config.fallback:
            return config.fallback
        else:
            raise ValueError(f"No model available for {logical_name} (no primary or fallback)")

    def get_agent_model(self, agent_name: str) -> str | List[str] | None:
        """
        Get model(s) for a specific agent.

        Args:
            agent_name: Agent name from routing table

        Returns:
            Single model name, list of model names, or None for code-only agents
        """
        logical_name = self._routing.get(agent_name)
        if logical_name is None:
            return None
        elif isinstance(logical_name, list):
            return [self.get_model(name) for name in logical_name]
        else:
            return self.get_model(logical_name)

    def get_agent_models_dict(self) -> Dict[str, str | List[str] | None]:
        """
        Get all agent-to-model mappings as a dictionary.

        Returns:
            Dict mapping agent names to model names/None
        """
        return {agent: self.get_agent_model(agent) for agent in self._routing.keys()}

    def validate_routing(self) -> List[str]:
        """
        Validate that all routed models exist and are properly configured.

        Returns:
            List of validation errors (empty if all valid)
        """
        errors = []

        for agent, logical_name in self._routing.items():
            if logical_name is None:
                continue  # Code-only agent, no model needed
            elif isinstance(logical_name, list):
                for name in logical_name:
                    if name not in self._models:
                        errors.append(f"Agent '{agent}' references unknown model '{name}'")
            elif logical_name not in self._models:
                errors.append(f"Agent '{agent}' references unknown model '{logical_name}'")

        return errors

    def get_provider(self) -> str:
        """Get the inference provider (currently always lmstudio)."""
        return os.getenv("INFERENCE_PROVIDER", "lmstudio")

    def is_live_enforced(self) -> bool:
        """Check if ENFORCE_QWEN_LIVE=1 (fail-closed mode)."""
        return os.getenv("ENFORCE_QWEN_LIVE", "0") == "1"


# Global router instance
_router = None


def get_router() -> ModelRouter:
    """Get the global model router instance."""
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router


def get_model_for_agent(agent_name: str) -> str | List[str] | None:
    """
    Convenience function to get model(s) for an agent.

    Args:
        agent_name: Agent name (discovery, enrichment, rerank, etc.)

    Returns:
        Model name(s) or None for code-only agents
    """
    return get_router().get_agent_model(agent_name)


def validate_model_routing() -> List[str]:
    """
    Validate model routing configuration.

    Returns:
        List of validation errors (empty if valid)
    """
    return get_router().validate_routing()
