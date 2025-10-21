from __future__ import annotations
import os, requests, time, json

HOST = os.getenv("LM_STUDIO_HOST", "http://127.0.0.1:1234")
TIMEOUT = int(os.getenv("LM_STUDIO_TIMEOUT", "30"))
RETRY_ATTEMPTS = int(os.getenv("LM_STUDIO_RETRY_ATTEMPTS", "3"))
RETRY_DELAY = float(os.getenv("LM_STUDIO_RETRY_DELAY", "2.0"))
MOCK = os.getenv("LM_STUDIO_MOCK", "false").lower() in ("1","true","yes")

THEOLOGY_MODEL = os.getenv("THEOLOGY_MODEL", "christian-bible-expert-v2.0-12b")
MATH_MODEL = os.getenv("MATH_MODEL", "self-certainty-qwen3-1.7b-base-math")

class LMStudioClient:
    def __init__(self):
        self.session = requests.Session()

    def _post(self, endpoint: str, payload: dict) -> dict:
        if MOCK:
            # Check if this is a confidence check request (different model)
            if payload.get("model") == MATH_MODEL:
                return {"choices": [{"message": {"content": "0.95"}}], "usage": {"total_tokens": 10}}
            else:
                return {"choices": [{"message": {"content": "Sample insight"}}], "usage": {"total_tokens": 42}}
        url = f"{HOST}/v1/chat/completions"
        for attempt in range(RETRY_ATTEMPTS):
            try:
                resp = self.session.post(url, json=payload, timeout=TIMEOUT)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                if attempt < RETRY_ATTEMPTS - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    raise e

    def generate_insight(self, noun: dict) -> dict:
        prompt = f"Provide theological insight (150-250 words) for {noun['hebrew']} ({noun['name']})."
        payload = {"model": THEOLOGY_MODEL, "messages": [{"role": "user","content": prompt}]}
        res = self._post("v1/chat/completions", payload)
        content = res.get("choices", [{}])[0].get("message", {}).get("content","")
        return {"text": content, "tokens": res.get("usage",{}).get("total_tokens",0)}

    def confidence_check(self, noun: dict, expected_value: int) -> float:
        prompt = f"Rate the confidence (0.0 to 1.0) that the gematria value {noun['value']} for '{noun['name']}' is correct. Expected was {expected_value}. Return only a number between 0.0 and 1.0."
        payload = {"model": MATH_MODEL, "messages": [{"role": "user","content": prompt}]}
        res = self._post("v1/chat/completions", payload)
        content = res.get("choices", [{}])[0].get("message", {}).get("content","0.95").strip()
        # Extract just the numeric part if the model returns extra text
        import re
        match = re.search(r'([0-9]*\.?[0-9]+)', content)
        if match:
            score = float(match.group(1))
        else:
            score = 0.95  # fallback
        return max(0.0, min(1.0, score))

    def generate_embedding(self, text: str, model: str = None) -> list[float]:
        """Generate embeddings for text using LM Studio embeddings endpoint."""
        if MOCK:
            # Return a mock 1024-dimensional embedding
            import random
            random.seed(hash(text) % 10000)  # Deterministic for testing
            return [random.uniform(-1, 1) for _ in range(1024)]

        model = model or THEOLOGY_MODEL  # Default to theology model for embeddings
        payload = {"model": model, "input": text}
        url = f"{HOST}/v1/embeddings"

        for attempt in range(RETRY_ATTEMPTS):
            try:
                resp = self.session.post(url, json=payload, timeout=TIMEOUT)
                resp.raise_for_status()
                data = resp.json()
                return data["data"][0]["embedding"]
            except Exception as e:
                if attempt < RETRY_ATTEMPTS - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    raise e

def get_lmstudio_client() -> LMStudioClient:
    return LMStudioClient()
