#!/usr/bin/env python3
"""Tests for reality check module (agentpm.reality.check)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from agentpm.reality.check import (
    check_control_plane_exports,
    check_db_and_control,
    check_env_and_dsn,
    check_lm_health_status,
    reality_check,
    run_eval_smoke,
)


@patch("agentpm.reality.check.get_rw_dsn")
@patch("agentpm.reality.check.get_ro_dsn")
@patch("agentpm.reality.check.get_bible_db_dsn")
def test_check_env_and_dsn_ok(mock_bible, mock_ro, mock_rw):
    """Test env/DSN check when all DSNs are available."""
    mock_rw.return_value = "postgresql://user:pass@localhost/db"
    mock_ro.return_value = "postgresql://user:pass@localhost/db_ro"
    mock_bible.return_value = "postgresql://user:pass@localhost/bible_db"

    result = check_env_and_dsn()

    assert result["ok"] is True
    assert result["dsn_ok"] is True
    assert result["details"]["dsns"]["rw"] is True
    assert result["details"]["dsns"]["ro"] is True
    assert result["details"]["dsns"]["bible"] is True


@patch("agentpm.reality.check.get_rw_dsn")
@patch("agentpm.reality.check.get_ro_dsn")
@patch("agentpm.reality.check.get_bible_db_dsn")
def test_check_env_and_dsn_no_rw(mock_bible, mock_ro, mock_rw):
    """Test env/DSN check when RW DSN is missing."""
    mock_rw.return_value = None
    mock_ro.return_value = "postgresql://user:pass@localhost/db_ro"
    mock_bible.return_value = "postgresql://user:pass@localhost/bible_db"

    result = check_env_and_dsn()

    assert result["ok"] is True  # Still OK, just no RW DSN
    assert result["dsn_ok"] is False
    assert result["details"]["dsns"]["rw"] is False


@patch("agentpm.reality.check.compute_control_summary")
def test_check_db_and_control_ok(mock_summary):
    """Test DB/control check when control summary is OK."""
    mock_summary.return_value = {
        "ok": True,
        "status": {"ok": True, "mode": "ready"},
        "tables": {"ok": True, "mode": "db_on"},
    }

    result = check_db_and_control()

    assert result["ok"] is True
    assert "control_schema" in result


@patch("agentpm.reality.check.compute_control_summary")
def test_check_db_and_control_fail(mock_summary):
    """Test DB/control check when control summary fails."""
    mock_summary.return_value = {
        "ok": False,
        "status": {"ok": False, "mode": "db_off"},
    }

    result = check_db_and_control()

    assert result["ok"] is False


@patch("agentpm.reality.check.compute_lm_status")
@patch("agentpm.reality.check.check_lm_health")
def test_check_lm_health_status_ok(mock_health, mock_status):
    """Test LM health check when LM is OK."""
    mock_health.return_value = {
        "ok": True,
        "mode": "lm_ready",
        "provider": "ollama",
    }
    mock_status.return_value = {
        "ok": True,
        "slots": [
            {
                "slot": "local_agent",
                "provider": "ollama",
                "model": "granite4:tiny-h",
                "service_status": "OK",
            },
        ],
    }

    result = check_lm_health_status()

    assert result["ok"] is True
    assert result["provider"] == "ollama"
    assert "slots" in result


@patch("agentpm.reality.check.compute_lm_status")
@patch("agentpm.reality.check.check_lm_health")
def test_check_lm_health_status_fail(mock_health, mock_status):
    """Test LM health check when LM is not OK."""
    mock_health.return_value = {
        "ok": False,
        "mode": "lm_off",
        "provider": "ollama",
        "details": {"errors": ["models_missing: Christian-Bible-Expert-v2.0-12B"]},
    }
    mock_status.return_value = {
        "ok": True,
        "slots": [],
    }

    result = check_lm_health_status()

    assert result["ok"] is False
    assert result["mode"] == "lm_off"


@patch("agentpm.reality.check.load_json_file")
def test_check_control_plane_exports_all_present(mock_load):
    """Test control plane exports check when all files are present."""
    mock_load.side_effect = [
        {"status": "offline"},  # lm_indicator
        {"compliance": "ok"},  # compliance_head
        {"docs": []},  # kb_docs_head
        {"catalog": []},  # mcp_catalog
    ]

    result = check_control_plane_exports()

    assert result["ok"] is True
    assert result["lm_indicator"] is not None
    assert result["compliance_head"] is not None
    assert result["kb_docs_head"] is not None
    assert result["mcp_catalog"] is not None


@patch("agentpm.reality.check.load_json_file")
def test_check_control_plane_exports_missing(mock_load):
    """Test control plane exports check when files are missing (hermetic OK)."""
    mock_load.return_value = None  # All files missing

    result = check_control_plane_exports()

    # In HINT mode, missing files are OK
    assert result["ok"] is True
    assert result["lm_indicator"] is None
    assert result["compliance_head"] is None


@patch("agentpm.reality.check.subprocess.run")
def test_run_eval_smoke_ok(mock_run):
    """Test eval smoke when all targets pass."""
    mock_run.return_value = MagicMock(returncode=0, stderr="")

    result = run_eval_smoke()

    assert result["ok"] is True
    assert len(result["targets"]) == 2
    assert len(result["messages"]) == 2
    assert mock_run.call_count == 2


@patch("agentpm.reality.check.subprocess.run")
def test_run_eval_smoke_fail(mock_run):
    """Test eval smoke when a target fails."""
    mock_run.return_value = MagicMock(returncode=1, stderr="Error message")

    result = run_eval_smoke()

    assert result["ok"] is False
    assert any("exit 1" in msg for msg in result["messages"])


@patch("agentpm.reality.check.run_eval_smoke")
@patch("agentpm.reality.check.check_control_plane_exports")
@patch("agentpm.reality.check.check_lm_health_status")
@patch("agentpm.reality.check.check_db_and_control")
@patch("agentpm.reality.check.check_env_and_dsn")
def test_reality_check_hint_mode_all_ok(mock_env, mock_db, mock_lm, mock_exports, mock_eval):
    """Test reality_check in HINT mode when all components are OK."""
    mock_env.return_value = {"ok": True, "dsn_ok": True}
    mock_db.return_value = {"ok": True}
    mock_lm.return_value = {"ok": True}
    mock_exports.return_value = {"ok": True}
    mock_eval.return_value = {"ok": True}

    result = reality_check(mode="HINT")

    assert result["overall_ok"] is True
    assert result["mode"] == "HINT"
    assert len(result["hints"]) == 0
    assert "command" in result
    assert "timestamp" in result


@patch("agentpm.reality.check.run_eval_smoke")
@patch("agentpm.reality.check.check_control_plane_exports")
@patch("agentpm.reality.check.check_lm_health_status")
@patch("agentpm.reality.check.check_db_and_control")
@patch("agentpm.reality.check.check_env_and_dsn")
def test_reality_check_hint_mode_lm_fail(mock_env, mock_db, mock_lm, mock_exports, mock_eval):
    """Test reality_check in HINT mode when LM fails (should still pass)."""
    mock_env.return_value = {"ok": True, "dsn_ok": True}
    mock_db.return_value = {"ok": True}
    mock_lm.return_value = {"ok": False, "mode": "lm_off"}
    mock_exports.return_value = {"ok": True}
    mock_eval.return_value = {"ok": True}

    result = reality_check(mode="HINT")

    # In HINT mode, LM failure should not cause overall failure
    assert result["overall_ok"] is True
    assert len(result["hints"]) > 0
    assert any("LM" in hint for hint in result["hints"])


@patch("agentpm.reality.check.run_eval_smoke")
@patch("agentpm.reality.check.check_control_plane_exports")
@patch("agentpm.reality.check.check_lm_health_status")
@patch("agentpm.reality.check.check_db_and_control")
@patch("agentpm.reality.check.check_env_and_dsn")
def test_reality_check_hint_mode_db_fail(mock_env, mock_db, mock_lm, mock_exports, mock_eval):
    """Test reality_check in HINT mode when DB fails (should fail hard)."""
    mock_env.return_value = {"ok": True, "dsn_ok": True}
    mock_db.return_value = {"ok": False}
    mock_lm.return_value = {"ok": True}
    mock_exports.return_value = {"ok": True}
    mock_eval.return_value = {"ok": True}

    result = reality_check(mode="HINT")

    # In HINT mode, DB failure should still cause overall failure
    assert result["overall_ok"] is False
    assert any("Critical infrastructure" in hint for hint in result["hints"])


@patch("agentpm.reality.check.run_eval_smoke")
@patch("agentpm.reality.check.check_control_plane_exports")
@patch("agentpm.reality.check.check_lm_health_status")
@patch("agentpm.reality.check.check_db_and_control")
@patch("agentpm.reality.check.check_env_and_dsn")
def test_reality_check_strict_mode_lm_fail(mock_env, mock_db, mock_lm, mock_exports, mock_eval):
    """Test reality_check in STRICT mode when LM fails (should fail hard)."""
    mock_env.return_value = {"ok": True, "dsn_ok": True}
    mock_db.return_value = {"ok": True}
    mock_lm.return_value = {"ok": False, "mode": "lm_off"}
    mock_exports.return_value = {"ok": True}
    mock_eval.return_value = {"ok": True}

    result = reality_check(mode="STRICT")

    # In STRICT mode, LM failure should cause overall failure
    assert result["overall_ok"] is False
    assert any("STRICT" in hint for hint in result["hints"])


@patch("agentpm.reality.check.run_eval_smoke")
@patch("agentpm.reality.check.check_control_plane_exports")
@patch("agentpm.reality.check.check_lm_health_status")
@patch("agentpm.reality.check.check_db_and_control")
@patch("agentpm.reality.check.check_env_and_dsn")
def test_reality_check_skip_dashboards(mock_env, mock_db, mock_lm, mock_exports, mock_eval):
    """Test reality_check with skip_dashboards=True."""
    mock_env.return_value = {"ok": True, "dsn_ok": True}
    mock_db.return_value = {"ok": True}
    mock_lm.return_value = {"ok": True}

    result = reality_check(mode="HINT", skip_dashboards=True)

    assert result["overall_ok"] is True
    assert result["exports"]["skipped"] is True
    assert result["eval_smoke"]["skipped"] is True
    # Exports and eval should not have been called
    mock_exports.assert_not_called()
    mock_eval.assert_not_called()
