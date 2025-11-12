from datetime import UTC, datetime

from agentpm.graph.assembler import assemble_graph, correlate_nodes_across_batches


BASE = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)


def test_e17_graph_level_provenance_rollup_exists():
    g = assemble_graph([{"idx": 0}, {"idx": 1}], "qwen2.5", 7, BASE)
    r = g["meta"]["provenance_rollup"]
    assert r["models"] == ["qwen2.5"]
    assert r["seeds"] == [7]
    assert r["ts_min"] <= r["ts_max"]
    assert isinstance(r["ts_min"], str) and r["ts_min"].endswith("Z")


def test_e18_per_node_audit_trail_fields_present():
    g = assemble_graph([{"idx": 0}, {"idx": 1}, {"idx": 2}], "qwen2.5", 7, BASE)
    for n in g["nodes"]:
        audit = n["meta"]["audit"]
        assert audit["batch_id"] == g["batch_id"]
        # provenance hash is 64 hex chars
        h = audit["provenance_hash"]
        assert isinstance(h, str) and len(h) == 64 and all(c in "0123456789abcdef" for c in h)
    # hash changes if provenance changes (model differs)
    g2 = assemble_graph([{"idx": 0}], "other-model", 7, BASE)
    assert g2["nodes"][0]["meta"]["audit"]["provenance_hash"] != g["nodes"][0]["meta"]["audit"]["provenance_hash"]


def test_e19_cross_batch_correlation_helper():
    g1 = assemble_graph([{"idx": 0}, {"idx": 1}], "qwen2.5", 7, BASE)
    g2 = assemble_graph([{"idx": 1}, {"idx": 2}], "qwen2.5", 8, BASE)
    m = correlate_nodes_across_batches([g1, g2], key_field="idx")
    assert m[0] == [g1["batch_id"]]
    assert m[1] == [g1["batch_id"], g2["batch_id"]]
    assert m[2] == [g2["batch_id"]]
