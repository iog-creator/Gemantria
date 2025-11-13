"""Test control-plane MCP catalog export."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _export_script() -> Path:
    return _repo_root() / "scripts" / "db" / "control_mcp_catalog_export.py"


def _export_path() -> Path:
    return _repo_root() / "share" / "atlas" / "control_plane" / "mcp_catalog.json"


def _run_export() -> None:
    script = _export_script()
    assert script.exists(), "control_mcp_catalog_export.py is missing"
    subprocess.run(
        [sys.executable, str(script)],
        check=True,
        cwd=_repo_root(),
    )


def test_control_mcp_catalog_export_shape_db_off_tolerant() -> None:
    """Export must succeed and produce a reasonable JSON shape even when DB is off.

    We don't assert on ok/connection_ok values because they may differ between
    local/dev and CI, but we do assert that the core shape is present.
    """
    _run_export()
    path = _export_path()
    assert path.exists(), "mcp_catalog.json was not created"

    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)

    assert data.get("schema") == "control"
    assert "generated_at" in data

    assert "ok" in data
    assert isinstance(data["ok"], bool)

    assert "connection_ok" in data
    assert isinstance(data["connection_ok"], bool)

    assert "tools" in data
    assert isinstance(data["tools"], list)

    # Error field should always exist (may be null/str depending on path)
    assert "error" in data
