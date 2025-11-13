from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _guard_script() -> Path:
    return _repo_root() / "scripts" / "guards" / "guard_control_knowledge_mcp_exports.py"


def _verdict_path() -> Path:
    return _repo_root() / "evidence" / "guard_control_knowledge_mcp_exports.json"


def _run_exports() -> None:
    """Ensure the three Knowledge-MCP exports exist before running the guard."""
    root = _repo_root()
    subprocess.run(
        ["make", "control.mcp.catalog.export"],
        check=True,
        cwd=root,
    )
    subprocess.run(
        ["make", "control.capability.rules.export"],
        check=True,
        cwd=root,
    )
    subprocess.run(
        ["make", "control.agent_runs_7d.export"],
        check=True,
        cwd=root,
    )


def _run_guard() -> None:
    script = _guard_script()
    assert script.exists(), "guard_control_knowledge_mcp_exports.py is missing"
    subprocess.run(
        [sys.executable, str(script)],
        check=True,
        cwd=_repo_root(),
    )


def test_guard_control_knowledge_mcp_exports_shape() -> None:
    """Guard must produce a verdict JSON and consider shape-only invariants.

    This test is DB-off tolerant: exports may have ok/connection_ok=false, but
    as long as their JSON shape is correct, the guard verdict.ok should be True.
    """
    _run_exports()
    _run_guard()
    path = _verdict_path()
    assert path.exists(), "guard verdict JSON was not created"

    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)

    assert "ok" in data
    assert isinstance(data["ok"], bool)
    assert data["ok"] is True

    assert "files" in data
    assert isinstance(data["files"], list)
    assert len(data["files"]) == 3

    assert "errors" in data
    assert isinstance(data["errors"], list)
    assert data["errors"] == []
