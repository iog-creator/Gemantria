from src.services.lmstudio_client import LMStudioClient
def test_mock_mode(monkeypatch):
    monkeypatch.setenv("LM_STUDIO_MOCK","1")
    c = LMStudioClient()
    result = c.generate_insight({"name":"Adam","hebrew":"אדם","value":45})
    assert "Sample" in result["text"]
    assert result["tokens"] == 42
