#!/usr/bin/env python3
"""
LM Studio Helper Functions

Phase-6: Simple helper functions that use guarded_lm_call() for text generation.
These can be used by downstream apps (StoryMaker, BibleScholar) or internal features.
"""

from __future__ import annotations

from typing import Any

from agentpm.runtime.lm_logging import guarded_lm_call


def generate_text(
    prompt: str,
    *,
    max_tokens: int = 256,
    temperature: float = 0.7,
    system_prompt: str | None = None,
    model_slot: str | None = None,
) -> dict[str, Any]:
    """
    Phase-6: Simple text generation using guarded LM Studio calls.

    This is a small, clearly-scoped feature that demonstrates LM Studio enablement.
    When LM_STUDIO_ENABLED=true, it uses LM Studio with control-plane logging.
    When disabled, it returns a fallback response.

    Args:
        prompt: User prompt text
        max_tokens: Maximum tokens to generate (default: 256)
        temperature: Sampling temperature (default: 0.7)
        system_prompt: Optional system prompt

    Returns:
        Dictionary with:
        - ok: bool (True if generation succeeded)
        - mode: "lm_on" | "lm_off" | "fallback"
        - text: str | None (generated text if ok)
        - call_site: str (identifier for this call)
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    def fallback_fn(msgs: list[dict[str, str]], kwargs: dict[str, Any]) -> dict[str, Any]:
        """Simple fallback that returns empty response."""
        return {
            "ok": False,
            "response": None,
        }

    result = guarded_lm_call(
        call_site="lm_helpers.generate_text",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        fallback_fn=fallback_fn,
        model_slot=model_slot,
    )

    # Extract text from response
    text = None
    if result.get("ok") and result.get("response"):
        response = result["response"]
        if choices := response.get("choices"):
            text = choices[0].get("message", {}).get("content", "")

    return {
        "ok": result.get("ok", False),
        "mode": result.get("mode", "lm_off"),
        "text": text,
        "call_site": result.get("call_site", "lm_helpers.generate_text"),
    }
