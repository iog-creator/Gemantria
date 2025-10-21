from __future__ import annotations
import os, requests, time, json, math
from typing import NamedTuple


class QwenHealth(NamedTuple):
    """Health check result for Qwen models."""
    ok: bool
    reason: str
    embed_dim: int | None
    lat_ms_embed: int | None
    lat_ms_rerank: int | None


class QwenUnavailableError(Exception):
    """Raised when Qwen models are not available and mocks are not allowed."""
    pass


HOST = os.getenv("LM_STUDIO_HOST", "http://127.0.0.1:1234")
TIMEOUT = int(os.getenv("LM_STUDIO_TIMEOUT", "30"))
RETRY_ATTEMPTS = int(os.getenv("LM_STUDIO_RETRY_ATTEMPTS", "3"))
RETRY_DELAY = float(os.getenv("LM_STUDIO_RETRY_DELAY", "2.0"))

def _is_mock_mode() -> bool:
    """Check if mock mode is enabled (checked at runtime)."""
    return os.getenv("LM_STUDIO_MOCK", "false").lower() in ("1","true","yes")

def _get_bool_env(key: str, default: str = "false") -> bool:
    """Get boolean environment variable."""
    return os.getenv(key, default).lower() in ("1", "true", "yes")


def assert_qwen_live(required_models: list[str]) -> QwenHealth:
    """
    Assert that Qwen models are live and functional.

    Performs health checks on LM Studio to ensure embedding and reranker models
    are loaded and responding correctly. This is called before any production
    pipeline work to prevent accidental use of mock embeddings.

    Args:
        required_models: List of model names that must be available

    Returns:
        QwenHealth struct with verification results

    Raises:
        QwenUnavailableError: If models are not available and mocks not allowed
    """
    # Check if Qwen embeddings are required (production mode)
    if not _get_bool_env("USE_QWEN_EMBEDDINGS", "true"):
        raise QwenUnavailableError("USE_QWEN_EMBEDDINGS must be true in production")

    # Check for test-only mock bypass
    allow_mocks = _get_bool_env("ALLOW_MOCKS_FOR_TESTS", "false")
    if allow_mocks:
        return QwenHealth(ok=True, reason="Mock mode allowed for tests", embed_dim=1024, lat_ms_embed=0, lat_ms_rerank=0)

    try:
        # Check available models via LM Studio API
        models_resp = requests.get(f"{HOST}/v1/models", timeout=TIMEOUT)
        models_resp.raise_for_status()
        available_models = {model["id"] for model in models_resp.json().get("data", [])}

        # Verify required models are loaded
        missing_models = [model for model in required_models if model not in available_models]
        if missing_models:
            reason = f"Missing models: {', '.join(missing_models)}. Available: {', '.join(available_models)}"
            return QwenHealth(ok=False, reason=reason, embed_dim=None, lat_ms_embed=None, lat_ms_rerank=None)

        # Dry-run embedding check
        embed_model = QWEN_EMBEDDING_MODEL
        embed_start = time.time()
        embed_resp = requests.post(
            f"{HOST}/v1/embeddings",
            json={"model": embed_model, "input": ["healthcheck"]},
            timeout=TIMEOUT
        )
        embed_resp.raise_for_status()
        embed_data = embed_resp.json()
        embed_dim = len(embed_data["data"][0]["embedding"])
        lat_ms_embed = int((time.time() - embed_start) * 1000)

        # Dry-run reranker check
        rerank_model = QWEN_RERANKER_MODEL
        rerank_start = time.time()
        rerank_resp = requests.post(
            f"{HOST}/v1/chat/completions",
            json={
                "model": rerank_model,
                "messages": [
                    {"role": "system", "content": "Judge whether the Document meets the requirements based on the Query and the Instruct provided. The answer can only be yes or no."},
                    {"role": "user", "content": "Query: health check\nDocument: test"}
                ],
                "max_tokens": 10
            },
            timeout=TIMEOUT
        )
        rerank_resp.raise_for_status()
        lat_ms_rerank = int((time.time() - rerank_start) * 1000)

        return QwenHealth(
            ok=True,
            reason=f"All models verified: {', '.join(required_models)}",
            embed_dim=embed_dim,
            lat_ms_embed=lat_ms_embed,
            lat_ms_rerank=lat_ms_rerank
        )

    except requests.RequestException as e:
        reason = f"LM Studio not available: {str(e)}"
        return QwenHealth(ok=False, reason=reason, embed_dim=None, lat_ms_embed=None, lat_ms_rerank=None)
    except Exception as e:
        reason = f"Health check failed: {str(e)}"
        return QwenHealth(ok=False, reason=reason, embed_dim=None, lat_ms_embed=None, lat_ms_rerank=None)


THEOLOGY_MODEL = os.getenv("THEOLOGY_MODEL", "christian-bible-expert-v2.0-12b")
MATH_MODEL = os.getenv("MATH_MODEL", "self-certainty-qwen3-1.7b-base-math")
QWEN_EMBEDDING_MODEL = os.getenv("QWEN_EMBEDDING_MODEL", "qwen-embed")
QWEN_RERANKER_MODEL = os.getenv("QWEN_RERANKER_MODEL", "qwen-reranker")

class LMStudioClient:
    def __init__(self):
        self.session = requests.Session()

    def _post(self, endpoint: str, payload: dict) -> dict:
        if _is_mock_mode():
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
        if _is_mock_mode() or not _get_bool_env("USE_QWEN_EMBEDDINGS", "true"):
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
                    # Hard fail - no mock fallback in production
                    if _get_bool_env("ALLOW_MOCKS_FOR_TESTS", "false"):
                        # Test-only bypass for unit tests
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
                    else:
                        # Production mode - hard fail
                        raise QwenUnavailableError(f"LM Studio embeddings failed after {RETRY_ATTEMPTS} attempts: {str(e)}")

    def rerank(self, query: str, candidates: list[str], model: str = None) -> list[float]:
        """
        Rerank candidates using Qwen3-Reranker-0.6B-GGUF for theological relevance.

        Uses the specified prompt format for binary relevance classification.
        Supports both yes/no text parsing and logprob extraction for score computation.

        Args:
            query: The theological theme or query string
            candidates: List of candidate document texts to rerank
            model: Model name (defaults to QWEN_RERANKER_MODEL)

        Returns:
            List of relevance scores (0.0 to 1.0) for each candidate
        """
        if _is_mock_mode():
            # Return mock reranking scores for testing
            import random
            random.seed(hash(query) % 10000)
            return [random.uniform(0.1, 0.9) for _ in candidates]

        model = model or QWEN_RERANKER_MODEL
        scores = []

        # Process candidates in smaller batches to keep latency reasonable
        batch_size = min(8, len(candidates))
        for i in range(0, len(candidates), batch_size):
            batch_candidates = candidates[i:i+batch_size]

            for candidate in batch_candidates:
                prompt = f"""Judge whether the Document meets the requirements based on the Query and the Instruct provided. The answer can only be yes or no.

<Instruct>: Given a theological theme, identify relevant biblical nouns.
<Query>: {query}

<Document>: {candidate}"""

                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "Judge whether the Document meets the requirements based on the Query and the Instruct provided. The answer can only be yes or no."},
                        {"role": "user", "content": prompt}
                    ],
                    "logprobs": True,  # Request log probabilities for more precise scoring
                    "top_logprobs": 2
                }

                for attempt in range(RETRY_ATTEMPTS):
                    try:
                        resp = self.session.post(f"{HOST}/v1/chat/completions", json=payload, timeout=TIMEOUT)
                        resp.raise_for_status()
                        data = resp.json()

                        response_text = data["choices"][0]["message"]["content"].strip().lower()
                        logprobs = data["choices"][0].get("logprobs", {})

                        # Try logprob-based scoring first (more precise)
                        score = self._extract_score_from_logprobs(logprobs)

                        # Fallback to text parsing if logprobs not available
                        if score is None:
                            if "yes" in response_text:
                                score = 1.0
                            elif "no" in response_text:
                                score = 0.0
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

    def _extract_score_from_logprobs(self, logprobs: dict) -> float | None:
        """
        Extract relevance score from log probabilities.
        Returns sigmoid of (yes_logprob - no_logprob) to get score in [0,1].
        """
        if not logprobs or "content" not in logprobs:
            return None

        # Look for yes/no tokens in the response
        yes_logprob = None
        no_logprob = None

        for token_info in logprobs["content"]:
            token = token_info.get("token", "").strip().lower()
            logprob = token_info.get("logprob", float('-inf'))

            if "yes" in token:
                yes_logprob = max(yes_logprob or float('-inf'), logprob)
            elif "no" in token:
                no_logprob = max(no_logprob or float('-inf'), logprob)

        # If we have both yes and no logprobs, compute score
        if yes_logprob is not None and no_logprob is not None:
            # Sigmoid of logit difference gives score in [0,1]
            logit_diff = yes_logprob - no_logprob
            return 1 / (1 + math.exp(-logit_diff))  # sigmoid

        return None

def get_lmstudio_client() -> LMStudioClient:
    return LMStudioClient()
