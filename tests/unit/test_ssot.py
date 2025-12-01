from pathlib import Path

import pytest

from src.core import MasterPlan


def create_master_plan(tmp_path: Path) -> Path:
    content = """# MASTER_PLAN\n- PR-000 bootstrap\n- Coverage gate ≥98%\n- No writes to bible_db\n"""
    path = tmp_path / "MASTER_PLAN.md"
    path.write_text(content, encoding="utf-8")
    return path


def test_load_from_file(tmp_path: Path) -> None:
    plan_path = create_master_plan(tmp_path)

    plan = MasterPlan.load_from_file(plan_path)

    assert plan.bootstrap_summary == "PR-000 bootstrap"
    assert plan.coverage_gate == 98
    assert plan.prohibits_db_writes is True
    assert "Coverage ≥" in plan.summary()


def test_confirm_expectations(tmp_path: Path) -> None:
    plan_path = create_master_plan(tmp_path)
    plan = MasterPlan.load_from_file(plan_path)

    plan.confirm_expectations(measured_coverage=99, wrote_to_db=False)

    with pytest.raises(ValueError):
        plan.confirm_expectations(measured_coverage=90, wrote_to_db=False)

    with pytest.raises(ValueError):
        plan.confirm_expectations(measured_coverage=100, wrote_to_db=True)


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        MasterPlan.load_from_file(tmp_path / "missing.md")


def test_missing_coverage(tmp_path: Path) -> None:
    path = tmp_path / "plan.md"
    path.write_text("- PR-000 bootstrap", encoding="utf-8")

    with pytest.raises(ValueError):
        MasterPlan.load_from_file(path)


def test_empty_plan(tmp_path: Path) -> None:
    path = tmp_path / "plan.md"
    path.write_text("\n", encoding="utf-8")

    with pytest.raises(ValueError):
        MasterPlan.load_from_file(path)
