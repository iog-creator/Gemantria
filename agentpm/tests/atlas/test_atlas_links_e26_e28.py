import os, json, pytest, re

xfail_reason = "Staged TV: node deep-links + per-node audit view + breadcrumb pending implementation"
pytestmark = pytest.mark.xfail(reason=xfail_reason, strict=False)

def _maybe(paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None

def _read_json(path):
    import json
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_e26_export_has_valid_node_link_prefix():
    export_path = _maybe(["share/exports/graph_latest.json", "exports/graph_latest.json"])
    assert export_path, "graph export missing (staged)"
    data = _read_json(export_path)
    links = (data.get("meta") or {}).get("links") or {}
    assert "atlas_node_prefix" in links, "missing atlas_node_prefix (staged)"
    # Implementation will ensure node pages exist and are addressable as f"{prefix}{id}.html"

def test_e27_per_node_audit_view_or_anchor_present_when_page_exists():
    node0 = _maybe(["share/atlas/nodes/0.html"])
    if not node0:
        pytest.skip("node pages not generated yet (staged)")
    html = open(node0, "r", encoding="utf-8").read()
    assert ("id=\"audit\"" in html) or ("Audit" in html), "no audit section/anchor (staged)"

def test_e28_node_pages_have_breadcrumb_to_index():
    node0 = _maybe(["share/atlas/nodes/0.html"])
    if not node0:
        pytest.skip("node pages not generated yet (staged)")
    html = open(node0, "r", encoding="utf-8").read()
    assert re.search(r'href="..\/index\.html"', html) or ("Back to Atlas" in html), "no breadcrumb/backlink (staged)"
