import os
import sys

import requests

base = os.getenv("EMBED_URL", "http://127.0.0.1:9994/v1")
model = os.getenv("EMBEDDING_MODEL", "text-embedding-bge-m3")
try:
    # liveness
    r = requests.get(f"{base}/models", timeout=5)
    r.raise_for_status()
    ids = [m["id"] for m in r.json().get("data", [])]
    if model not in ids:
        print(f"[FAIL] embeddings server active but '{model}' not loaded. Have: {ids}")
        sys.exit(2)
    # real embedding call
    payload = {"model": model, "input": ["in the beginning", "ἐν ἀρχῇ", "בְּרֵאשִׁית"]}
    r = requests.post(f"{base}/embeddings", json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()["data"]
    dims = len(data[0]["embedding"])
    assert dims in (768, 1024, 1536, 3072), f"Unexpected dim {dims}"
    print(f"[OK] embeddings live: model={model}, dim={dims}, batch={len(data)}")
except Exception as e:
    print(f"[FAIL] embeddings smoke: {e}")
    sys.exit(1)
