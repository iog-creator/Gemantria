"""Unit tests for reality-check live status banner."""

from agentpm.reality import check as rc


def _mk_verdict(mode: str, db_ok: bool, lm_ok: bool) -> dict:
    """Create a minimal verdict dict for testing."""
    return {
        "mode": mode,
        "db": {"ok": db_ok},
        "lm": {"ok": lm_ok},
    }


def test_summarize_live_status_hint_not_ready() -> None:
    """Test banner in HINT mode when services are not ready."""
    verdict = _mk_verdict(mode="hint", db_ok=False, lm_ok=False)
    banner = rc.summarize_live_status(verdict)
    assert "LIVE STATUS: NOT READY" in banner
    assert "MODE=HINT" in banner
    assert "DB=OFF" in banner
    assert "LM=OFF" in banner
    assert "CI/dev-only" in banner  # Hint-mode warning


def test_summarize_live_status_strict_ready() -> None:
    """Test banner in STRICT mode when services are ready."""
    verdict = _mk_verdict(mode="strict", db_ok=True, lm_ok=True)
    banner = rc.summarize_live_status(verdict)
    assert "LIVE STATUS: READY" in banner
    assert "MODE=STRICT" in banner
    assert "DB=OK" in banner
    assert "LM=OK" in banner
    assert "CI/dev-only" not in banner  # No hint warning in STRICT mode


def test_summarize_live_status_hint_partial() -> None:
    """Test banner in HINT mode when only DB is ready."""
    verdict = _mk_verdict(mode="hint", db_ok=True, lm_ok=False)
    banner = rc.summarize_live_status(verdict)
    assert "LIVE STATUS: NOT READY" in banner
    assert "MODE=HINT" in banner
    assert "DB=OK" in banner
    assert "LM=OFF" in banner
    assert "CI/dev-only" in banner


def test_summarize_live_status_strict_not_ready() -> None:
    """Test banner in STRICT mode when services are not ready."""
    verdict = _mk_verdict(mode="strict", db_ok=False, lm_ok=True)
    banner = rc.summarize_live_status(verdict)
    assert "LIVE STATUS: NOT READY" in banner
    assert "MODE=STRICT" in banner
    assert "DB=OFF" in banner
    assert "LM=OK" in banner
    assert "CI/dev-only" not in banner
