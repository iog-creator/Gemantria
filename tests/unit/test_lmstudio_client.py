import pytest

from src.services.lmstudio_client import (
    LMStudioClient,
    chat_completion,
    safe_json_parse,
)


def test_mock_mode(monkeypatch):
    monkeypatch.setenv("LM_STUDIO_MOCK", "1")
    c = LMStudioClient()
    result = c.generate_insight({"name": "Adam", "hebrew": "אדם", "value": 45})
    assert "Sample" in result["text"]
    assert result["tokens"] == 42


def test_chat_completion_mock_mode(monkeypatch):
    """Test chat_completion returns mock responses in mock mode."""
    monkeypatch.setenv("LM_STUDIO_MOCK", "1")
    messages_batch = [[{"role": "user", "content": "test"}]]
    results = chat_completion(messages_batch, model="test-model")
    assert len(results) == 1
    assert results[0].text == '{"insight": "Mock theological insight", "confidence": 0.95}'


def test_safe_json_parse_valid():
    """Test parsing valid JSON."""
    text = '{"insight": "Test insight", "confidence": 0.85}'
    result = safe_json_parse(text, required_keys=["insight", "confidence"])
    assert result["insight"] == "Test insight"
    assert result["confidence"] == 0.85


def test_safe_json_parse_with_markdown():
    """Test parsing JSON wrapped in markdown code fences."""
    text = '```json\n{"insight": "Test insight", "confidence": 0.85}\n```'
    result = safe_json_parse(text, required_keys=["insight", "confidence"])
    assert result["insight"] == "Test insight"
    assert result["confidence"] == 0.85


def test_safe_json_parse_missing_keys():
    """Test that missing required keys raise ValueError."""
    text = '{"insight": "Test insight"}'
    with pytest.raises(ValueError, match="missing required keys: \\['confidence'\\]"):
        safe_json_parse(text, required_keys=["insight", "confidence"])


def test_safe_json_parse_invalid_json():
    """Test that invalid JSON raises ValueError."""
    text = '{"insight": "Test insight", invalid}'
    with pytest.raises(ValueError, match="Failed to parse JSON"):
        safe_json_parse(text, required_keys=["insight"])
