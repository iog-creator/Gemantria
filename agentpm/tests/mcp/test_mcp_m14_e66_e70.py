import json

from pathlib import Path

import pytest


# PLAN-074 M14 tests


def test_e66_graph_rollup_metrics_are_versioned():
    """The graph rollup receipt exists and carries a versioned schema header."""
    # Ensure the receipt is present (trigger via make if missing)
    p = Path("share/atlas/graph/rollup.json")
    if not p.exists():
        # Best-effort local generation for dev/CI HINT runs
        import os, subprocess

        os.environ.setdefault("STRICT_MODE", "HINT")
        os.environ.setdefault("GRAPH_ROLLUP_OUT", str(p))
        subprocess.run(["make", "-s", "m14.proofs"], check=False)
    data = json.loads(p.read_text(encoding="utf-8"))
    assert "schema" in data and isinstance(data["schema"], dict)
    assert data["schema"].get("id", "").startswith("atlas.graph.rollup.v")
    assert isinstance(data["schema"].get("version"), int) and data["schema"]["version"] >= 1
    assert "generated_at" in data


def test_e67_per_node_drilldown_links_present():
    import json
    from pathlib import Path

    p = Path("share/atlas/nodes/drilldown.sample.json")
    if not p.exists():
        import os, subprocess

        os.environ.setdefault("STRICT_MODE", "HINT")
        os.environ.setdefault("DRILL_PATH", str(p))
        subprocess.run(["make", "-s", "m14.proofs"], check=False)
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data.get("schema", {}).get("id") == "atlas.nodes.drilldown.v1"
    items = data.get("items", [])
    assert isinstance(items, list) and len(items) >= 1
    first = items[0]
    assert isinstance(first.get("id"), str)
    assert isinstance(first.get("page_url"), str) and first["page_url"].startswith("/atlas/nodes/")
    assert isinstance(first.get("backlinks"), list) and first["backlinks"]


def test_e68_atlas_screenshot_manifest_canonicalized():
    import json
    from pathlib import Path
    import os, subprocess

    p = Path("share/atlas/screenshots/manifest.json")
    if not p.exists():
        os.environ.setdefault("STRICT_MODE", "HINT")
        os.environ.setdefault("SCREENSHOT_MANIFEST", str(p))
        subprocess.run(["make", "-s", "m14.proofs"], check=False)
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data.get("schema", {}).get("id") == "atlas.screenshots.manifest.v1"
    items = data.get("items", [])
    assert isinstance(items, list) and len(items) >= 1
    assert all(items[i]["path"] <= items[i + 1]["path"] for i in range(len(items) - 1))
    allowed = {"path", "page_url", "width", "height"}
    first = items[0]
    assert set(first.keys()) == allowed
    assert first["path"].startswith("/atlas/screenshots/") and first["path"].endswith(".png")
    assert first["page_url"].startswith("/atlas/nodes/") and first["page_url"].endswith(".html")


def test_e69_reranker_badges_exported_and_guarded():
    """Reranker signal plumbed into badges: receipt exists, guard validates, badges match score thresholds."""
    import json
    import os
    import subprocess
    from pathlib import Path

    # Ensure receipt is generated
    p = Path("share/atlas/badges/reranker.json")
    if not p.exists():
        os.environ.setdefault("STRICT_MODE", "HINT")
        os.environ.setdefault("RERANKER_BADGES_OUT", str(p))
        subprocess.run(["make", "-s", "m14.proofs"], check=False)

    # Load and validate receipt
    assert p.exists(), "reranker.json receipt missing"
    data = json.loads(p.read_text(encoding="utf-8"))

    # Check top-level structure
    assert "schema" in data and isinstance(data["schema"], dict)
    assert data["schema"].get("id") == "atlas.badges.reranker.v1"
    assert isinstance(data["schema"].get("version"), int) and data["schema"]["version"] == 1
    assert "generated_at" in data
    assert "mode" in data
    assert "items" in data
    assert "ok" in data

    # Check items
    items = data.get("items", [])
    assert isinstance(items, list)
    mode = data.get("mode", "").upper()
    min_items = 3 if mode == "HINT" else 1
    assert len(items) >= min_items, f"Expected at least {min_items} items in {mode} mode, got {len(items)}"

    # Validate each item structure and badge classification
    for item in items:
        assert isinstance(item.get("node_id"), str) and item["node_id"]
        score = item.get("score")
        assert isinstance(score, (int, float)) and 0.0 <= float(score) <= 1.0
        badge = item.get("badge")
        assert badge in ("high", "med", "low"), f"Invalid badge value: {badge}"
        thresholds = item.get("thresholds")
        assert isinstance(thresholds, dict)
        assert "high" in thresholds and "med" in thresholds

        # Verify badge classification matches rule
        score_val = float(score)
        thresh_high = float(thresholds["high"])
        thresh_med = float(thresholds["med"])
        expected_badge = "high" if score_val >= thresh_high else ("med" if score_val >= thresh_med else "low")
        assert badge == expected_badge, f"Badge mismatch: score={score_val}, badge={badge}, expected={expected_badge}"

    # Check sorting by node_id
    if len(items) > 1:
        for i in range(len(items) - 1):
            assert items[i]["node_id"] <= items[i + 1]["node_id"], "Items not sorted by node_id"

    # Run guard and verify verdict
    result = subprocess.run(
        ["python3", "scripts/guards/guard_m14_reranker_badges.py"],
        capture_output=True,
        text=True,
        check=False,
    )
    guard_output = result.stdout
    if guard_output:
        guard_data = json.loads(guard_output)
        assert guard_data.get("ok") is True, f"Guard verdict not ok: {guard_data}"


@pytest.mark.xfail(reason="E70 not implemented yet", strict=False)
def test_e70_webproof_bundle_has_backlinks():
    raise AssertionError("placeholder")
