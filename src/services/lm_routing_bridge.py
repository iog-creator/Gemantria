#!/usr/bin/env python3
"""
LM Routing Bridge

Phase-3C P1b: Bridges batch chat_completion interface to new LM Studio adapter + routing.
Maintains backward compatibility with existing enrichment pipeline while adding
control-plane logging and health-aware routing.
"""

from __future__ import annotations

from types import SimpleNamespace

from pmagent.runtime.lm_logging import lm_studio_chat_with_logging
from pmagent.runtime.lm_routing import select_lm_backend
from src.infra.structured_logger import get_logger, log_json

LOG = get_logger("gemantria.lm_routing_bridge")


def chat_completion_with_routing(
    messages_batch: list[list[dict[str, str]]],
    model: str,
    temperature: float = 0.0,
    max_tokens: int = 8192,
) -> list[SimpleNamespace]:
    """
    Execute batched chat completions with LM Studio routing and control-plane logging.

    Phase-3C P1b: Uses new adapter pattern (lm_studio_chat_with_logging) when LM Studio
    is selected, falls back to legacy chat_completion for remote LLMs.

    Args:
        messages_batch: List of message lists, each containing conversation history
        model: Model name to use
        temperature: Sampling temperature (default 0.0 for deterministic)
        max_tokens: Maximum tokens to generate (default 8192)

    Returns:
        List of SimpleNamespace objects with 'text' attribute containing response text

    Raises:
        QwenUnavailableError: If models are not available and mocks not allowed
    """
    backend = select_lm_backend(prefer_local=True)

    if backend == "lm_studio":
        # Use new adapter with control-plane logging
        results = []
        for idx, messages in enumerate(messages_batch):
            log_json(
                LOG,
                20,
                "lm_routing_bridge_call",
                backend="lm_studio",
                model=model,
                batch_idx=idx,
                batch_size=len(messages_batch),
            )

            # Call LM Studio adapter with logging
            result = lm_studio_chat_with_logging(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=30.0,
            )

            if result.get("ok") and result.get("mode") == "lm_on":
                # Extract content from response
                response = result.get("response", {})
                if choices := response.get("choices"):
                    content = choices[0].get("message", {}).get("content", "")
                    results.append(SimpleNamespace(text=content))
                else:
                    # Fallback: empty response
                    log_json(
                        LOG,
                        30,
                        "lm_routing_bridge_no_content",
                        backend="lm_studio",
                        batch_idx=idx,
                    )
                    results.append(SimpleNamespace(text='{"insight": "", "confidence": 0.0}'))
            else:
                # LM Studio unavailable - fall back to legacy chat_completion
                log_json(
                    LOG,
                    30,
                    "lm_routing_bridge_fallback",
                    backend="lm_studio",
                    reason=result.get("reason", "unknown"),
                    batch_idx=idx,
                    fallback_to="legacy_chat_completion",
                )
                # Import legacy function for fallback
                from src.services.lmstudio_client import chat_completion

                legacy_result = chat_completion([messages], model=model, temperature=temperature)
                results.extend(legacy_result)

        return results

    # Remote backend (future: implement remote LLM calls)
    # For now, fall back to legacy chat_completion
    log_json(
        LOG,
        20,
        "lm_routing_bridge_call",
        backend="remote",
        model=model,
        batch_size=len(messages_batch),
        note="falling back to legacy chat_completion",
    )
    from src.services.lmstudio_client import chat_completion

    return chat_completion(messages_batch, model=model, temperature=temperature)
