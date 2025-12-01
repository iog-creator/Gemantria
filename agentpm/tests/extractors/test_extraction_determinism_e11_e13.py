import copy
import datetime as dt

from agentpm.extractors import provenance


UTC = dt.UTC
BASE = dt.datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)


def test_e11_deterministic_with_injected_clock():
    items = [{"i": 1}, {"i": 2}, {"i": 3}]
    a = provenance.stamp_batch(items, "qwen2.5", 7, base_dt=BASE)
    b = provenance.stamp_batch(copy.deepcopy(items), "qwen2.5", 7, base_dt=BASE)
    assert a == b, "Identical inputs with same seed+base_dt must produce identical outputs"


def test_e12_stable_ordering_is_preserved():
    items = [{"idx": i} for i in range(5)]
    out = provenance.stamp_batch(items, "qwen2.5", 7, base_dt=BASE)
    assert [r["idx"] for r in out] == [
        r["idx"] for r in items
    ], "Output order must match input order"


def test_e13_seed_separation_only_changes_seed_field():
    items = [{"x": "a"}, {"x": "b"}]
    out1 = provenance.stamp_batch(items, "qwen2.5", 1, base_dt=BASE)
    out2 = provenance.stamp_batch(items, "qwen2.5", 2, base_dt=BASE)
    # ts_iso sequences must be equal; seeds differ
    assert [r["ts_iso"] for r in out1] == [r["ts_iso"] for r in out2]
    assert [r["seed"] for r in out1] != [r["seed"] for r in out2]
