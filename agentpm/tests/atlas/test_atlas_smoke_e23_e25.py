import os, json


def _maybe(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def test_e23_atlas_index_exists_or_link_present():
    export_path = _maybe(["share/exports/graph_latest.json", "exports/graph_latest.json"])
    assert export_path is not None, "graph export missing"
    data = json.load(open(export_path, encoding="utf-8"))
    link = ((data.get("meta") or {}).get("links") or {}).get("atlas_index")
    # In staging, it's fine if only the link is present. Implementation will ensure file exists.
    atlas_index = _maybe([link or "", "share/atlas/index.html"])
    assert link or atlas_index, "no atlas index link or file"


def test_e24_node_link_prefix_present():
    export_path = _maybe(["share/exports/graph_latest.json", "exports/graph_latest.json"])
    assert export_path is not None, "graph export missing"
    data = json.load(open(export_path, encoding="utf-8"))
    links = (data.get("meta") or {}).get("links") or {}
    assert "atlas_node_prefix" in links, "missing atlas_node_prefix"


def test_e25_graph_view_link_present():
    export_path = _maybe(["share/exports/graph_latest.json", "exports/graph_latest.json"])
    assert export_path is not None, "graph export missing"
    data = json.load(open(export_path, encoding="utf-8"))
    links = (data.get("meta") or {}).get("links") or {}
    assert "atlas_graph_view" in links, "missing atlas_graph_view"
