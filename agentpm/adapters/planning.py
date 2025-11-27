from __future__ import annotations

from typing import Any

from agentpm.adapters import gemini_cli, codex_cli
from agentpm.adapters.lm_studio import chat as lm_studio_chat_helper
from agentpm.adapters.planning_common import PlanningCliResult
from scripts.config.env import get_lm_model_config

# Nemotron system prompts and sampling parameters
NEMOTRON_REASONING_SYSTEM = (
    "You are Nemotron Nano 12B v2, a careful reasoning assistant. /think\n"
    "Think step by step inside <think>...</think>, then give a short final answer."
)

NEMOTRON_FAST_SYSTEM = (
    "You are Nemotron Nano 12B v2, answer concisely. /no_think\n"
    "Do not spend tokens on long reasoning unless strictly needed."
)


def _nemotron_reasoning_params() -> dict[str, Any]:
    """NVIDIA-recommended defaults for reasoning mode."""
    return {
        "temperature": 0.6,
        "top_p": 0.95,
        "max_tokens": 1024,
    }


def _nemotron_fast_params() -> dict[str, Any]:
    """Fast mode parameters for Nemotron."""
    return {
        "temperature": 0.0,  # greedy
        "top_p": 1.0,
        "max_tokens": 512,
    }


def run_planning_prompt(
    prompt: str,
    *,
    system: str | None = None,
    extra_env: dict[str, str] | None = None,
    extra_args: list[str] | None = None,
    timeout: float = 180.0,
) -> PlanningCliResult:
    """Route a planning prompt to the configured planning provider."""
    cfg = get_lm_model_config()
    planning_provider = (cfg.get("planning_provider") or "").strip().lower()
    planning_model = cfg.get("planning_model")

    if planning_provider == "gemini":
        # Deprecated: Gemini CLI disabled by default for local inference goals
        result = gemini_cli.run(
            prompt,
            system=system,
            model=planning_model,
            cli_path=cfg.get("gemini_cli_path") or "gemini",
            enabled=bool(cfg.get("gemini_enabled", False)),  # Default to False
            extra_env=extra_env,
            extra_args=extra_args,
            timeout=timeout,
        )
        if result.ok:
            return result
        # On failure fall back to local lane
    elif planning_provider == "codex":
        result = codex_cli.run(
            prompt,
            system=system,
            model=planning_model,
            cli_path=cfg.get("codex_cli_path") or "codex",
            enabled=bool(cfg.get("codex_enabled", False)),
            extra_env=extra_env,
            extra_args=extra_args,
            timeout=timeout,
        )
        if result.ok:
            return result
    elif planning_provider in ("ollama", "lmstudio"):
        # Route to Nemotron via Ollama/LM Studio adapter
        model_name = planning_model or "nvidia/nemotron-nano-12b-v2"
        _nemotron_reasoning_params()  # Load params for model config
        system_prompt = NEMOTRON_REASONING_SYSTEM

        # Determine if fast mode is needed (based on prompt characteristics)
        # Simple heuristic: short prompts or "simple" keywords → fast mode
        prompt_lower = prompt.lower()
        if any(keyword in prompt_lower for keyword in ["simple", "quick", "brief", "short"]):
            # Use fast mode parameters (though Ollama/LM Studio adapters may not use them)
            system_prompt = NEMOTRON_FAST_SYSTEM

        if planning_provider == "ollama":
            try:
                from agentpm.adapters.ollama import chat as ollama_chat

                # Ollama adapter doesn't support temperature/top_p/max_tokens in chat()
                # These are handled by the model's default settings
                response = ollama_chat(
                    prompt,
                    model=model_name,
                    system=system_prompt or system,
                )
            except ImportError:
                # Ollama adapter not available, fall through to fallback
                response = None
        else:  # lmstudio
            # Use LM Studio chat helper with Nemotron model
            # The chat() helper accepts prompt, model, system and returns string directly
            # Note: We pass model_slot=None to use explicit model name instead of slot routing
            response = lm_studio_chat_helper(
                prompt,
                model=model_name,
                model_slot=None,  # Use explicit model, not slot routing
                system=system_prompt or system,
            )

        if response:
            return PlanningCliResult(
                ok=True,
                mode="lm_on",
                provider=planning_provider,
                response=response,
            )

    # Fallback: local agent slot via existing LM adapters
    fallback_text = lm_studio_chat_helper(prompt, model_slot="local_agent", system=system)
    return PlanningCliResult(
        ok=True,
        mode="lm_on",
        provider=planning_provider or "local_agent",
        response=fallback_text,
    )


def summarize_result(result: PlanningCliResult) -> dict[str, Any]:
    """Return a dict summary suitable for pmagent CLI output."""
    base = result.as_dict()
    # Shorten stdout/stderr to keep CLI tidy
    if base.get("stdout"):
        base["stdout"] = _truncate(base["stdout"])
    if base.get("stderr"):
        base["stderr"] = _truncate(base["stderr"])
    return base


def _truncate(value: str, limit: int = 4000) -> str:
    """Truncate long values for CLI display."""
    if len(value) <= limit:
        return value
    return f"{value[:limit]}… (+{len(value) - limit} chars)"
