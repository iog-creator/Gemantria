# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import json
import os
import time
import urllib.request

from src.infra.env_loader import ensure_env_loaded

ensure_env_loaded()


def get(url, data=None, headers=None, timeout=30):
    req = urllib.request.Request(
        url, data=data, headers=headers or {}, method="POST" if data else "GET"
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8")


EMBED_URL = os.getenv("EMBED_URL", "http://127.0.0.1:9994/v1")
LLM_ANS = os.getenv("LM_STUDIO_HOST", "http://127.0.0.1:9991")
LLM_CRIT = "http://127.0.0.1:9993"


def list_models(host, retries: int = 5):
    last_err = None
    for _ in range(retries):
        try:
            txt = get(f"{host}/v1/models")
            data = json.loads(txt)
            return True, data
        except Exception as e:
            last_err = e
            time.sleep(0.5)
    return False, str(last_err) if last_err else "unknown error"


def chat_ping(host, model, retries: int = 3):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Reply with exactly the string OK"}],
        "temperature": 0.0,
        "max_tokens": 3,
    }
    t0 = time.time()
    for _ in range(retries):
        try:
            txt = get(
                f"{host}/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            dt = time.time() - t0
            obj = json.loads(txt)
            out = obj.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return True, {"latency_s": round(dt, 3), "output": out}
        except Exception as e:
            err = e
            time.sleep(0.5)
    return False, str(err)


def embed_ping():
    payload = {
        "input": ["hello world"],
        "model": os.getenv("EMBEDDING_MODEL", "text-embedding-bge-m3"),
    }
    # primary: /v1/embeddings
    try:
        txt = get(
            f"{EMBED_URL}/embeddings",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        obj = json.loads(txt)
        vec = obj["data"][0]["embedding"]
        return len(vec)
    except Exception:
        # fallback: strip trailing /v1 if present and try /embeddings
        base = EMBED_URL.rstrip("/")
        if base.endswith("/v1"):
            base = base[:-3]
        try:
            txt = get(
                f"{base}/v1/embeddings",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            obj = json.loads(txt)
            vec = obj["data"][0]["embedding"]
            return len(vec)
        except Exception as e2:
            raise e2


ok_ans, ans_models = list_models(LLM_ANS)
ok_crit, crit_models = list_models(LLM_CRIT)
res = {
    "answerer_list_ok": ok_ans,
    "answerer_models": ans_models,
    "critic_list_ok": ok_crit,
    "critic_models": crit_models,
}
print("[verify] /models:", json.dumps(res, ensure_ascii=False))

# choose model names
ANS_NAME = os.getenv("ANSWERER_MODEL_PRIMARY", "christian-bible-expert-v2.0-12b")
if os.getenv("ANSWERER_USE_ALT", "0") == "1":
    ANS_NAME = os.getenv("ANSWERER_MODEL_ALT", "Qwen2.5-14B-Instruct-GGUF")
CRIT_NAME = "skywork-critic-llama-3.1-8b"

ok_chat1, info1 = chat_ping(LLM_ANS, ANS_NAME)
ok_chat2, info2 = chat_ping(LLM_CRIT, CRIT_NAME)
print("[verify] chat/answerer:", ok_chat1, info1)
print("[verify] chat/critic:", ok_chat2, info2)

try:
    dim = embed_ping()
    print(f"[verify] embeddings dim={dim} (expect 1024)")
except Exception as e:
    print(f"[verify] embeddings FAILED: {e}")
    dim = -1

ok = ok_chat1 and isinstance(info1, dict) and info1.get("output") == "OK" and dim == 1024
print("[verify] OK" if ok else "[verify] FAIL")
