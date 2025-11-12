import pytest


pytestmark = pytest.mark.xfail(
    strict=False, reason="M2+ rollups/audit/correlation TVs (E17-E19) pending implementation"
)


def test_e17_graph_level_provenance_rollup_exists():
    # expect: graph.meta.provenance_rollup with unique models/seeds and min/max ts_iso
    raise AssertionError("Implement graph rollup and expose graph.meta.provenance_rollup")


def test_e18_per_node_audit_trail_fields_present():
    # expect: each node.meta.audit contains batch_id and provenance_hash
    raise AssertionError("Implement per-node audit trail with batch_id + provenance_hash")


def test_e19_cross_batch_correlation_helper():
    # expect: correlate_nodes_across_batches([{graph, key_field}], returns mapping key->[batch_ids...])
    raise AssertionError("Implement cross-batch correlation helper (stable-key mapping)")
