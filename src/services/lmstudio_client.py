from __future__ import annotations
import os, requests, time, json

HOST = os.getenv("LM_STUDIO_HOST", "http://127.0.0.1:1234")
TIMEOUT = int(os.getenv("LM_STUDIO_TIMEOUT", "30"))
RETRY_ATTEMPTS = int(os.getenv("LM_STUDIO_RETRY_ATTEMPTS", "3"))
RETRY_DELAY = float(os.getenv("LM_STUDIO_RETRY_DELAY", "2.0"))
MOCK = os.getenv("LM_STUDIO_MOCK", "false").lower() in ("1","true","yes")

def _get_bool_env(key: str, default: str = "false") -> bool:
    """Get boolean environment variable."""
    return os.getenv(key, default).lower() in ("1", "true", "yes")

THEOLOGY_MODEL = os.getenv("THEOLOGY_MODEL", "christian-bible-expert-v2.0-12b")
MATH_MODEL = os.getenv("MATH_MODEL", "self-certainty-qwen3-1.7b-base-math")
QWEN_EMBEDDING_MODEL = os.getenv("QWEN_EMBEDDING_MODEL", "qwen-embed")
QWEN_RERANKER_MODEL = os.getenv("QWEN_RERANKER_MODEL", "qwen-reranker")

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
        """Generate single embedding for text (legacy method)."""
        return self.get_embeddings([text], model)[0]

    def get_embeddings(self, texts: list[str], model: str = None) -> list[list[float]]:
        """
        Generate embeddings for multiple texts using Qwen3-Embedding-0.6B-GGUF.

        Args:
            texts: List of text strings to embed
            model: Model name (defaults to QWEN_EMBEDDING_MODEL)

        Returns:
            List of normalized 1024-dimensional vectors
        """
        if MOCK or not _get_bool_env("USE_QWEN_EMBEDDINGS", "true"):
            # Return mock embeddings for testing or when disabled
            import random
            result = []
            for text in texts:
                random.seed(hash(text) % 10000)  # Deterministic for testing
                embedding = [random.uniform(-1, 1) for _ in range(1024)]
                # L2 normalize
                norm = sum(x*x for x in embedding) ** 0.5
                normalized = [x/norm for x in embedding]
                result.append(normalized)
            return result

        model = model or QWEN_EMBEDDING_MODEL
        payload = {"model": model, "input": texts}
        url = f"{HOST}/v1/embeddings"

        for attempt in range(RETRY_ATTEMPTS):
            try:
                resp = self.session.post(url, json=payload, timeout=TIMEOUT)
                resp.raise_for_status()
                data = resp.json()

                embeddings = []
                for item in data["data"]:
                    embedding = item["embedding"]
                    # L2 normalize the embedding
                    norm = sum(x*x for x in embedding) ** 0.5
                    if norm > 0:
                        normalized = [x/norm for x in embedding]
                    else:
                        normalized = embedding  # Fallback for zero vector
                    embeddings.append(normalized)

                return embeddings
            except Exception as e:
                if attempt < RETRY_ATTEMPTS - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    raise e

    def rerank(self, query: str, candidates: list[str], model: str = None) -> list[float]:
        """
        Rerank candidates using Qwen3-Reranker-0.6B-GGUF for relevance to query.

        Args:
            query: The theological theme or query string
            candidates: List of candidate texts to rerank
            model: Model name (defaults to QWEN_RERANKER_MODEL)

        Returns:
            List of relevance scores (0.0 to 1.0) for each candidate
        """
        if MOCK:
            # Return mock reranking scores for testing
            import random
            random.seed(hash(query) % 10000)
            return [random.uniform(0.1, 0.9) for _ in candidates]

        model = model or QWEN_RERANKER_MODEL
        scores = []

        for candidate in candidates:
            prompt = f"""<Instruct>: Given a theological theme, identify relevant biblical nouns.

<Query>: {query}

<Document>: {candidate}

Respond with only "yes" or "no" indicating if this document is relevant to the query."""

            payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}

            for attempt in range(RETRY_ATTEMPTS):
                try:
                    resp = self.session.post(f"{HOST}/v1/chat/completions", json=payload, timeout=TIMEOUT)
                    resp.raise_for_status()
                    data = resp.json()

                    response_text = data["choices"][0]["message"]["content"].strip().lower()

                    # Parse response: "yes" = 0.8-1.0, "no" = 0.0-0.2
                    if "yes" in response_text:
                        score = 0.9  # High confidence for relevant
                    elif "no" in response_text:
                        score = 0.1  # Low confidence for irrelevant
                    else:
                        score = 0.5  # Neutral for unclear responses

                    scores.append(score)
                    break

                except Exception as e:
                    if attempt < RETRY_ATTEMPTS - 1:
                        time.sleep(RETRY_DELAY)
                    else:
                        # Fallback score on failure
                        scores.append(0.5)
                        break

        return scores

def get_lmstudio_client() -> LMStudioClient:
    return LMStudioClient()
