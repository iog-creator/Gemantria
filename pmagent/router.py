#!/usr/bin/env python3
"""
Router - LM routing for pmagent tools.

Routes tasks to appropriate models (Granite Tiny → expert models) using existing LM infrastructure.
"""

from __future__ import annotations


from scripts.config.env import get_lm_model_config
from pmagent.adapters.lm_studio import chat as lm_studio_chat
from pmagent.adapters.theology import chat as theology_chat


def route_task(
    prompt: str,
    task_type: str = "general",
    *,
    system: str | None = None,
    temperature: float = 0.0,
    max_tokens: int = 512,
) -> str:
    """Route a task to the appropriate model.

    Args:
        prompt: Task prompt text.
        task_type: Task type ("general", "theology", "math", "local_agent").
        system: Optional system prompt.
        temperature: Sampling temperature (default: 0.0 for determinism).
        max_tokens: Maximum tokens to generate (default: 512).

    Returns:
        Response text string.

    Raises:
        RuntimeError: If model not configured or provider unavailable.
    """
    cfg = get_lm_model_config()

    # Route based on task type
    if task_type == "theology":
        return theology_chat(prompt, system=system)
    elif task_type == "local_agent":
        # Use local agent model (e.g., Granite 4 tiny)
        model = cfg.get("local_agent_model")
        if not model:
            raise RuntimeError("No LOCAL_AGENT_MODEL configured")
        return lm_studio_chat(prompt, model_slot="local_agent", system=system)
    elif task_type == "math":
        # Use math model
        model = cfg.get("math_model")
        if not model:
            raise RuntimeError("No MATH_MODEL configured")
        return lm_studio_chat(prompt, model_slot="math", system=system)
    else:
        # Default: use local agent model
        model = cfg.get("local_agent_model")
        if not model:
            raise RuntimeError("No LOCAL_AGENT_MODEL configured")
        return lm_studio_chat(prompt, model_slot="local_agent", system=system)
