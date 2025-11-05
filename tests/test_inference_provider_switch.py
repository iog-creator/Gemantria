import os

from src.services.inference_client import InferenceClient


def test_vllm_base_url(monkeypatch):
    monkeypatch.setenv("INFERENCE_PROVIDER", "vllm")
    monkeypatch.delenv("VLLM_BASE_URL", raising=False)
    c = InferenceClient()
    assert c.base_url.endswith(":8001/v1")


def test_lmstudio_base_url(monkeypatch):
    monkeypatch.setenv("INFERENCE_PROVIDER", "lmstudio")
    monkeypatch.setenv("OPENAI_BASE_URL", "http://127.0.0.1:1234/v1")
    c = InferenceClient()
    assert c.base_url.endswith(":1234/v1")
