from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scripts.governance import ingest_docs_to_db as mod


class DummyConn:
    def execute(self, *_args: Any, **_kwargs: Any) -> None:
        # Dry-run mode should never call execute; keep this as a safety net.
        return None


class DummyEngine:
    def begin(self) -> Any:
        class _Ctx:
            def __enter__(self_inner: Any) -> DummyConn:  # noqa: ANN001
                return DummyConn()

            def __exit__(self_inner: Any, *_exc: Any) -> None:  # noqa: ANN001
                return None

        return _Ctx()  # type: ignore[return-value]


def test_ingest_docs_dry_run_discovers_docs_and_returns_zero(
    tmp_path: Path, monkeypatch: Any
) -> None:  # noqa: ANN001
    # Prepare a tiny fake repo structure rooted at tmp_path.
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

    # Patch REPO_ROOT so the module sees our temp tree as the repo root.
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)

    # Patch CANONICAL_DOCS to rebuild the list using the new REPO_ROOT.
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
    monkeypatch.setattr(mod, "CANONICAL_DOCS", canonical)

    # Patch get_control_engine to avoid touching a real DB.
    def _fake_get_control_engine() -> DummyEngine:
        return DummyEngine()

    monkeypatch.setattr(
        "scripts.governance.ingest_docs_to_db.get_control_engine", _fake_get_control_engine
    )

    # Run in dry-run mode; this should use our fake docs and return 0.
    rc = mod.main(["--dry-run"])
    assert rc == 0
