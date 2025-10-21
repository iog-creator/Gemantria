#!/usr/bin/env python3
import os, json, re, socket
from pathlib import Path
from typing import Dict, Tuple

# Load .env file if it exists
env_path = Path(".env")
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"): continue
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            # Remove quotes if present
            if value and ((value[0]==value[-1]) and value[0] in ['"',"'"]):
                value = value[1:-1]
            os.environ[key] = value

REPORT = {"env": {}, "conflicts": [], "postgres": {}, "lmstudio": {}, "verdict": "fail"}

def read_kv(path: Path) -> Dict[str,str]:
    if not path.exists(): return {}
    data = {}
    for line in path.read_text().splitlines():
        if not line or line.strip().startswith("#"): continue
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)=(.*)$', line.strip())
        if m:
            k,v = m.group(1), m.group(2)
            # strip optional quotes
            if v and ((v[0]==v[-1]) and v[0] in ['"',"'"]): v = v[1:-1]
            data[k]=v
    return data

def compare_env_sources() -> None:
    files = [(".env", Path(".env")), (".env.local", Path(".env.local")), ("env_example.txt", Path("env_example.txt"))]
    sources = {name: read_kv(path) for name, path in files}
    shell = {k:v for k,v in os.environ.items()}
    REPORT["env"]["files"] = {name: list(src.keys()) for name,src in sources.items()}
    REPORT["env"]["shell_subset"] = {k: shell.get(k) for k in [
        "GEMATRIA_DSN","BIBLE_DB_DSN","LM_STUDIO_HOST",
        "USE_QWEN_EMBEDDINGS","QWEN_EMBEDDING_MODEL","QWEN_RERANKER_MODEL",
        "VECTOR_DIM","ENABLE_RELATIONS","ENABLE_RERANK",
        "AI_CONFIDENCE_SOFT","AI_CONFIDENCE_HARD","ALLOW_PARTIAL","EXPORT_DIR","ENFORCE_QWEN_LIVE"
    ]}
    # detect value conflicts between .env and .env.local
    base = sources.get(".env", {})
    local = sources.get(".env.local", {})
    for k,v in local.items():
        if k in base and base[k] != v:
            REPORT["conflicts"].append({"var": k, "env": base[k], "env_local": v, "reason": "env_local overrides .env"})

def check_postgres():
    try:
        import psycopg
        dsn = os.environ.get("GEMATRIA_DSN","")
        if not dsn:
            REPORT["postgres"] = {"ok": False, "reason": "GEMATRIA_DSN not set"}
            return
        with psycopg.connect(dsn, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database(), current_user;")
                db, user = cur.fetchone()
                cur.execute("SHOW unix_socket_directories;")
                sockdirs = cur.fetchone()[0] if cur.description else "n/a"
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                cur.execute("SELECT 1;"); cur.fetchone()
        REPORT["postgres"] = {"ok": True, "db": db, "user": user, "unix_socket_dirs": sockdirs}
    except Exception as e:
        REPORT["postgres"] = {"ok": False, "error": str(e)}

def check_lmstudio():
    import requests, time
    host = os.environ.get("LM_STUDIO_HOST","")
    if not host:
        REPORT["lmstudio"] = {"ok": False, "reason": "LM_STUDIO_HOST not set"}
        return
    try:
        # models endpoint (OpenAI-compatible)
        t0 = time.time()
        r = requests.get(f"{host}/v1/models", timeout=5)
        t1 = time.time()
        if r.status_code != 200:
            REPORT["lmstudio"] = {"ok": False, "status": r.status_code, "reason": "No /v1/models endpoint — upgrade/enable OpenAI API"}
            return
        models = [m.get("id") for m in r.json().get("data",[])]
        need = [
            os.environ.get("QWEN_EMBEDDING_MODEL"),
            os.environ.get("QWEN_RERANKER_MODEL")
        ]
        missing = [m for m in need if m and m not in models]
        REPORT["lmstudio"] = {
            "ok": len(missing)==0,
            "latency_ms": int((t1-t0)*1000),
            "models": models,
            "missing": missing
        }
    except Exception as e:
        REPORT["lmstudio"] = {"ok": False, "error": str(e)}

def verdict():
    ok = REPORT["postgres"].get("ok") and REPORT["lmstudio"].get("ok")
    if REPORT["conflicts"]:
        REPORT["verdict"] = "conflicts"
    elif ok:
        REPORT["verdict"] = "pass"
    else:
        REPORT["verdict"] = "fail"

if __name__ == "__main__":
    compare_env_sources()
    check_postgres()
    check_lmstudio()
    verdict()
    print(json.dumps(REPORT, indent=2))
