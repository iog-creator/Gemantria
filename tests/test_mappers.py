from scripts.ingest.mappers import (
    normalize_label,
    normalize_type,
    normalize_verse_ref,
    clamp_weight,
    map_node,
    map_edge,
)


def test_normalize_label_truncates_and_collapses_spaces():
    s = "  a" + "x" * 130 + "   b "
    out = normalize_label(s)
    assert "  " not in out
    assert len(out) == 120


def test_normalize_type_truncates():
    s = "t" * 100
    assert len(normalize_type(s)) == 40


def test_clamp_weight_bounds_and_parse():
    assert clamp_weight(-1) == 0.0
    assert clamp_weight(2.5) == 1.0
    assert clamp_weight("0.7") == 0.7
    assert clamp_weight("bad") == 0.0


def test_map_node_minimal_fields():
    raw = {"id": " n1 ", "label": "  hello   world  ", "type": " example "}
    node = map_node(raw)
    assert node["id"] == "n1"
    assert node["label"] == "hello world"
    assert node["type"] == "example"


def test_map_edge_weight_and_reltype():
    raw = {"src": "a", "dst": "b", "rel_type": "  CONNECTS  ", "weight": 9}
    e = map_edge(raw)
    assert e["rel_type"] == "CONNECTS"[:40]
    assert e["weight"] == 1.0


def test_normalize_verse_ref_format():
    assert normalize_verse_ref("Genesis", 1, 1) == "Genesis 1:1"
