"""Test guard_control_compliance_webproof_backlinks guard."""

import json
from pathlib import Path


# Add project root to path
REPO = Path(__file__).resolve().parents[2]


def test_guard_control_compliance_webproof_verdict_structure():
    """Test that guard_control_compliance_webproof_backlinks.json has correct structure."""
    # Run the guard
    from scripts.guards.guard_control_compliance_webproof_backlinks import main as guard_main

    guard_main()

    # Check verdict file exists
    verdict_file = REPO / "evidence" / "guard_control_compliance_webproof_backlinks.json"
    assert verdict_file.exists(), "Guard verdict file should exist"

    # Read and parse JSON
    content = verdict_file.read_text(encoding="utf-8")
    data = json.loads(content)

    # Validate top-level keys
    required_keys = {"ok", "page", "errors", "generated_at"}
    assert required_keys.issubset(
        data.keys()
    ), f"Missing required keys: {required_keys - data.keys()}"

    # Validate page
    assert data["page"] == "control_compliance.html"

    # Validate ok is boolean
    assert isinstance(data["ok"], bool)

    # Validate errors is a list
    assert isinstance(data["errors"], list)

    # Validate generated_at is ISO format
    assert "T" in data["generated_at"] or "Z" in data["generated_at"]

    # Guard should pass if all backlinks are present
    assert data["ok"] is True, "Guard should pass if all required backlinks are present"
    assert len(data["errors"]) == 0, "No errors expected when all backlinks are present"

    # Validate found backlinks if present
    if "found" in data:
        assert isinstance(data["found"], list)
        assert len(data["found"]) == 4  # Four expected backlinks


def test_control_compliance_html_exists():
    """Test that control_compliance.html exists."""
    html_file = REPO / "docs" / "atlas" / "webproof" / "control_compliance.html"
    assert html_file.exists(), "control_compliance.html should exist"


def test_control_compliance_html_has_backlinks():
    """Test that control_compliance.html contains required backlinks."""
    html_file = REPO / "docs" / "atlas" / "webproof" / "control_compliance.html"
    assert html_file.exists(), "control_compliance.html should exist"

    content = html_file.read_text(encoding="utf-8")

    # Check for required data-testid attributes
    required_testids = [
        "backlink-compliance-head-json",
        "backlink-top-violations-7d-json",
        "backlink-top-violations-30d-json",
        "backlink-guard-control-compliance-exports-json",
    ]

    for testid in required_testids:
        assert f'data-testid="{testid}"' in content, f"Missing data-testid: {testid}"
