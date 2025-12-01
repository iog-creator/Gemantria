import os
import json


def _maybe(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def test_e35_node_page_has_view_raw_json_link():
    node_html = _maybe(["share/atlas/nodes/0.html", "share/atlas/nodes/1.html"])
    assert node_html is not None, "node page missing (staged)"
    html = _read(node_html)
    assert ('id="view-json-raw"' in html) or (
        "View raw JSON" in html
    ), "view-raw link not present (staged)"


def test_e36_jumpers_backfill_proof_present():
    jp = _maybe(["share/atlas/jumpers/index.html"])
    assert jp is not None, "jumpers index missing (staged)"
    txt = _read(jp)
    # Expect at least a placeholder marker to prove backlinks were back-filled in impl
    assert ("data-backfill-proof" in txt) or ("Backfill proof" in txt)


def test_e37_sitemap_integrity():
    sp = _maybe(["share/atlas/sitemap.json"])
    assert sp is not None, "sitemap missing (staged)"
    data = json.load(open(sp, encoding="utf-8"))
    assert "nodes_count" in data and "jumpers_count" in data
