from __future__ import annotations

from typing import Any

from agentpm.adapters import gemini_cli, codex_cli
from agentpm.adapters.lm_studio import chat as lm_studio_chat
from agentpm.adapters.planning_common import PlanningCliResult
from scripts.config.env import get_lm_model_config


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
        result = gemini_cli.run(
            prompt,
            system=system,
            model=planning_model,
            cli_path=cfg.get("gemini_cli_path") or "gemini",
            enabled=bool(cfg.get("gemini_enabled", True)),
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

    # Fallback: local agent slot via existing LM adapters
    fallback_text = lm_studio_chat(prompt, model_slot="local_agent", system=system)
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
