from __future__ import annotations

import os
import shutil
import subprocess
from typing import Mapping, Sequence

from agentpm.adapters.planning_common import PlanningCliResult, compose_prompt

DEFAULT_CODEX_MODEL = "gpt-5-codex"


def run(
    prompt: str,
    *,
    system: str | None = None,
    model: str | None = None,
    cli_path: str = "codex",
    enabled: bool = False,
    timeout: float = 180.0,
    extra_env: Mapping[str, str] | None = None,
    extra_args: Sequence[str] | None = None,
) -> PlanningCliResult:
    """Execute a prompt via the Codex CLI (non-interactive exec mode)."""
    provider = "codex"
    clean_prompt = (prompt or "").strip()
    if not clean_prompt:
        return PlanningCliResult(
            ok=False,
            mode="lm_off",
            provider=provider,
            reason="empty_prompt",
        )
    if not enabled:
        return PlanningCliResult(
            ok=False,
            mode="lm_off",
            provider=provider,
            reason="codex_disabled",
        )
    if not _command_available(cli_path):
        return PlanningCliResult(
            ok=False,
            mode="lm_off",
            provider=provider,
            reason=f"cli_not_found:{cli_path}",
        )

    cmd: list[str] = [cli_path, "exec"]
    model_id = (model or DEFAULT_CODEX_MODEL).strip()
    if model_id:
        cmd.extend(["--model", model_id])
    if extra_args:
        cmd.extend(extra_args)

    payload = compose_prompt(clean_prompt, system)
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)

    try:
        completed = subprocess.run(
            [*cmd, payload],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            check=False,
        )
    except FileNotFoundError:
        return PlanningCliResult(
            ok=False,
            mode="lm_off",
            provider=provider,
            reason=f"cli_not_found:{cli_path}",
        )
    except subprocess.TimeoutExpired:
        return PlanningCliResult(
            ok=False,
            mode="timeout",
            provider=provider,
            reason="cli_timeout",
        )

    stdout = completed.stdout.strip()
    if completed.returncode != 0:
        reason = completed.stderr.strip() or stdout or f"exit_code_{completed.returncode}"
        return PlanningCliResult(
            ok=False,
            mode="cli_error",
            provider=provider,
            reason=reason,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    if not stdout:
        return PlanningCliResult(
            ok=False,
            mode="cli_error",
            provider=provider,
            reason="empty_response",
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    return PlanningCliResult(
        ok=True,
        mode="lm_on",
        provider=provider,
        response=stdout,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def _command_available(binary: str) -> bool:
    """Return True if the binary can be resolved."""
    if os.path.isabs(binary):
        return os.path.exists(binary) and os.access(binary, os.X_OK)
    return shutil.which(binary) is not None
