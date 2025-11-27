#!/usr/bin/env python3
"""
LM Router Module (Phase-7C)

Centralized task classification and model slot selection for language model operations.
Maps task characteristics to appropriate model slots and providers based on the Granite 4.0
+ BGE-M3 + Granite Reranker stack.

See docs/SSOT/LM_ROUTER_CONTRACT.md for the full contract specification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from scripts.config.env import get_lm_model_config
from src.services.model_router import MODEL_REGISTRY, ModelRegistryConfig


@dataclass
class RouterTask:
    """Input structure describing a task that needs an LM operation.

    Attributes:
        kind: Task type (e.g., "chat", "embed", "rerank", "math_verification", "theology_enrichment", "vision")
        domain: Domain hint (e.g., "theology", "math", "general", "bible", "greek", "hebrew", "planning")
        language: Language hint (e.g., "hebrew", "greek", "english")
        needs_tools: Whether task requires tool-calling capabilities
        max_tokens: Maximum tokens for response (optional)
        temperature: Temperature preference (optional, router may override)
        has_images: Whether task contains images (for vision routing)
        modality: Task modality ("text" or "vision_text")
    """

    kind: str
    domain: str | None = None
    language: str | None = None
    needs_tools: bool = False
    max_tokens: int | None = None
    temperature: float | None = None
    has_images: bool = False
    modality: str | None = None


@dataclass
class RouterDecision:
    """Output structure describing the chosen model and configuration.

    Attributes:
        slot: Model slot ("theology", "math", "local_agent", "embedding", "reranker", "planning", "vision")
        provider: Provider ("ollama" or "lmstudio")
        model_name: Concrete model ID (e.g., "granite4:tiny-h", "christian-bible-expert-v2.0-12b")
        temperature: Recommended temperature (defaults from Prompting Guide)
        extra_params: Additional parameters (e.g., tool_choice, response_format)
    """

    slot: str
    provider: str
    model_name: str
    temperature: float = 0.6
    extra_params: dict[str, Any] = field(default_factory=dict)


@dataclass
class RouterResult:
    """Extended router result with slot and model config.

    Attributes:
        slot: Model slot name
        model: ModelRegistryConfig with full model metadata
    """

    slot: str
    model: ModelRegistryConfig


class GraniteRouter:
    """Router for task-to-model-slot mapping based on rule-based classification.

    Uses rule-based mapping (fast path) driven by RouterTask.kind and RouterTask.domain.
    Future extension: Option B - use Granite Tiny-H as classifier for dynamic routing.
    """

    def __init__(self, config: dict[str, Any] | None = None, dry_run: bool = False):
        """Initialize router with configuration.

        Args:
            config: Model configuration dict (defaults to get_lm_model_config())
            dry_run: If True, return decisions without checking provider availability (for tests)
        """
        self.config = config or get_lm_model_config()
        self.dry_run = dry_run

    def route_task(self, task: RouterTask) -> RouterDecision:
        """Route a task to the appropriate model slot and provider.

        Args:
            task: RouterTask describing the operation

        Returns:
            RouterDecision with slot, provider, model, and parameters

        Raises:
            RuntimeError: If no suitable model is configured or provider is unavailable
        """
        # Determine slot based on task kind and domain
        slot = self._determine_slot(task)

        # Get provider for this slot
        provider = self._get_provider_for_slot(slot)

        # Check provider availability (unless dry_run)
        if not self.dry_run:
            self._check_provider_available(provider)

        # Get model name for this slot
        model_name = self._get_model_for_slot(slot)
        if not model_name:
            # Fallback to local_agent if slot model not configured
            if slot != "local_agent":
                slot = "local_agent"
                provider = self._get_provider_for_slot(slot)
                model_name = self._get_model_for_slot(slot)
            if not model_name:
                raise RuntimeError(
                    f"No model configured for slot '{slot}' and no fallback available. "
                    f"Please configure {slot.upper()}_MODEL or LOCAL_AGENT_MODEL."
                )

        # Determine temperature (use task preference or default for slot)
        temperature = task.temperature if task.temperature is not None else self._get_default_temperature(slot, task)

        # Build extra_params based on slot and task requirements
        extra_params = self._build_extra_params(slot, task)

        return RouterDecision(
            slot=slot,
            provider=provider,
            model_name=model_name,
            temperature=temperature,
            extra_params=extra_params,
        )

    def route_task_with_config(self, task: RouterTask) -> RouterResult:
        """Route a task and return RouterResult with model config.

        Args:
            task: RouterTask describing the operation

        Returns:
            RouterResult with slot and ModelRegistryConfig

        Raises:
            RuntimeError: If no suitable model is configured or provider is unavailable
        """
        decision = self.route_task(task)
        registry = MODEL_REGISTRY()
        model_cfg = registry.get(decision.slot)
        if not model_cfg:
            raise RuntimeError(f"No model config found for slot '{decision.slot}' in registry")
        return RouterResult(slot=decision.slot, model=model_cfg)

    def _detect_vision_task(self, task: RouterTask) -> bool:
        """Detect if task requires vision capabilities.

        Detection logic:
        - Explicit: kind == "vision" or modality == "vision_text"
        - Implicit: has_images == True or vision-related keywords in prompt/description
        - Browser verification tasks
        """
        # Explicit vision task
        if task.kind == "vision" or task.modality == "vision_text":
            return True

        # Implicit detection: check for images
        if task.has_images:
            return True

        # Note: Keyword detection would require access to prompt text,
        # which is not available in RouterTask. This can be handled by
        # the caller setting has_images=True or kind="vision" when appropriate.

        return False

    def _determine_slot(self, task: RouterTask) -> str:
        """Determine model slot based on task characteristics.

        Slot selection rules:
        - kind == "embed" → "embedding"
        - kind == "rerank" → "reranker"
        - kind == "math_verification" or domain == "math" → "math" (if configured) or "local_agent"
        - kind == "theology_enrichment" or domain in ("theology", "bible") → "theology"
        - Vision tasks (detected via _detect_vision_task) → "vision" (if configured) or "local_agent"
        - kind == "planning" or domain == "planning" → "planning" (if configured) or "local_agent"
        - needs_tools == True → "local_agent"
        - Default → "local_agent"
        """
        # Embedding tasks
        if task.kind == "embed":
            return "embedding"

        # Reranking tasks
        if task.kind == "rerank":
            return "reranker"

        # Math tasks
        if task.kind == "math_verification" or task.domain == "math":
            # Check if math model is configured, otherwise fallback to local_agent
            if self._get_model_for_slot("math"):
                return "math"
            return "local_agent"

        # Theology/Bible tasks
        if task.kind == "theology_enrichment" or task.domain in ("theology", "bible"):
            return "theology"

        # Vision lane (Qwen3-VL-4B for multimodal tasks)
        if self._detect_vision_task(task):
            # Check if vision model is configured (Qwen3-VL-4B)
            if self._get_model_for_slot("vision"):
                return "vision"
            # Fallback to local_agent (Granite) if no vision model
            return "local_agent"

        # Planning lane (Nemotron for reasoning, Granite for default)
        if task.kind == "planning" or task.domain == "planning":
            # Check if planning model is configured (Nemotron)
            if self._get_model_for_slot("planning"):
                return "planning"
            # Fallback to local_agent (Granite)
            return "local_agent"

        # Tool-calling tasks
        if task.needs_tools:
            return "local_agent"

        # Default: general/local_agent
        return "local_agent"

    def _get_provider_for_slot(self, slot: str) -> str:
        """Get provider for a given slot.

        Provider is determined by per-slot environment variables:
        - THEOLOGY_PROVIDER → theology slot
        - LOCAL_AGENT_PROVIDER → local_agent slot
        - EMBEDDING_PROVIDER → embedding slot
        - RERANKER_PROVIDER → reranker slot
        - PLANNING_PROVIDER → planning slot
        - VISION_PROVIDER → vision slot
        - Falls back to INFERENCE_PROVIDER if slot-specific provider not set
        """
        if slot == "planning":
            provider = self.config.get("planning_provider") or self.config.get("provider", "lmstudio")
            provider = str(provider or "").strip()
            return provider or "lmstudio"
        if slot == "vision":
            provider = self.config.get("vision_provider") or self.config.get("provider", "lmstudio")
            provider = str(provider or "").strip()
            return provider or "lmstudio"
        provider_key = f"{slot}_provider"
        provider = self.config.get(provider_key) or self.config.get("provider", "lmstudio")
        return str(provider).strip()

    def _get_model_for_slot(self, slot: str) -> str | None:
        """Get model name for a given slot.

        Model is determined by per-slot environment variables:
        - THEOLOGY_MODEL → theology slot
        - LOCAL_AGENT_MODEL → local_agent slot
        - MATH_MODEL → math slot
        - EMBEDDING_MODEL → embedding slot
        - RERANKER_MODEL → reranker slot
        - PLANNING_MODEL → planning slot
        - VISION_MODEL → vision slot
        """
        if slot == "planning":
            model = self.config.get("planning_model") or self.config.get("local_agent_model")
            return str(model).strip() if model else None
        if slot == "vision":
            model = self.config.get("vision_model")
            return str(model).strip() if model else None
        model_key = f"{slot}_model"
        model = self.config.get(model_key)
        return str(model).strip() if model else None

    def _check_provider_available(self, provider: str) -> None:
        """Check if provider is enabled and available.

        Raises:
            RuntimeError: If provider is disabled or unavailable
        """
        provider = provider.strip()
        if provider == "ollama":
            if not self.config.get("ollama_enabled", True):
                raise RuntimeError("Ollama is disabled (OLLAMA_ENABLED=false)")
        elif provider == "lmstudio":
            if not self.config.get("lm_studio_enabled", True):
                raise RuntimeError("LM Studio is disabled (LM_STUDIO_ENABLED=false)")
        elif provider == "gemini":
            if not self.config.get("gemini_enabled", False):  # Default to False (deprecated)
                raise RuntimeError("Gemini CLI is disabled (GEMINI_ENABLED=false)")
        elif provider == "codex":
            if not self.config.get("codex_enabled", False):
                raise RuntimeError("Codex CLI is disabled (CODEX_ENABLED=false)")
        # Other providers: assume available (future extension)

    def _get_default_temperature(self, slot: str, task: RouterTask) -> float:
        """Get default temperature for a slot based on Prompting Guide recommendations.

        Temperature defaults (from Prompting Guide):
        - Theology tasks: 0.35 (enrichment) or 0.6 (reasoning)
        - Math tasks: 0.0 (deterministic verification)
        - General/Agent tasks: 0.6 (reasoning, default from Prompting Guide)
        - Embedding/Rerank: N/A (not applicable, but return 0.0 as placeholder)
        """
        if slot == "theology":
            # Enrichment vs reasoning: use 0.35 for enrichment, 0.6 for general
            if task.kind == "theology_enrichment":
                return 0.35
            return 0.6
        if slot == "math":
            return 0.0  # Deterministic verification
        if slot == "planning":
            return 0.2
        if slot == "vision":
            return 0.7  # Vision tasks benefit from slightly higher temperature
        if slot in ("embedding", "reranker"):
            return 0.0  # Not applicable, but return placeholder
        # Default: general/agent tasks
        return 0.6

    def _build_extra_params(self, slot: str, task: RouterTask) -> dict[str, Any]:
        """Build extra parameters based on slot and task requirements.

        Returns:
            Dictionary of extra parameters (e.g., tool_choice, response_format)
        """
        params: dict[str, Any] = {}

        # Tool-calling: Granite 4.0 supports parallel tools
        if task.needs_tools and slot == "local_agent":
            params["tool_choice"] = "auto"
            # Granite 4.0 can force JSON response for tool calls
            params["response_format"] = {"type": "json_object"}

        # Max tokens from task
        if task.max_tokens is not None:
            params["max_tokens"] = task.max_tokens

        if slot == "planning":
            params["planning_provider"] = self.config.get("planning_provider")
            params["planning_model"] = self.config.get("planning_model")

        return params


def route_task(task: RouterTask, config: dict[str, Any] | None = None, dry_run: bool = False) -> RouterDecision:
    """Convenience function to route a task.

    Args:
        task: RouterTask describing the operation
        config: Model configuration dict (defaults to get_lm_model_config())
        dry_run: If True, return decisions without checking provider availability

    Returns:
        RouterDecision with slot, provider, model, and parameters

    Raises:
        RuntimeError: If no suitable model is configured or provider is unavailable
    """
    router = GraniteRouter(config=config, dry_run=dry_run)
    return router.route_task(task)


class DryRunRouter(GraniteRouter):
    """Router that returns static decisions without checking provider availability.

    Useful for tests and hermetic CI environments.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize dry-run router."""
        super().__init__(config=config, dry_run=True)
