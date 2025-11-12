"""PLAN-073 M2: STRICT posture tests (E06-E10)."""

from __future__ import annotations

import json
import os
import pathlib

import pytest

xfail_reason = "PLAN-073 M2 (STRICT posture + Atlas DB-proof chip) staged; implementation pending."

pytestmark = pytest.mark.xfail(reason=xfail_reason, strict=False)


def test_e06_checkpointer_postgres_enabled():
    """STRICT posture requires CHECKPOINTER=postgres (env/runner-visible)."""
    assert os.environ.get("CHECKPOINTER", "") == "postgres"


def test_e07_dsn_mismatch_guard():
    """Guard should detect mismatch between env DSN and Makefile echo (simulated evidence file)."""
    p = pathlib.Path("share/mcp/dsn_mismatch.guard.json")
    assert p.exists(), "dsn_mismatch.guard.json missing"
    data = json.loads(p.read_text())
    assert data.get("ok") in (True, False)  # presence proves guard ran
    assert "env_dsn" in data and "make_dsn" in data


def test_e08_atlas_db_proof_chip():
    """Atlas toggles a DB-proof chip in STRICT; we assert the presence of a chip file for now."""
    chip = pathlib.Path("share/atlas/db_proof_chip.json")
    assert chip.exists(), "db_proof_chip.json not found"


def test_e09_rodsn_guard_in_strict():
    """Re-use RO-DSN guard; in STRICT, it must report strict:true."""
    p = pathlib.Path("share/mcp/rodsn.guard.json")
    assert p.exists(), "rodsn.guard.json missing"
    data = json.loads(p.read_text())
    assert data.get("strict") is True


def test_e10_query_roundtrip_min_postgres():
    """Minimal STRICT roundtrip evidence file exists (placeholder for live DB checkpointer)."""
    p = pathlib.Path("share/mcp/strict_roundtrip.ok.json")
    assert p.exists(), "strict_roundtrip.ok.json missing"
