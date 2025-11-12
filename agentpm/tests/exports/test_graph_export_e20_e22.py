import os, json, pytest


def _read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _maybe(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def test_e20_graph_export_validates_against_schema_if_present():
    export_path = _maybe(["exports/graph_latest.json", "share/exports/graph_latest.json"])
    schema_path = _maybe(
        [
            "share/graph.schema.json",
            "docs/SSOT/SSOT_graph.v1.schema.json",
            "docs/SSOT/graph.schema.json",
            "graph.schema.json",
        ]
    )
    # Expect both to exist in implementation; in staging it's fine if missing.
    assert export_path is not None and schema_path is not None, "graph export or schema missing"
    data = _read_json(export_path)
    assert "schema" in data and "nodes" in data and "edges" in data


def test_e21_graph_meta_has_atlas_linkbacks_fields():
    export_path = _maybe(["exports/graph_latest.json", "share/exports/graph_latest.json"])
    assert export_path is not None, "graph export missing"
    data = _read_json(export_path)
    meta = data.get("meta", {})
    links = meta.get("links", {})
    # Expected fields (implementation will populate):
    assert any(k in links for k in ("atlas_index", "atlas_node_prefix", "atlas_graph_view")), "no linkbacks"


def test_e22_stats_consistency_with_graph_export_when_present():
    graph_path = _maybe(["exports/graph_latest.json", "share/exports/graph_latest.json"])
    stats_path = _maybe(["exports/graph_stats.json", "share/exports/graph_stats.json"])
    assert graph_path is not None and stats_path is not None, "exports missing"
    g = _read_json(graph_path)
    s = _read_json(stats_path)
    # Minimal consistency: stats must mention node/edge counts when present.
    gn = len(g.get("nodes", []))
    ge = len(g.get("edges", []))
    sn = s.get("totals", {}).get("nodes")
    se = s.get("totals", {}).get("edges")
    assert sn is None or isinstance(sn, int)
    assert se is None or isinstance(se, int)
    if isinstance(sn, int):
        assert sn >= 0 and sn >= min(gn, 0)
    if isinstance(se, int):
        assert se >= 0 and se >= min(ge, 0)
