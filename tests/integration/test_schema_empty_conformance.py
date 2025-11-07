import json
import pathlib


def _j(p):
    assert pathlib.Path(p).exists(), f"missing {p}"
    return json.loads(open(p, encoding="utf-8").read())


def test_ai_nouns_has_required_fields():
    d = _j("share/exports/ai_nouns.json")
    for k in ("schema", "book", "generated_at", "nodes"):
        assert k in d


def test_graph_has_required_fields():
    d = _j("share/exports/graph_latest.json")
    for k in ("schema", "book", "generated_at", "nodes", "edges"):
        assert k in d


def test_temporal_patterns_conforms_shape():
    d = _j("share/exports/temporal_patterns.json")
    assert "patterns" in d and "metadata" in d
