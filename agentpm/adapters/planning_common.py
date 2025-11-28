from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class PlanningCliResult:
    """Standard return payload for planning CLI adapters."""

    ok: bool
    mode: str
    provider: str
    response: str | None = None
    reason: str | None = None
    stdout: str | None = None
    stderr: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Convert the result to a serializable dictionary."""
        return {
            "ok": self.ok,
            "mode": self.mode,
            "provider": self.provider,
            "response": self.response,
            "reason": self.reason,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


def compose_prompt(prompt: str, system: str | None = None) -> str:
    """Compose a single string that carries system + user content."""
    prompt = (prompt or "").strip()
    system = (system or "").strip()
    if system and prompt:
        return f"[system]\n{system}\n\n[prompt]\n{prompt}"
    if system:
        return f"[system]\n{system}"
    return prompt
