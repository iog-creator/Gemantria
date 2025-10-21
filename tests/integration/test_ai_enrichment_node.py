import os, pytest, psycopg
from src.nodes.enrichment import enrichment_node
@pytest.mark.skipif(not os.getenv("GEMATRIA_DSN"), reason="no DB")
def test_ai_enrichment_inserts(monkeypatch):
    state = {"nouns":[{"name":"Adam","hebrew":"אדם","value":45}]}
    out = enrichment_node(state)
    assert "confidence" in out["nouns"][0]
