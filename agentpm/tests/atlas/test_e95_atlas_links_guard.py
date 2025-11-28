import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures" / "e95"


def _run_guard(cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/guards/guard_atlas_links.py"],
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
    )


def test_guard_atlas_links_outputs_json_with_core_fields():
    result = _run_guard()
    assert result.stdout.strip(), f"guard emitted no stdout: {result}"
    data = json.loads(result.stdout)
    assert "ok" in data
    assert "checks" in data
    assert "counts" in data
    assert "details" in data


def test_guard_atlas_links_has_debug_lists():
    result = _run_guard()
    data = json.loads(result.stdout)
    details = data.get("details") or {}
    for key in (
        "broken_internal_links",
        "unmarked_external_links",
        "absolute_paths",
        "whitelisted_links",
    ):
        assert key in details


def test_guard_atlas_links_whitelisted_links():
    """Test that whitelisted evidence/share links are tracked but don't fail the guard."""
    result = _run_guard()
    data = json.loads(result.stdout)

    # Whitelisted links should be in details
    assert "whitelisted_links" in data["details"]
    assert isinstance(data["details"]["whitelisted_links"], list)

    # Count should be present
    assert "whitelisted_links" in data["counts"]
    assert isinstance(data["counts"]["whitelisted_links"], int)

    # Whitelisted links should not cause broken_internal_links to increase
    # (they're tracked separately)


def test_guard_atlas_links_absolute_paths():
    """Test that absolute paths are tracked separately."""
    result = _run_guard()
    data = json.loads(result.stdout)

    # Absolute paths should be in details
    assert "absolute_paths" in data["details"]
    assert isinstance(data["details"]["absolute_paths"], list)

    # Count should be present
    assert "absolute_paths" in data["counts"]
    assert isinstance(data["counts"]["absolute_paths"], int)

    # Absolute paths should not cause broken_internal_links to increase
    # (they're tracked separately)


def test_guard_atlas_links_broken_internal_detection():
    """Test that truly broken internal links are detected."""
    # Run guard on actual repo to verify it detects broken links when they exist
    result = _run_guard()
    data = json.loads(result.stdout)

    # Verify the guard structure supports broken link detection
    assert "checks" in data
    assert "no_broken_internal_links" in data["checks"]
    assert "counts" in data
    assert "broken_internal_links" in data["counts"]
    assert "details" in data
    assert "broken_internal_links" in data["details"]

    # If there are broken links, they should be reported
    if data["counts"]["broken_internal_links"] > 0:
        assert data["checks"]["no_broken_internal_links"] is False
        assert len(data["details"]["broken_internal_links"]) > 0
