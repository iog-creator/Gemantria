from __future__ import annotations

import importlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scripts.governance import ingest_docs_to_db as ingest_mod
from scripts.guards import guard_docs_db_ssot as mod


def test_guard_reports_db_off_when_engine_unavailable(tmp_path: Path, monkeypatch: Any, capsys: Any) -> None:  # noqa: ANN001
    # Build a minimal fake repo tree that the guard/ingest logic can discover.
    agents = tmp_path / "AGENTS.md"
    agents.write_text("# AGENTS\n", encoding="utf-8")

    master_plan = tmp_path / "MASTER_PLAN.md"
    master_plan.write_text("# MASTER PLAN\n", encoding="utf-8")

    rules_index = tmp_path / "RULES_INDEX.md"
    rules_index.write_text("# RULES INDEX\n", encoding="utf-8")

    ssot_root = tmp_path / "docs" / "SSOT"
    ssot_root.mkdir(parents=True)
    ssot_doc = ssot_root / "PHASE_PLAN.md"
    ssot_doc.write_text("# SSOT doc\n", encoding="utf-8")

    runbook_root = tmp_path / "docs" / "runbooks"
    runbook_root.mkdir(parents=True)
    runbook_doc = runbook_root / "GOV_RUNBOOK.md"
    runbook_doc.write_text("# Runbook doc\n", encoding="utf-8")

    # Patch ingest_mod.REPO_ROOT and CANONICAL_DOCS to use our temp tree.
    monkeypatch.setattr(ingest_mod, "REPO_ROOT", tmp_path)

    @dataclass
    class _DocTarget:
        logical_name: str
        role: str
        repo_path: Path
        is_ssot: bool

    canonical = [
        _DocTarget("AGENTS_ROOT", "ssot", agents, True),
        _DocTarget("MASTER_PLAN", "ssot", master_plan, True),
        _DocTarget("RULES_INDEX", "ssot", rules_index, True),
    ]
    monkeypatch.setattr(ingest_mod, "CANONICAL_DOCS", canonical)

    # Important: reload the guard module so that it picks up the patched ingest_mod.
    importlib.reload(mod)  # type: ignore[arg-type]

    # Patch get_control_engine inside the guard module to always fail, simulating DB-off.
    def _boom() -> None:
        raise RuntimeError("test: db unreachable")

    monkeypatch.setattr("scripts.guards.guard_docs_db_ssot.get_control_engine", _boom)

    # Run the guard and capture output.
    rc = mod.main()
    captured = capsys.readouterr()
    assert rc == 0

    data = json.loads(captured.out)
    assert data["ok"] is False
    assert data["mode"] == "db_off"
    assert "db" in data["reason"]
    assert data["details"]["total_local_docs"] >= 3
