"""PLAN-073 M4: STRICT Postgres checkpointer live path tests (E16-E20)."""
from __future__ import annotations

import json
import pathlib

import pytest

xfail_reason = "PLAN-073 M4 (STRICT Postgres checkpointer + real SELECT 1 + stronger Atlas chip) staged; implementation pending."

pytestmark = pytest.mark.xfail(reason=xfail_reason, strict=False)


def test_e16_checkpointer_driver_proof():
    """Checkpointer driver proof file exists."""
    p = pathlib.Path("share/mcp/pg_checkpointer.handshake.json")
    assert p.exists(), "pg_checkpointer.handshake.json missing"
    data = json.loads(p.read_text())
    assert data.get("driver") == "postgres"


def test_e17_db_select1_guard():
    """Real SELECT 1 guard receipt exists."""
    p = pathlib.Path("share/mcp/db_select1.ok.json")
    assert p.exists(), "db_select1.ok.json missing"
    data = json.loads(p.read_text())
    assert data.get("ok") is True
    # rowcount or value proof; minimal for now
    assert "rowcount" in data or "value" in data


def test_e18_atlas_chip_latency():
    """Atlas DB-proof chip includes latency field."""
    p = pathlib.Path("share/atlas/db_proof_chip.json")
    assert p.exists(), "db_proof_chip.json missing"
    data = json.loads(p.read_text())
    # Chip now includes latency or timing field
    assert any(k in data for k in ("latency_ms", "latency_us", "generated_at"))


def test_e19_dsn_host_hash_redacted():
    """DSN remains redacted and includes host hash."""
    p = pathlib.Path("share/atlas/db_proof_chip.json")
    data = json.loads(p.read_text())
    # DSN must remain redacted; host hash present (non-empty)
    assert "<REDACTED>" in (data.get("dsn") or "")
    hh = data.get("dsn_host_hash")
    assert isinstance(hh, str) and len(hh) >= 8


def test_e20_error_path_guard():
    """Error-path guard receipt exists."""
    p = pathlib.Path("share/mcp/db_error.guard.json")
    assert p.exists(), "db_error.guard.json missing"

