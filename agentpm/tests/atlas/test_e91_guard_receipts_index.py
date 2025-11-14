import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[3]


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    """Run command in repo root."""
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


def test_guard_receipts_index_html_exists():
    """Test that guard_receipts.html exists after generator runs."""
    html_path = ROOT / "docs" / "atlas" / "browser" / "guard_receipts.html"
    assert html_path.exists(), "guard_receipts.html should exist after generator runs"


def test_guard_receipts_guard_ok_field_present():
    """Test that guard script produces valid JSON with ok + checks fields."""
    result = _run([sys.executable, "scripts/guards/guard_atlas_guard_receipts.py"])
    assert result.stdout.strip(), "guard script produced no output"

    verdict = json.loads(result.stdout.strip())
    assert "ok" in verdict, "verdict must have 'ok' field"
    assert "checks" in verdict, "verdict must have 'checks' field"
    assert isinstance(verdict["ok"], bool), "ok must be boolean"
    assert isinstance(verdict["checks"], dict), "checks must be dict"


def test_guard_receipts_html_has_required_backlinks():
    """Test that HTML has required backlinks."""
    html_path = ROOT / "docs" / "atlas" / "browser" / "guard_receipts.html"
    if not html_path.exists():
        pytest.skip("HTML file does not exist")

    content = html_path.read_text()

    required_backlinks = [
        "backlink-compliance-summary",
        "backlink-compliance-timeseries",
        "backlink-violations-browser",
        "backlink-evidence-dir",
    ]

    for backlink in required_backlinks:
        assert f'data-testid="{backlink}"' in content, f"Missing backlink: {backlink}"


def test_guard_receipts_html_has_e91_badge():
    """Test that HTML has E91 badge."""
    html_path = ROOT / "docs" / "atlas" / "browser" / "guard_receipts.html"
    if not html_path.exists():
        pytest.skip("HTML file does not exist")

    content = html_path.read_text()
    assert 'class="badge">E91' in content or 'badge">E91' in content, "Missing E91 badge"


def test_guard_receipts_generator_script_exists():
    """Test that generator script exists."""
    script_path = ROOT / "scripts" / "atlas" / "generate_guard_receipts_index.py"
    assert script_path.exists(), "Generator script must exist"


def test_guard_receipts_guard_script_exists():
    """Test that guard script exists."""
    script_path = ROOT / "scripts" / "guards" / "guard_atlas_guard_receipts.py"
    assert script_path.exists(), "Guard script must exist"
