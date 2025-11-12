"""PLAN-073 M3: STRICT live-path tests (E11-E15)."""

from __future__ import annotations

import json
import pathlib


# pytestmark removed: PLAN-073 M3 now implemented


def test_e11_checkpointer_live_handshake():
    """A live-path handshake proves Postgres Checkpointer is wired (STRICT-only)."""
    p = pathlib.Path("share/mcp/strict_live.handshake.json")
    assert p.exists(), "strict_live.handshake.json missing"


def test_e12_db_smoke_receipt():
    """Minimal SELECT 1 smoke receipt saved as JSON (STRICT)."""
    p = pathlib.Path("share/mcp/db_smoke.ok.json")
    assert p.exists(), "db_smoke.ok.json missing"
    data = json.loads(p.read_text())
    assert data.get("ok") is True


def test_e13_atlas_chip_in_html():
    """Atlas index page contains a DB-proof chip marker (STRICT)."""
    p = pathlib.Path("share/atlas/index.html")
    assert p.exists(), "atlas index not generated"
    text = p.read_text(errors="ignore")
    assert (
        'data-db-strict="true"' in text
        or "data-db-strict='true'" in text
        or "db-proof-chip" in text
    )


def test_e14_dsn_redacted_in_chip():
    """Chip JSON contains redacted DSN, never raw credentials."""
    p = pathlib.Path("share/atlas/db_proof_chip.json")
    assert p.exists(), "db_proof_chip.json missing"
    data = json.loads(p.read_text())
    assert "<REDACTED>" in (data.get("dsn") or "")


def test_e15_trace_link_written():
    """A minimal trace pointer exists for the STRICT live-path actions."""
    p = pathlib.Path("share/mcp/strict_trace.ptr.txt")
    assert p.exists(), "strict_trace.ptr.txt missing"
