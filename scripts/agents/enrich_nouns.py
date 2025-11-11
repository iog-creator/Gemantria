"""Example instrumented agent: enrich_nouns."""
from __future__ import annotations

from scripts.observability.otel_helpers import span_llm


def enrich_nouns(prompt: str, client, model: str = "qwen2.5"):
    """Enrich nouns with theological context (instrumented example)."""
    prompt_len = len(prompt or "")
    with span_llm(agent="enrich_nouns", model=model, prompt_len=prompt_len):
        resp = client.chat_completion(model=model, messages=[{"role": "user", "content": prompt}])
    return resp


if __name__ == "__main__":
    class DummyClient:
        def chat_completion(self, model, messages):
            return {"ok": True, "model": model, "reply": messages[0]["content"][:80]}

    print(enrich_nouns("test enrich nouns", DummyClient()))
