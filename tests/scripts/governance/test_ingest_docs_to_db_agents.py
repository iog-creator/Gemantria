from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scripts.governance import ingest_docs_to_db as mod


def test_iter_agents_docs_discovers_root_and_module_agents(tmp_path: Path, monkeypatch: Any) -> None:  # noqa: ANN001
    # Create a fake repo structure with:
    # - Root AGENTS.md
    # - A module-level AGENTS.md
    # - A scripts_AGENTS.md file
    root_agents = tmp_path / "AGENTS.md"
    root_agents.write_text("# Root AGENTS\n", encoding="utf-8")

    module_dir = tmp_path / "agentpm"
    module_dir.mkdir()
    module_agents = module_dir / "AGENTS.md"
    module_agents.write_text("# AgentPM AGENTS\n", encoding="utf-8")

    scripts_agents = tmp_path / "scripts_AGENTS.md"
    scripts_agents.write_text("# Scripts AGENTS\n", encoding="utf-8")

    # Patch REPO_ROOT so discovery operates on our fake tree.
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)

    @dataclass
    class _DocTarget:
        logical_name: str
        role: str
        repo_path: Path
        is_ssot: bool

    # Ensure CANONICAL_DOCS doesn't accidentally include unrelated paths here.
    monkeypatch.setattr(
        mod,
        "CANONICAL_DOCS",
        [
            _DocTarget("AGENTS_ROOT", "agent_framework_index", root_agents, True),
        ],
    )

    results = list(mod.iter_agents_docs())
    logical_names = {d.logical_name for d in results}
    paths = {d.repo_path for d in results}

    assert root_agents in paths
    assert module_agents in paths
    assert scripts_agents in paths

    # Root AGENTS.md should be treated as the global framework index.
    assert "AGENTS_ROOT" in logical_names
    # The others should be namespaced by relative path.
    assert any(name.startswith("AGENTS::") for name in logical_names)
