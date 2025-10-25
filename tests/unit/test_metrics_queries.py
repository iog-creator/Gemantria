import pytest

from src.infra.metrics_queries import node_latency_7d


def test_queries_fail_without_dsn(monkeypatch):
    monkeypatch.delenv("GEMATRIA_DSN", raising=False)
    with pytest.raises(RuntimeError):
        node_latency_7d()
