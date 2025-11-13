from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _guard_script() -> Path:
    return _repo_root() / "scripts" / "guards" / "guard_control_knowledge_mcp_webproof_backlinks.py"


def _webproof_path() -> Path:
    return _repo_root() / "docs" / "atlas" / "webproof" / "knowledge_mcp.html"


def _verdict_path() -> Path:
    return _repo_root() / "evidence" / "guard_control_knowledge_mcp_webproof_backlinks.json"


def _run_exports_and_guard() -> None:
    root = _repo_root()
    subprocess.run(["make", "control.mcp.catalog.export"], check=True, cwd=root)
    subprocess.run(["make", "control.capability.rules.export"], check=True, cwd=root)
    subprocess.run(["make", "control.agent_runs_7d.export"], check=True, cwd=root)
    subprocess.run(["make", "guard.control.knowledge.mcp.exports"], check=True, cwd=root)

    script = _guard_script()
    subprocess.run([sys.executable, str(script)], check=True, cwd=root)


def test_guard_control_knowledge_mcp_webproof_backlinks_shape() -> None:
    assert _webproof_path().exists(), "knowledge_mcp.html missing"
    _run_exports_and_guard()

    verdict_path = _verdict_path()
    assert verdict_path.exists(), "webproof backlinks verdict missing"

    data = json.loads(verdict_path.read_text(encoding="utf-8"))
    assert data["ok"] is True
    assert len(data["checks"]) == 5
    assert data["errors"] == []
