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


@pytest.mark.xfail(reason="E68 not implemented yet", strict=False)
def test_e68_atlas_screenshot_manifest_canonicalized():
    raise AssertionError("placeholder")


@pytest.mark.xfail(reason="E69 not implemented yet", strict=False)
def test_e69_reranker_signal_plumbed_into_badges():
    raise AssertionError("placeholder")


@pytest.mark.xfail(reason="E70 not implemented yet", strict=False)
def test_e70_webproof_bundle_has_backlinks():
    raise AssertionError("placeholder")
