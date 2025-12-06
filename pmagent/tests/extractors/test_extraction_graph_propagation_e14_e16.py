import re

import pytest
from datetime import UTC, datetime

from pmagent.graph.assembler import assemble_graph, batch_id_v7, ensure_nodes_have_provenance


UUID_V7_RX = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
BASE = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)


def test_e14_provenance_propagates_into_graph_nodes():
    items = [{"idx": 0}, {"idx": 1}, {"idx": 2}]
    g = assemble_graph(items, "qwen2.5", 7, BASE)
    assert "batch_id" in g and isinstance(g["nodes"], list) and len(g["nodes"]) == len(items)
    for node in g["nodes"]:
        p = node["meta"]["provenance"]
        assert all(k in p for k in ("model", "seed", "ts_iso"))
        assert p["model"] == "qwen2.5" and isinstance(p["seed"], int)


def test_e15_missing_provenance_hard_fails():
    with pytest.raises(ValueError):
        ensure_nodes_have_provenance([{"meta": {}}, {}])  # deliberately missing


def test_e16_batch_uuidv7_deterministic():
    a = batch_id_v7(BASE, 42)
    b = batch_id_v7(BASE, 42)
    c = batch_id_v7(BASE, 43)
    assert a == b and a != c
    assert UUID_V7_RX.match(a)
