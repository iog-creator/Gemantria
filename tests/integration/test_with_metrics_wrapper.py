from src.graph.graph import with_metrics


def dummy(state):
    state["items"] = [1, 2, 3]
    return state


def test_wrapper_propagates_state_and_counts():
    wrapped = with_metrics(dummy, "dummy")
    state = {"items": [1, 2]}
    out = wrapped(state)
    assert "run_id" in out and "thread_id" in out
    assert out["items"] == [1, 2, 3]
