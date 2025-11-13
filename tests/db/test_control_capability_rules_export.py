"""Test control-plane capability rules export."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _export_script() -> Path:
    return _repo_root() / "scripts" / "db" / "control_capability_rules_export.py"


def _export_path() -> Path:
    return _repo_root() / "share" / "atlas" / "control_plane" / "capability_rules.json"


def _run_export() -> None:
    script = _export_script()
    assert script.exists(), "control_capability_rules_export.py is missing"
    subprocess.run(
        [sys.executable, str(script)],
        check=True,
        cwd=_repo_root(),
    )


def test_control_capability_rules_export_shape_db_off_tolerant() -> None:
    """Export must succeed and produce a reasonable JSON shape even when DB is off.

    We assert only on the JSON shape, not on specific values, so this test
    passes in both DB-off and DB-on environments.
    """
    _run_export()
    path = _export_path()
    assert path.exists(), "capability_rules.json was not created"

    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)

    assert data.get("schema") == "control"
    assert "generated_at" in data

    assert "ok" in data
    assert isinstance(data["ok"], bool)

    assert "connection_ok" in data
    assert isinstance(data["connection_ok"], bool)

    assert "rules" in data
    assert isinstance(data["rules"], list)

    # Error field should always exist (may be null/str depending on path)
    assert "error" in data
