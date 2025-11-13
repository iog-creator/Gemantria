from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _export_script() -> Path:
    return _repo_root() / "scripts" / "db" / "control_agent_runs_7d_export.py"


def _export_path() -> Path:
    return _repo_root() / "share" / "atlas" / "control_plane" / "agent_runs_7d.json"


def _run_export() -> None:
    script = _export_script()
    assert script.exists(), "control_agent_runs_7d_export.py is missing"
    env = dict(os.environ)
    env["PYTHONPATH"] = str(_repo_root())
    subprocess.run(
        [sys.executable, str(script)],
        check=True,
        cwd=_repo_root(),
        env=env,
    )


def test_control_agent_runs_7d_export_shape_db_off_tolerant() -> None:
    """Export must succeed and produce a reasonable JSON shape even when DB is off.

    We only assert on the JSON shape so this passes in both DB-off and DB-on
    environments.
    """
    _run_export()
    path = _export_path()
    assert path.exists(), "agent_runs_7d.json was not created"

    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)

    assert data.get("schema") == "control"
    assert "generated_at" in data

    # Window metadata
    assert "window_days" in data
    assert data["window_days"] == 7
    assert "since" in data

    # Status fields
    assert "ok" in data
    assert isinstance(data["ok"], bool)

    assert "connection_ok" in data
    assert isinstance(data["connection_ok"], bool)

    # Payload lists
    assert "runs" in data
    assert isinstance(data["runs"], list)

    assert "sessions" in data
    assert isinstance(data["sessions"], list)

    # Error field should always exist (may be null/str depending on path)
    assert "error" in data
