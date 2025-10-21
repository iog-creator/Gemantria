from src.graph.nodes import GraphNode


def test_graph_node_executes_handler() -> None:
    calls: list[int] = []

    def handler(value: int) -> int:
        calls.append(value)
        return value * 2

    node = GraphNode(name="doubler", handler=handler)
    result = node.execute(3)

    assert result == 6
    assert calls == [3]
